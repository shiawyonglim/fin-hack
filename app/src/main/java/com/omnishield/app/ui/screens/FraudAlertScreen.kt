package com.omnishield.app.ui.screens

import androidx.compose.animation.core.EaseInOutSine
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.GppBad
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.omnishield.app.OmniShieldViewModel
import com.omnishield.app.ui.theme.ErrorDeepRed
import com.omnishield.app.ui.theme.OnError

// ============================================================
// FraudAlertScreen — Automated Block (3rd payment attempt)
// ============================================================
// Full-screen deep red gradient. No Scaffold — intentionally
// dramatic and non-dismissable to convey urgency.
// ============================================================

@Composable
fun FraudAlertScreen(
    viewModel: OmniShieldViewModel,
    onNavigateHome: () -> Unit
) {
    // Pulsing shield icon
    val infiniteTransition = rememberInfiniteTransition(label = "fraudPulse")
    val iconScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.1f,
        animationSpec = infiniteRepeatable(
            animation = tween(800, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "shieldScale"
    )

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(
                Brush.verticalGradient(
                    colors = listOf(
                        ErrorDeepRed,
                        ErrorDeepRed.copy(alpha = 0.85f),
                        Color(0xFF4A0000) // Deep dark red bottom
                    )
                )
            )
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // ── Pulsing Blocked Shield Icon ──────────────────
            Surface(
                modifier = Modifier
                    .size(140.dp)
                    .scale(iconScale),
                shape = CircleShape,
                color = Color.White.copy(alpha = 0.15f)
            ) {
                Box(contentAlignment = Alignment.Center) {
                    Icon(
                        imageVector = Icons.Filled.GppBad,
                        contentDescription = "Fraud Alert",
                        modifier = Modifier.size(90.dp),
                        tint = OnError
                    )
                }
            }

            Spacer(Modifier.height(40.dp))

            // ── Headline ─────────────────────────────────────
            Text(
                text = "Transfer Blocked",
                style = MaterialTheme.typography.displayMedium,
                fontWeight = FontWeight.Black,
                color = OnError,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(16.dp))

            HorizontalDivider(
                modifier = Modifier.width(80.dp),
                thickness = 3.dp,
                color = OnError.copy(alpha = 0.4f)
            )

            Spacer(Modifier.height(16.dp))

            // ── Sub-headline ─────────────────────────────────
            Text(
                text = "Suspicious Activity Detected",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = OnError.copy(alpha = 0.9f),
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(12.dp))

            // ── Body ─────────────────────────────────────────
            Text(
                text = "Multiple rapid transactions have been flagged\n" +
                        "by our fraud detection system. This transfer\n" +
                        "has been automatically blocked for your protection.",
                style = MaterialTheme.typography.bodyLarge.copy(
                    lineHeight = 26.sp
                ),
                color = OnError.copy(alpha = 0.7f),
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(48.dp))

            // ── Return to Home — RESETS FRAUD COUNTER ────────
            Button(
                onClick = {
                    viewModel.resetFraudCounter() // Reset for demo replay
                    onNavigateHome()
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(60.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = OnError,
                    contentColor = ErrorDeepRed
                ),
                elevation = ButtonDefaults.buttonElevation(defaultElevation = 6.dp)
            ) {
                Icon(
                    Icons.Filled.Shield,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    "Return to Home",
                    style = MaterialTheme.typography.titleLarge,
                    fontWeight = FontWeight.Bold
                )
            }
        }
    }
}
