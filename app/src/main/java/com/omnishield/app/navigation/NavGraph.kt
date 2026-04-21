package com.omnishield.app.navigation

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.omnishield.app.OmniShieldViewModel
import com.omnishield.app.ui.screens.FraudAlertScreen
import com.omnishield.app.ui.screens.HomeDashboardScreen
import com.omnishield.app.ui.screens.PayScreen
import com.omnishield.app.ui.screens.PaymentFailedScreen
import com.omnishield.app.ui.screens.PaymentSuccessScreen
import com.omnishield.app.ui.screens.ReceiveScreen

// ============================================================
// OmniShield Navigation Graph — All screens wired
// ============================================================

@Composable
fun OmniShieldNavGraph(
    navController: NavHostController,
    viewModel: OmniShieldViewModel = viewModel()
) {
    NavHost(
        navController = navController,
        startDestination = Routes.HOME
    ) {

        // ── Home Dashboard ──────────────────────────────────
        composable(Routes.HOME) {
            HomeDashboardScreen(
                viewModel = viewModel,
                onNavigateToPay = {
                    navController.navigate(Routes.PAY)
                },
                onNavigateToReceive = {
                    navController.navigate(Routes.RECEIVE)
                }
            )
        }

        // ── Receive (Static QR) ─────────────────────────────
        composable(Routes.RECEIVE) {
            ReceiveScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }

        // ── Pay (Camera Scanner + Amount Input) ─────────────
        composable(Routes.PAY) {
            PayScreen(
                viewModel = viewModel,
                onNavigateBack = {
                    navController.popBackStack()
                },
                onPaymentSuccess = {
                    navController.navigate(Routes.PAYMENT_SUCCESS) {
                        // Pop PayScreen so Back goes to Home
                        popUpTo(Routes.HOME) { inclusive = false }
                    }
                },
                onPaymentFailed = {
                    navController.navigate(Routes.PAYMENT_FAILED) {
                        popUpTo(Routes.HOME) { inclusive = false }
                    }
                },
                onFraudAlert = {
                    navController.navigate(Routes.FRAUD_ALERT) {
                        popUpTo(Routes.HOME) { inclusive = false }
                    }
                }
            )
        }

        // ── Payment Success ─────────────────────────────────
        composable(Routes.PAYMENT_SUCCESS) {
            PaymentSuccessScreen(
                onNavigateHome = {
                    navController.popBackStack(Routes.HOME, inclusive = false)
                }
            )
        }

        // ── Payment Failed ──────────────────────────────────
        composable(Routes.PAYMENT_FAILED) {
            PaymentFailedScreen(
                onTryAgain = {
                    // Navigate back to PayScreen for a retry
                    navController.navigate(Routes.PAY) {
                        popUpTo(Routes.HOME) { inclusive = false }
                    }
                },
                onCancel = {
                    navController.popBackStack(Routes.HOME, inclusive = false)
                }
            )
        }

        // ── Fraud Alert ─────────────────────────────────────
        composable(Routes.FRAUD_ALERT) {
            FraudAlertScreen(
                viewModel = viewModel,
                onNavigateHome = {
                    // ViewModel.resetFraudCounter() is called inside
                    // FraudAlertScreen before this lambda fires
                    navController.popBackStack(Routes.HOME, inclusive = false)
                }
            )
        }
    }
}
