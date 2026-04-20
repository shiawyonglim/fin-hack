"""
=============================================================================
 FRAUD DETECTION ENGINE - ONNX Runtime + Deterministic Rule Engine
=============================================================================
 This module is the full fraud detection system described in about.md.
 It combines:
   1. ONNX Neural Network   — ML-based anomaly scoring
   2. Deterministic Rules    — White-box rule engine with plain-text logs
   3. User Self-Evaluation   — Categorise users (elderly, child, adult, etc.)
   4. Scammer Database       — SC Investor Alert List / BNM FCA lookup
   5. Time-based Anomaly     — e.g. elderly transferring at 2 AM
   6. Offline / Online mode  — Zero-Trust Edge policy

 The engine is designed to run ENTIRELY on-device via ONNX Runtime (or
 ONNX Runtime Web via WebAssembly). No cloud dependency.
=============================================================================
"""

import onnxruntime as ort
import numpy as np
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCAMMER_CSV = os.path.join(BASE_DIR, "../data/investor_alert_list.csv")
DEFAULT_ONNX_MODEL = os.path.join(BASE_DIR, "../models/fraud_detection_model.onnx")
from enum import Enum
from typing import Optional


# ============================================================================
#  ENUMS & DATA CLASSES
# ============================================================================

class UserCategory(Enum):
    """Self-evaluation user categories from about.md"""
    CHILD = "child"
    ADULT = "adult"
    ELDERLY = "elderly"
    SUSPICIOUS = "suspicious_account"
    POTENTIAL_SCAMMER = "potential_scammer"
    SCAMMER = "scammer"


