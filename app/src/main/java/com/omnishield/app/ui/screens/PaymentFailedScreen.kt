package com.omnishield.app.ui.screens

import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ErrorOutline
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.omnishield.app.ui.theme.ErrorDeepRed
import com.omnishield.app.ui.theme.ErrorRedContainer
import com.omnishield.app.ui.theme.NeutralGrey
import com.omnishield.app.ui.theme.OmniOrange
import com.omnishield.app.ui.theme.OnOmniOrange
import kotlinx.coroutines.delay

// ============================================================
// PaymentFailedScreen — Insufficient funds
// ============================================================

@Composable
fun PaymentFailedScreen(
    onTryAgain: () -> Unit,
    onCancel: () -> Unit
) {
    // Brief shake animation on the error icon
    val infiniteTransition = rememberInfiniteTransition(label = "shake")
    val shakeOffset by infiniteTransition.animateFloat(
        initialValue = -4f,
        targetValue = 4f,
        animationSpec = infiniteRepeatable(
            animation = tween(100, easing = LinearEasing),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shakeX"
    )

    // Stop shaking after 600ms
    var isShaking by remember { mutableStateOf(true) }
    LaunchedEffect(Unit) {
        delay(600L)
        isShaking = false
    }

    Scaffold(
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // ── Error Icon with Shake ────────────────────────
            Surface(
                modifier = Modifier
                    .size(120.dp)
                    .offset(x = if (isShaking) shakeOffset.dp else 0.dp),
                shape = CircleShape,
                color = ErrorRedContainer
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Filled.ErrorOutline,
                        contentDescription = "Failed",
                        modifier = Modifier.size(80.dp),
                        tint = ErrorDeepRed
                    )
                }
            }

            Spacer(Modifier.height(32.dp))

            Text(
                text = "Transaction Failed.",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = ErrorDeepRed,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(12.dp))

            Text(
                text = "Insufficient offline balance\nto complete this payment.",
                style = MaterialTheme.typography.bodyLarge,
                color = NeutralGrey,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(48.dp))

            // ── Try Again (Orange) ───────────────────────────
            Button(
                onClick = onTryAgain,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = OmniOrange,
                    contentColor = OnOmniOrange
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp)
            ) {
                Text(
                    "Try Again",
                    style = MaterialTheme.typography.titleLarge
                )
            }

            Spacer(Modifier.height(16.dp))

            // ── Cancel (Outlined) ────────────────────────────
            OutlinedButton(
                onClick = onCancel,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.outlinedButtonColors(
                    contentColor = NeutralGrey
                )
            ) {
                Text(
                    "Cancel",
                    style = MaterialTheme.typography.titleLarge
                )
            }
        }
    }
}
