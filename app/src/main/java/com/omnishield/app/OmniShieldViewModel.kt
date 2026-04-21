package com.omnishield.app

import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.lifecycle.ViewModel

// ============================================================
// OmniShieldViewModel — Single source of truth for all demo state
// ============================================================

/**
 * Payment result enum used to drive navigation after processing.
 */
enum class PaymentResult {
    SUCCESS,
    INSUFFICIENT_FUNDS,
    FRAUD_BLOCKED
}

class OmniShieldViewModel : ViewModel() {

    // ── Network State ───────────────────────────────────────
    var isOnline by mutableStateOf(true)
        private set

    // ── Balances ────────────────────────────────────────────
    // Online starts at 250, Offline starts at 200.
    // Offline is conceptually a subset of Online.
    // ALL payments deduct from BOTH simultaneously.
    var onlineBalance by mutableStateOf(250.00)
        private set

    var offlineBalance by mutableStateOf(200.00)
        private set

    // ── Fraud Velocity Tracking ─────────────────────────────
    // 3rd consecutive attempt → FraudAlertScreen.
    // Resets ONLY when user taps "Return to Home" from FraudAlertScreen.
    var paymentAttemptCount by mutableIntStateOf(0)
        private set

    // ── Voice Assistant ─────────────────────────────────────
    var preFillAmount by mutableStateOf<String?>(null)
        private set

    var showVoiceSheet by mutableStateOf(false)
        private set

    // ── Processing / Loading ────────────────────────────────
    var isProcessing by mutableStateOf(false)
        private set

    // ═══════════════════════════════════════════════════════
    // Actions
    // ═══════════════════════════════════════════════════════

    /** Toggle between Online and Offline mode (Wi-Fi button). */
    fun toggleNetworkState() {
        isOnline = !isOnline
    }

    /**
     * Core payment logic with hardcoded demo rules:
     * 1. Increment attempt counter
     * 2. If 3rd attempt → FRAUD_BLOCKED (no balance check)
     * 3. If amount > offlineBalance → INSUFFICIENT_FUNDS
     * 4. Otherwise → deduct from both balances → SUCCESS
     */
    fun processPayment(amount: Double): PaymentResult {
        paymentAttemptCount++

        // RULE 1: Fraud takes ABSOLUTE priority on 3rd attempt
        if (paymentAttemptCount >= 3) {
            return PaymentResult.FRAUD_BLOCKED
        }

        // RULE 2: Insufficient funds — check against offline balance
        if (amount > offlineBalance) {
            return PaymentResult.INSUFFICIENT_FUNDS
        }

        // RULE 3: Success — deduct from BOTH, floor at 0.0
        offlineBalance = maxOf(0.0, offlineBalance - amount)
        onlineBalance = maxOf(0.0, onlineBalance - amount)

        return PaymentResult.SUCCESS
    }

    /**
     * Reset fraud counter — called ONLY from FraudAlertScreen's
     * "Return to Home" button. Enables demo replay for judges.
     */
    fun resetFraudCounter() {
        paymentAttemptCount = 0
    }

    /** Toggle processing spinner for the 1.5s "Confirm & Lock" delay. */
    fun updateProcessingState(processing: Boolean) {
        isProcessing = processing
    }

    // ── Voice Assistant Actions ─────────────────────────────

    /** Open the voice bottom sheet (Mic FAB pressed). */
    fun triggerVoiceAssistant() {
        preFillAmount = null
        showVoiceSheet = true
    }

    /** Mock voice recognition complete — pre-fill RM 15.00. */
    fun onVoiceRecognized() {
        preFillAmount = "15.00"
    }

    /** Dismiss the voice bottom sheet. */
    fun dismissVoiceSheet() {
        showVoiceSheet = false
    }

    /** Clear pre-fill after PayScreen has consumed it. */
    fun clearPreFillAmount() {
        preFillAmount = null
    }

    // ── Demo Reset ──────────────────────────────────────────

    /** Full reset for starting a fresh demo run. */
    fun resetDemo() {
        onlineBalance = 250.00
        offlineBalance = 200.00
        paymentAttemptCount = 0
        preFillAmount = null
        showVoiceSheet = false
        isProcessing = false
    }
}