class RiskLevel(Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


@dataclass
class UserProfile:
    """Represents a user's self-evaluation profile"""
    user_id: str
    name: str
    age: int
    account_balance: float
    account_age_days: int
    category: UserCategory = UserCategory.ADULT
    risk_score: float = 0.0
    flagged: bool = False
    flag_reason: str = ""


@dataclass
class Transaction:
    """Represents a single transaction to be evaluated"""
    sender_id: str
    sender_name: str
    sender_age: int
    sender_balance: float
    sender_account_age_days: int
    receiver_id: str
    receiver_name: str
    amount: float
    transaction_type: str  # TRANSFER, PAYMENT, CASH_OUT, DEBIT, CASH_IN
    timestamp: datetime
    is_offline: bool = False


@dataclass
class ComplianceLog:
    """Plain-text compliance log explaining the exact boundary breached"""
    timestamp: str
    transaction_id: str
    rule_name: str
    rule_description: str
    boundary_value: str
    actual_value: str
    result: str  # PASS / FAIL
    action: str  # ALLOW / WARN / BLOCK


@dataclass
class FraudResult:
    """Full result of fraud detection evaluation"""
    transaction_allowed: bool
    risk_level: RiskLevel
    onnx_fraud_probability: float
    sender_category: UserCategory
    compliance_logs: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    scammer_db_match: bool = False
    scammer_db_match_details: str = ""

    def to_dict(self):
        return {
            "transaction_allowed": self.transaction_allowed,
            "risk_level": self.risk_level.value,
            "onnx_fraud_probability": round(self.onnx_fraud_probability, 6),
            "sender_category": self.sender_category.value,
            "compliance_logs": [asdict(log) for log in self.compliance_logs],
            "warnings": self.warnings,
            "scammer_db_match": self.scammer_db_match,
            "scammer_db_match_details": self.scammer_db_match_details,
        }


# ============================================================================
#  SCAMMER DATABASE  (SC Investor Alert List + BNM FCA)
# ============================================================================

class ScammerDatabase:
    """
    Offline-cacheable scammer database.
    Loads from SC Investor Alert List CSV and provides fast lookup.
    Every time the system connects to wifi, this list gets refreshed.
    """

    def __init__(self, investor_alert_csv: str = DEFAULT_SCAMMER_CSV):
        self.scammer_names = set()
        self.scammer_aliases = set()
        self.scammer_entries = []
        self._load(investor_alert_csv)

    def _load(self, csv_path: str):
        if not os.path.exists(csv_path):
            print(f"[ScammerDB] Warning: {csv_path} not found. Running with empty database.")
            return

        try:
            df = pd.read_csv(csv_path)
            for _, row in df.iterrows():
                name = str(row.get("name", "")).strip().lower()
                aliases = str(row.get("aliases", "")).strip().lower()

                if name and name != "nan":
                    self.scammer_names.add(name)
                    self.scammer_entries.append({
                        "name": name,
                        "aliases": aliases,
                        "dataset": str(row.get("dataset", "")),
                        "schema": str(row.get("schema", "")),
                    })

                if aliases and aliases != "nan":
                    for alias in aliases.split(";"):
                        alias = alias.strip()
                        if alias:
                            self.scammer_aliases.add(alias)

            print(f"[ScammerDB] Loaded {len(self.scammer_names)} entities, "
                  f"{len(self.scammer_aliases)} aliases from {csv_path}")
        except Exception as e:
            print(f"[ScammerDB] Error loading {csv_path}: {e}")

    def lookup(self, name: str) -> tuple:
        """
        Check if a name matches any known scammer entity.
        Returns (is_match: bool, details: str)
        """
        name_lower = name.strip().lower()

        # Exact match on scammer names
        if name_lower in self.scammer_names:
            entry = next((e for e in self.scammer_entries if e["name"] == name_lower), {})
            return True, f"EXACT MATCH in {entry.get('dataset', 'scammer database')}: '{name}'"

        # Exact match on aliases
        if name_lower in self.scammer_aliases:
            return True, f"ALIAS MATCH in scammer database: '{name}'"

        # Fuzzy / partial match (substring)
        for scammer_name in self.scammer_names:
            if name_lower in scammer_name or scammer_name in name_lower:
                return True, f"PARTIAL MATCH in scammer database: '{name}' ~ '{scammer_name}'"

        return False, ""


# ============================================================================
#  USER SELF-EVALUATION ENGINE
# ============================================================================

class SelfEvaluationEngine:
    """
    Evaluates the user and categorises them:
      - child (age < 18)
      - elderly (age >= 60)
      - adult (18-59)
      - suspicious_account / potential_scammer / scammer
        (based on transaction history patterns)

    Each category gets custom protection policies.
    """

    @staticmethod
    def categorise_user(user: UserProfile, transaction_history: list = None) -> UserProfile:
        """Run self-evaluation to assign a user category"""

        # ---- Age-based categorisation ----
        # Only apply age-baseline if the user isn't already a known scammer/suspicious
        if user.category not in (UserCategory.SCAMMER, UserCategory.POTENTIAL_SCAMMER, UserCategory.SUSPICIOUS):
            if user.age < 18:
                user.category = UserCategory.CHILD
            elif user.age >= 60:
                user.category = UserCategory.ELDERLY
            else:
                user.category = UserCategory.ADULT

        # ---- History-based suspicion scoring ----
        if transaction_history:
            # Pattern: receives money from 60+ year-old persons multiple times
            # in a week, amount >= 1000 each time → likely scam against elderly
            elderly_high_value_count = 0
            recent_window = datetime.now() - timedelta(days=7)

            for txn in transaction_history:
                if (txn.get("receiver_id") == user.user_id
                        and txn.get("sender_age", 0) >= 60
                        and txn.get("amount", 0) >= 1000
                        and txn.get("timestamp", datetime.min) >= recent_window):
                    elderly_high_value_count += 1

            if elderly_high_value_count >= 3:
                user.category = UserCategory.SCAMMER
                user.flagged = True
                user.flag_reason = (
                    f"Received {elderly_high_value_count} high-value transactions "
                    f"(>= RM 1000) from elderly users (age >= 60) in the past 7 days"
                )
                user.risk_score = 1.0
            elif elderly_high_value_count >= 2:
                user.category = UserCategory.POTENTIAL_SCAMMER
                user.flagged = True
                user.flag_reason = (
                    f"Received {elderly_high_value_count} high-value transactions "
                    f"from elderly users in the past 7 days — monitoring"
                )
                user.risk_score = 0.7

        return user

    @staticmethod
    def get_policy(category: UserCategory) -> dict:
        """Return the protection policy for each category"""
        policies = {
            UserCategory.CHILD: {
                "max_single_transfer": 200,
                "daily_limit": 500,
                "require_guardian_approval": True,
                "blocked_hours": list(range(0, 6)),  # midnight to 6am
                "description": "Child account: strict limits, guardian approval required",
            },
            UserCategory.ELDERLY: {
                "max_single_transfer": 5000,
                "daily_limit": 10000,
                "require_guardian_approval": False,
                "blocked_hours": list(range(0, 5)),  # midnight to 5am
                "description": "Elderly account: stricter policy, easier money recovery",
            },
            UserCategory.ADULT: {
                "max_single_transfer": 50000,
                "daily_limit": 100000,
                "require_guardian_approval": False,
                "blocked_hours": [],
                "description": "Adult account: standard limits",
            },
            UserCategory.SUSPICIOUS: {
                "max_single_transfer": 1000,
                "daily_limit": 2000,
                "require_guardian_approval": False,
                "blocked_hours": list(range(0, 6)),
                "description": "Suspicious account: reduced limits, under review",
            },
            UserCategory.POTENTIAL_SCAMMER: {
                "max_single_transfer": 500,
                "daily_limit": 1000,
                "require_guardian_approval": False,
                "blocked_hours": list(range(0, 8)),
                "description": "Potential scammer: heavily restricted, under investigation",
            },
            UserCategory.SCAMMER: {
                "max_single_transfer": 0,
                "daily_limit": 0,
                "require_guardian_approval": False,
                "blocked_hours": list(range(0, 24)),  # blocked always
                "description": "SCAMMER: account frozen. Cannot receive money until proven otherwise",
            },
        }
        return policies.get(category, policies[UserCategory.ADULT])


# ============================================================================
#  DETERMINISTIC RULE ENGINE (White-Box, Plain-Text Compliance Logs)
# ============================================================================

class DeterministicRuleEngine:
    """
    Hardcoded, white-box rule engine.
    Prints a plain-text compliance log explaining the EXACT mathematical
    boundary breached. No black-box. Fully auditable.
    """

    @staticmethod
    def evaluate(txn: Transaction, sender_profile: UserProfile,
                 scammer_db: ScammerDatabase,
                 transaction_history: list = None) -> tuple:
        """
        Run all deterministic rules and return:
          (is_blocked: bool, risk_level: RiskLevel, logs: list[ComplianceLog], warnings: list[str])
        """
        logs = []
        warnings = []
        is_blocked = False
        risk_level = RiskLevel.SAFE
        policy = SelfEvaluationEngine.get_policy(sender_profile.category)
        txn_id = f"TXN-{txn.timestamp.strftime('%Y%m%d%H%M%S')}-{txn.sender_id[:6]}"

        # ---- RULE 1: HIGH-STAKE VELOCITY ----
        # Detect transfer (high_stake = receive > 1000 AND transfer > 1000 AND count > 2)
        if txn.amount > 1000 and transaction_history:
            recent_large = [
                h for h in transaction_history
                if h.get("sender_id") == txn.sender_id
                and h.get("amount", 0) > 1000
                and h.get("timestamp", datetime.min) >= datetime.now() - timedelta(hours=24)
            ]
            if len(recent_large) >= 2:
                log = ComplianceLog(
                    timestamp=datetime.now().isoformat(),
                    transaction_id=txn_id,
                    rule_name="HIGH_STAKE_VELOCITY",
                    rule_description="More than 2 transfers exceeding RM 1,000 within 24 hours",
                    boundary_value="max_count=2, min_amount=1000, window=24h",
                    actual_value=f"count={len(recent_large)+1}, amount={txn.amount}",
                    result="FAIL",
                    action="BLOCK",
                )
                logs.append(log)
                is_blocked = True
                risk_level = RiskLevel.BLOCKED
                warnings.append(
                    "[SYSTEM: ABNORMAL VELOCITY DETECTED. TRANSFER BLOCKED.] "
                    f"You have made {len(recent_large)+1} high-value transfers (> RM 1,000) "
                    f"in the past 24 hours."
                )

        # ---- RULE 2: TIME-BASED ANOMALY (Elderly at 2 AM) ----
        current_hour = txn.timestamp.hour
        if current_hour in policy.get("blocked_hours", []):
            severity = "BLOCK" if sender_profile.category in (
                UserCategory.ELDERLY, UserCategory.CHILD, UserCategory.SCAMMER
            ) else "WARN"

            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="TIME_ANOMALY",
                rule_description=f"Transaction at unusual hour for {sender_profile.category.value} account",
                boundary_value=f"blocked_hours={policy['blocked_hours']}",
                actual_value=f"transaction_hour={current_hour}",
                result="FAIL",
                action=severity,
            )
            logs.append(log)

            if severity == "BLOCK":
                is_blocked = True
                risk_level = RiskLevel.BLOCKED
                warnings.append(
                    f"[SYSTEM: TIME ANOMALY DETECTED. TRANSFER BLOCKED.] "
                    f"{sender_profile.category.value.upper()} account attempting transfer at "
                    f"{current_hour}:00. This is outside permitted hours."
                )
            else:
                risk_level = max(risk_level, RiskLevel.MEDIUM, key=lambda x: list(RiskLevel).index(x))
                warnings.append(
                    f"[WARNING] Transfer at {current_hour}:00 is unusual for your account type."
                )

        # ---- RULE 3: BALANCE DRAIN ----
        # If elderly people suddenly want to transfer everything they have
        balance_ratio = txn.amount / max(sender_profile.account_balance, 0.01)
        if balance_ratio > 0.8 and sender_profile.category == UserCategory.ELDERLY:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="ELDERLY_BALANCE_DRAIN",
                rule_description="Elderly account attempting to transfer more than 80% of balance",
                boundary_value="max_balance_ratio=0.80",
                actual_value=f"balance_ratio={balance_ratio:.2f} (amount={txn.amount}, balance={sender_profile.account_balance})",
                result="FAIL",
                action="BLOCK",
            )
            logs.append(log)
            is_blocked = True
            risk_level = RiskLevel.BLOCKED
            warnings.append(
                "[SYSTEM: BALANCE DRAIN DETECTED. TRANSFER BLOCKED.] "
                f"Elderly account attempting to transfer {balance_ratio*100:.0f}% of total balance "
                f"(RM {txn.amount} of RM {sender_profile.account_balance})."
            )
        elif balance_ratio > 0.9:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="BALANCE_DRAIN",
                rule_description="Account attempting to transfer more than 90% of balance",
                boundary_value="max_balance_ratio=0.90",
                actual_value=f"balance_ratio={balance_ratio:.2f}",
                result="FAIL",
                action="WARN",
            )
            logs.append(log)
            risk_level = max(risk_level, RiskLevel.HIGH, key=lambda x: list(RiskLevel).index(x))
            warnings.append(
                f"[WARNING] You are transferring {balance_ratio*100:.0f}% of your total balance."
            )

        # ---- RULE 4: SINGLE TRANSFER LIMIT ----
        max_transfer = policy.get("max_single_transfer", 50000)
        if txn.amount > max_transfer:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="SINGLE_TRANSFER_LIMIT",
                rule_description=f"Transfer exceeds {sender_profile.category.value} single transaction limit",
                boundary_value=f"max_single_transfer=RM {max_transfer}",
                actual_value=f"amount=RM {txn.amount}",
                result="FAIL",
                action="BLOCK",
            )
            logs.append(log)
            is_blocked = True
            risk_level = RiskLevel.BLOCKED
            warnings.append(
                f"[SYSTEM: TRANSFER LIMIT EXCEEDED. BLOCKED.] "
                f"Your {sender_profile.category.value} account limit is RM {max_transfer}. "
                f"Attempted: RM {txn.amount}."
            )

        # ---- RULE 5: SCAMMER DATABASE LOOKUP ----
        is_match, match_details = scammer_db.lookup(txn.receiver_name)
        if is_match:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="SCAMMER_DATABASE_HIT",
                rule_description="Receiver matches known scammer in SC Investor Alert / BNM FCA list",
                boundary_value="scammer_database=DENY_ALL",
                actual_value=f"receiver='{txn.receiver_name}', match='{match_details}'",
                result="FAIL",
                action="BLOCK",
            )
            logs.append(log)
            is_blocked = True
            risk_level = RiskLevel.BLOCKED
            warnings.append(
                f"[SYSTEM: SCAMMER DATABASE MATCH. TRANSFER BLOCKED.] "
                f"The recipient '{txn.receiver_name}' is flagged in the scammer database. "
                f"Detail: {match_details}"
            )

        # ---- RULE 6: SCAMMER ACCOUNT FREEZE ----
        if sender_profile.category == UserCategory.SCAMMER:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="SCAMMER_ACCOUNT_FREEZE",
                rule_description="Account is flagged as SCAMMER — all transactions blocked",
                boundary_value="account_status=FROZEN",
                actual_value=f"category={sender_profile.category.value}, reason={sender_profile.flag_reason}",
                result="FAIL",
                action="BLOCK",
            )
            logs.append(log)
            is_blocked = True
            risk_level = RiskLevel.BLOCKED
            warnings.append(
                "[SYSTEM: ACCOUNT FROZEN. ALL TRANSACTIONS BLOCKED.] "
                "This account has been classified as a scammer account and cannot "
                "send or receive money until proven otherwise."
            )

        # ---- If no rules triggered, it passes ----
        if not logs:
            log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=txn_id,
                rule_name="ALL_RULES_PASSED",
                rule_description="Transaction passed all deterministic rule checks",
                boundary_value="N/A",
                actual_value="N/A",
                result="PASS",
                action="ALLOW",
            )
            logs.append(log)

        return is_blocked, risk_level, logs, warnings


