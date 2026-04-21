# Zero-Trust Edge Engine: Rule Specifications

This document outlines the deterministic, offline White-Box Rule Engine integrated into the FinHack Edge Simulator. These rules execute instantly on the device, dropping connections if bounds are breached before allowing the transaction to pass to the ONNX Deep Learning check or online servers.

---

## 1. User Categorization (Self-Evaluation)
The system categorizes users into dynamic archetypes based on their age and historical behavior.

| Category | Age Criteria | Context trigger |
|--|--|--|
| **CHILD** | `< 18` | N/A |
| **ADULT** | `18 - 59` | Standard users |
| **ELDERLY** | `>= 60` | High protection profile |
| **SUSPICIOUS** | N/A | User manually flagged or displaying aggressive edge behavior |
| **POTENTIAL_SCAMMER**| N/A | Receiver got 2+ high-value transfers (>= RM 1000) from ELDERLY accounts in the last 7 days |
| **SCAMMER** | N/A | Receiver got 3+ high-value transfers (>= RM 1000) from ELDERLY accounts in the last 7 days |

---

## 2. Dynamic Threshold Policies
Based on the category evaluated above, the device enforces hard mathematical limits on the sender:

| Persona | Single TX Limit (RM) | Offline Blocked Hours (Disabled Time) |
|--|--|--|
| **CHILD** | `RM 200` | Midnight to 6:00 AM (`0,1,2,3,4,5`) |
| **ELDERLY** | `RM 5,000` | Midnight to 5:00 AM (`0,1,2,3,4`) |
| **ADULT** | `RM 50,000` | None |
| **SUSPICIOUS**| `RM 1,000` | Midnight to 6:00 AM (`0,1,2,3,4,5`) |
| **POTENTIAL_SCAMMER**| `RM 500` | Midnight to 8:00 AM (`0,1,2,3,4,5,6,7`) |
| **SCAMMER** | `RM 0` (FROZEN) | 24 Hours (`0-23`) |

---

## 3. Deterministic Safety Checks (Pre-ONNX)
Before invoking the PyTorch ONNX model, the following sequential gates are verified:

### [Rule 0] SCAMMER_DATABASE_HIT
**Trigger:** Receiver organization matches the pre-cached Securities Commission (SC) or BNM Alert List (e.g., Questra, Master Binary).
**Action:** `FAIL -> BLOCK`

### [Rule 1] HIGH_STAKE_VELOCITY
**Trigger:** 3+ consecutive transfers over `RM 1000` within a sliding `24 hour` window.
**Action:** `FAIL -> BLOCK`

### [Rule 2] TIME_ANOMALY
**Trigger:** Transaction falls within the restricted `blocked_hours` parameter assigned to the user profile.
**Action:** 
- If user is `CHILD`, `ELDERLY`, or `SCAMMER`: `BLOCK`
- Otherwise: `WARN` (Proceeds with elevated Risk Flag)

### [Rule 3] BALANCE_DRAIN (The Protection Rule)
**Trigger (Elderly):** Sender is > 60 years old and attempts to transfer > 80% of their total balance in one go.
**Action:** `FAIL -> BLOCK`
**Trigger (General):** Any sender transferring > 90% of their total balance.
**Action:** `FAIL -> WARN`

### [Rule 4] SINGLE_TRANSFER_LIMIT
**Trigger:** Transaction exceeds the hard limit stated in the Dynamic Threshold table.
**Action:** `FAIL -> BLOCK`

### [Rule 5] FROZEN_ACCOUNT
**Trigger:** Sending account is classified as a `SCAMMER`.
**Action:** `FAIL -> BLOCK`

### [Rule 6] INSUFFICIENT_FUNDS
**Trigger:** Transfer amount is larger than available balance.
**Action:** `FAIL -> BLOCK`

---

## 4. The Final Gate: ONNX_NEURAL_NETWORK
If all semantic deterministic checks succeed, the `[Type, Amount, Old_Balance, New_Balance]` parameters are normalized via our `StandardScaler` matrix and piped into the WebAssembly ONNX `fraud_detection_model.onnx`. 

**Trigger:** Inference output probability node exceeds `50.00%`.
**Action:** `FAIL -> BLOCK`

If the probability output completes below 50% and all other rules evaluate safely, the UI prints `ALL_RULES_PASSED` and finalizes the offline mesh signature.

5. account age based on the acocunt age there is a limit what it can handles and transfer
if the account age is very new and 