# ============================================================================
#  ONNX NEURAL NETWORK INFERENCE
# ============================================================================

import multiprocessing

class OnnxFraudModel:
    """
    Smart Edge AI Engine.
    Automatically selects between Float32 (High Accuracy) and Int8 (High Speed)
    models based on the device's hardware capabilities.
    """

    TYPE_ENCODING = {
        "CASH_IN": 0, "CASH_OUT": 1, "DEBIT": 2, "PAYMENT": 3, "TRANSFER": 4,
    }

    def __init__(self, normal_model_path: str, quantized_model_path: str):
        # SMART DEVICE SELECTOR: Check CPU Cores to simulate device performance
        cpu_cores = multiprocessing.cpu_count()
        
        if cpu_cores <= 4:
            print(f"[AI CORE] Budget device detected ({cpu_cores} cores). Loading Quantized Int8 Model for speed.")
            chosen_model = quantized_model_path
        else:
            print(f"[AI CORE] High-end device detected ({cpu_cores} cores). Loading Normal Float32 Model for max accuracy.")
            chosen_model = normal_model_path

        if not os.path.exists(chosen_model):
            raise FileNotFoundError(f"ONNX model not found: {chosen_model}")
            
        self.session = ort.InferenceSession(chosen_model)
        self.input_name = self.session.get_inputs()[0].name

    def predict(self, txn: Transaction, transaction_history: list = None) -> float:
        txn_type_encoded = self.TYPE_ENCODING.get(txn.transaction_type.upper(), 3)
        new_balance_sender = max(txn.sender_balance - txn.amount, 0.0)
        
        hour_of_day = txn.timestamp.hour
        balance_drain_ratio = (txn.amount / txn.sender_balance) if txn.sender_balance > 0 else 0.0

        # --- NEW: CALCULATE VELOCITY ON THE FLY ---
        # 1. Count past transactions in the offline cache
        daily_transfer_count = len(transaction_history) if transaction_history else 0
        
        # 2. Calculate historical average (default to 1.0 ratio if no history)
        if transaction_history:
            avg_amount = sum(h.get("amount", 0) for h in transaction_history) / len(transaction_history)
            amount_vs_average = (txn.amount / avg_amount) if avg_amount > 0 else 1.0
        else:
            amount_vs_average = 1.0

        # Build the EXACT 10 features expected by the ONNX model
        raw_features = np.array([
            txn_type_encoded,
            txn.amount,
            txn.sender_balance,
            new_balance_sender,
            0.0,        # oldbalanceDest
            txn.amount, # newbalanceDest
            hour_of_day,
            balance_drain_ratio,
            daily_transfer_count,  # <-- NEW
            amount_vs_average      # <-- NEW
        ], dtype=np.float32)

        # 3. Apply the Standard Scaler 
        # !!! YOU MUST UPDATE THESE ARRAYS WITH THE NEW 10-NUMBER CONSOLE OUTPUT !!!
        scaler_means = np.array([1.7078, 163120.888, 878499.1822, 898848.3621, 979592.8811, 1138019.2403, 0.0002, 1.0, 13.9437, 76.6354])
        scaler_scales = np.array([1.3444, 268863.0357, 2942850.0581, 2979972.4519, 2320771.3175, 2467818.0594, 0.0128, 0.0129, 4.2905, 2193.2676])
        
        scaled_features = (raw_features - scaler_means) / scaler_scales
        
        # Reshape for the batch size (1, 10) and run inference
        final_input = np.array([scaled_features], dtype=np.float32)
        output = self.session.run(None, {self.input_name: final_input})
        
        raw_score = float(output[0][0][0])
        probability = 1.0 / (1.0 + np.exp(-raw_score))
        
        return probability


# ============================================================================
#  MAIN FRAUD DETECTION ENGINE
# ============================================================================

class FraudDetectionEngine:
    def __init__(self, 
                 normal_onnx_path: str = DEFAULT_ONNX_MODEL,
                 quantized_onnx_path: str = DEFAULT_ONNX_MODEL.replace(".onnx", "_quantized.onnx"),
                 scammer_db_csv: str = DEFAULT_SCAMMER_CSV):
                 
        # 1. Initialize the Smart AI Model
        self.onnx_model = OnnxFraudModel(normal_onnx_path, quantized_onnx_path)
        
        # 2. Initialize the Deterministic Rule Engines & Databases
        self.scammer_db = ScammerDatabase(scammer_db_csv)
        self.rule_engine = DeterministicRuleEngine()
        self.self_eval = SelfEvaluationEngine()

        # 3. In-memory log of suspicious persons (flagged across sessions)
        self.flagged_persons = {}

    def evaluate_transaction(self, txn: Transaction,
                             transaction_history: list = None) -> FraudResult:
        """
        Full fraud evaluation pipeline.
        Returns a FraudResult with all details.
        """

        # ---- STEP 1: Self-evaluate the sender ----
        sender_profile = UserProfile(
            user_id=txn.sender_id,
            name=txn.sender_name,
            age=txn.sender_age,
            account_balance=txn.sender_balance,
            account_age_days=txn.sender_account_age_days,
        )

        # Check if sender was previously flagged
        if txn.sender_id in self.flagged_persons:
            prev = self.flagged_persons[txn.sender_id]
            sender_profile.category = prev["category"]
            sender_profile.flagged = True
            sender_profile.flag_reason = prev["reason"]

        sender_profile = self.self_eval.categorise_user(
            sender_profile, transaction_history
        )

        # ---- STEP 2: Run ONNX Neural Network ----
        onnx_probability = self.onnx_model.predict(txn)

        # ---- STEP 3: Run Deterministic Rule Engine ----
        is_blocked, risk_level, compliance_logs, warnings = self.rule_engine.evaluate(
            txn, sender_profile, self.scammer_db, transaction_history
        )

        # ---- STEP 4: Combine NN score with rule engine ----
        # If the NN says high fraud probability, treat as a rule breach too
        if onnx_probability > 0.5 and not is_blocked:
            nn_log = ComplianceLog(
                timestamp=datetime.now().isoformat(),
                transaction_id=f"TXN-{txn.timestamp.strftime('%Y%m%d%H%M%S')}-{txn.sender_id[:6]}",
                rule_name="ONNX_ANOMALY_DETECTION",
                rule_description="Neural network detected anomalous transaction pattern",
                boundary_value="max_fraud_probability=0.50",
                actual_value=f"fraud_probability={onnx_probability:.4f}",
                result="FAIL",
                action="BLOCK",
            )
            compliance_logs.append(nn_log)
            is_blocked = True
            risk_level = RiskLevel.BLOCKED
            warnings.append(
                f"[SYSTEM: ABNORMAL PATTERN DETECTED. TRANSFER BLOCKED.] "
                f"AI fraud probability: {onnx_probability*100:.1f}%"
            )
        elif onnx_probability > 0.3:
            warnings.append(
                f"[WARNING] Elevated AI fraud score: {onnx_probability*100:.1f}%. "
                f"Proceed with caution."
            )
            risk_level = max(risk_level, RiskLevel.MEDIUM, key=lambda x: list(RiskLevel).index(x))

        # ---- STEP 5: Check scammer DB for receiver ----
        scammer_match, scammer_detail = self.scammer_db.lookup(txn.receiver_name)

        # ---- STEP 6: Flag suspicious persons for future lookups ----
        if sender_profile.flagged:
            self.flagged_persons[txn.sender_id] = {
                "category": sender_profile.category,
                "reason": sender_profile.flag_reason,
            }

        # ---- Build final result ----
        result = FraudResult(
            transaction_allowed=not is_blocked,
            risk_level=risk_level,
            onnx_fraud_probability=onnx_probability,
            sender_category=sender_profile.category,
            compliance_logs=compliance_logs,
            warnings=warnings,
            scammer_db_match=scammer_match,
            scammer_db_match_details=scammer_detail,
        )

        return result

    def print_result(self, result: FraudResult):
        """Pretty-print the fraud detection result with compliance logs"""
        print("\n" + "=" * 70)
        print("  FRAUD DETECTION ENGINE - COMPLIANCE REPORT")
        print("=" * 70)

        status = "PASS: ALLOWED" if result.transaction_allowed else "FAIL: BLOCKED"
        print(f"  Status          : {status}")
        print(f"  Risk Level      : {result.risk_level.value}")
        print(f"  AI Fraud Score  : {result.onnx_fraud_probability * 100:.2f}%")
        print(f"  Sender Category : {result.sender_category.value}")
        print(f"  Scammer DB Hit  : {'YES — ' + result.scammer_db_match_details if result.scammer_db_match else 'No'}")

        if result.warnings:
            print("\n  --- WARNINGS ---")
            for w in result.warnings:
                print(f"  [!] {w}")

        print("\n  --- COMPLIANCE LOG (Plain-Text, White-Box) ---")
        for log in result.compliance_logs:
            print(f"  [{log.timestamp}]")
            print(f"    Rule       : {log.rule_name}")
            print(f"    Description: {log.rule_description}")
            print(f"    Boundary   : {log.boundary_value}")
            print(f"    Actual     : {log.actual_value}")
            print(f"    Result     : {log.result} -> {log.action}")
            print()

        print("=" * 70)


# Add this to the very bottom of fraud_detection_engine.py
if __name__ == "__main__":
    print("Booting up Hackathon Fraud Engine...")
    engine = FraudDetectionEngine()

    # 1. Create a fake transaction (65-year-old sending RM 4,500 at 2 AM)
    test_txn = Transaction(
        sender_id="user_123",
        sender_name="Uncle Ah Kao",
        sender_age=65,
        sender_balance=5000.0,
        sender_account_age_days=300,
        receiver_id="user_999",
        receiver_name="Aether Bridge Financial", # This is on your blacklist!
        amount=4500.0,
        transaction_type="TRANSFER",
        timestamp=datetime.now().replace(hour=2) # 2:00 AM
    )

    # 2. "Talk" to the model
    print("Evaluating transaction...")
    result = engine.evaluate_transaction(test_txn, transaction_history=[])
    
    # 3. Print the gorgeous compliance log
    engine.print_result(result)