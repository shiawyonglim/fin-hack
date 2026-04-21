package com.omnishield.app.ui.screens

import androidx.compose.animation.animateColorAsState
import androidx.compose.animation.core.EaseInOutSine
import androidx.compose.animation.core.EaseOut
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
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
import androidx.compose.material.icons.automirrored.outlined.CallReceived
import androidx.compose.material.icons.automirrored.outlined.Send
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material.icons.filled.WifiOff
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FabPosition
import androidx.compose.material3.FloatingActionButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LargeFloatingActionButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SheetState
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.omnishield.app.OmniShieldViewModel
import com.omnishield.app.ui.theme.ErrorDeepRed
import com.omnishield.app.ui.theme.NeutralGrey
import com.omnishield.app.ui.theme.OmniOrange
import com.omnishield.app.ui.theme.OnOmniOrange
import com.omnishield.app.ui.theme.SuccessGreen
import kotlinx.coroutines.delay

// ============================================================
// HomeDashboardScreen — Main entry screen after launch
// ============================================================

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeDashboardScreen(
    viewModel: OmniShieldViewModel,
    onNavigateToPay: () -> Unit,
    onNavigateToReceive: () -> Unit
) {
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)

    // ── Voice Assistant Bottom Sheet ────────────────────────
    if (viewModel.showVoiceSheet) {
        VoiceAssistantBottomSheet(
            sheetState = sheetState,
            onDismiss = { viewModel.dismissVoiceSheet() },
            onNavigateToPay = {
                viewModel.dismissVoiceSheet()
                viewModel.onVoiceRecognized() // Pre-fill "15.00"
                onNavigateToPay()
            }
        )
    }

    // ── Main Scaffold ───────────────────────────────────────
    Scaffold(
        topBar = {
            HomeDashboardTopBar(
                isOnline = viewModel.isOnline,
                onToggleNetwork = { viewModel.toggleNetworkState() }
            )
        },
        floatingActionButton = {
            MicFab(onClick = { viewModel.triggerVoiceAssistant() })
        },
        floatingActionButtonPosition = FabPosition.Center,
        containerColor = MaterialTheme.colorScheme.background
    ) { innerPadding ->

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(horizontal = 24.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            // ── Top Section: Greeting + Balances ────────────
            Column {
                Spacer(Modifier.height(16.dp))

                Text(
                    text = "Hello User,",
                    style = MaterialTheme.typography.headlineLarge,
                    color = MaterialTheme.colorScheme.onBackground
                )

                Spacer(Modifier.height(32.dp))

                BalanceDisplay(
                    isOnline = viewModel.isOnline,
                    onlineBalance = viewModel.onlineBalance,
                    offlineBalance = viewModel.offlineBalance
                )
            }

            // ── Bottom Section: Action Buttons ──────────────
            Column {
                ActionButtonRow(
                    onPayClick = onNavigateToPay,
                    onReceiveClick = onNavigateToReceive
                )
                // Reserve space so buttons don't overlap with the massive MIC FAB
                Spacer(Modifier.height(140.dp))
            }
        }
    }
}

// ============================================================
// Top App Bar — "Repo" chip + Network toggle
// ============================================================

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun HomeDashboardTopBar(
    isOnline: Boolean,
    onToggleNetwork: () -> Unit
) {
    val statusColor by animateColorAsState(
        targetValue = if (isOnline) SuccessGreen else ErrorDeepRed,
        animationSpec = tween(300),
        label = "statusColor"
    )

    TopAppBar(
        title = {
            // "Repo" chip
            Surface(
                shape = RoundedCornerShape(8.dp),
                color = MaterialTheme.colorScheme.surfaceVariant,
                tonalElevation = 2.dp
            ) {
                Text(
                    text = "Repo",
                    modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
                    style = MaterialTheme.typography.labelLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        },
        actions = {
            // Network status pill with toggle
            Surface(
                shape = RoundedCornerShape(12.dp),
                color = statusColor.copy(alpha = 0.12f)
            ) {
                Row(
                    modifier = Modifier.padding(start = 12.dp, end = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    Text(
                        text = if (isOnline) "Online" else "Offline",
                        style = MaterialTheme.typography.labelLarge,
                        color = statusColor
                    )
                    IconButton(onClick = onToggleNetwork) {
                        Icon(
                            imageVector = if (isOnline) Icons.Filled.Wifi else Icons.Filled.WifiOff,
                            contentDescription = "Toggle network state",
                            tint = statusColor
                        )
                    }
                }
            }
        },
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color.Transparent
        )
    )
}

// ============================================================
// Dynamic Balance Display — Swaps prominence based on isOnline
// ============================================================

@Composable
private fun BalanceDisplay(
    isOnline: Boolean,
    onlineBalance: Double,
    offlineBalance: Double
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        if (isOnline) {
            // ONLINE mode: offline is secondary, online is massive
            SecondaryBalanceLabel(
                label = "Offline Balance",
                amount = offlineBalance
            )
            PrimaryBalanceDisplay(
                label = "Online Balance",
                amount = onlineBalance
            )
        } else {
            // OFFLINE mode: online is secondary, offline is massive
            SecondaryBalanceLabel(
                label = "Online Balance",
                amount = onlineBalance
            )
            PrimaryBalanceDisplay(
                label = "Offline Balance",
                amount = offlineBalance
            )
        }
    }
}

@Composable
private fun SecondaryBalanceLabel(label: String, amount: Double) {
    Text(
        text = "$label: RM ${"%.2f".format(amount)}",
        style = MaterialTheme.typography.bodyLarge,
        color = NeutralGrey
    )
}

@Composable
private fun PrimaryBalanceDisplay(label: String, amount: Double) {
    Column {
        Text(
            text = label,
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onBackground.copy(alpha = 0.7f)
        )
        Text(
            text = "RM ${"%.2f".format(amount)}",
            style = MaterialTheme.typography.displayLarge,
            color = MaterialTheme.colorScheme.onBackground,
            fontWeight = FontWeight.Black
        )
    }
}

// ============================================================
// Action Button Row — "Receive" and "Pay" (Orange, large)
// ============================================================

@Composable
private fun ActionButtonRow(
    onPayClick: () -> Unit,
    onReceiveClick: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // ── Receive Button ──────────────────────────────────
        Button(
            onClick = onReceiveClick,
            modifier = Modifier
                .weight(1f)
                .height(64.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = OmniOrange,
                contentColor = OnOmniOrange
            ),
            elevation = ButtonDefaults.buttonElevation(
                defaultElevation = 4.dp,
                pressedElevation = 8.dp
            )
        ) {
            Icon(
                Icons.AutoMirrored.Outlined.CallReceived,
                contentDescription = null,
                modifier = Modifier.size(24.dp)
            )
            Spacer(Modifier.width(8.dp))
            Text(
                "Receive",
                style = MaterialTheme.typography.titleLarge
            )
        }

        // ── Pay Button ──────────────────────────────────────
        Button(
            onClick = onPayClick,
            modifier = Modifier
                .weight(1f)
                .height(64.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = OmniOrange,
                contentColor = OnOmniOrange
            ),
            elevation = ButtonDefaults.buttonElevation(
                defaultElevation = 4.dp,
                pressedElevation = 8.dp
            )
        ) {
            Icon(
                Icons.AutoMirrored.Outlined.Send,
                contentDescription = null,
                modifier = Modifier.size(24.dp)
            )
            Spacer(Modifier.width(8.dp))
            Text(
                "Pay",
                style = MaterialTheme.typography.titleLarge
            )
        }
    }
}

// ============================================================
// Mic FAB — Massive, pulsing, bottom-center
// ============================================================

@Composable
private fun MicFab(onClick: () -> Unit) {
    val infiniteTransition = rememberInfiniteTransition(label = "micPulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.08f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "fabScale"
    )

    LargeFloatingActionButton(
        onClick = onClick,
        modifier = Modifier.scale(scale),
        shape = CircleShape,
        containerColor = OmniOrange,
        contentColor = OnOmniOrange,
        elevation = FloatingActionButtonDefaults.elevation(
            defaultElevation = 8.dp,
            pressedElevation = 12.dp
        )
    ) {
        Icon(
            imageVector = Icons.Filled.Mic,
            contentDescription = "Voice Assistant",
            modifier = Modifier.size(36.dp)
        )
    }
}

// ============================================================
// Voice Assistant Bottom Sheet
// ============================================================

private enum class VoiceState {
    LISTENING,
    RECOGNIZED
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceAssistantBottomSheet(
    sheetState: SheetState,
    onDismiss: () -> Unit,
    onNavigateToPay: () -> Unit
) {
    var voiceState by remember { mutableStateOf(VoiceState.LISTENING) }

    // Auto-advance: LISTENING (2s) → RECOGNIZED (1.5s) → Navigate
    LaunchedEffect(Unit) {
        delay(2000L)
        voiceState = VoiceState.RECOGNIZED
        delay(1500L)
        onNavigateToPay()
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = sheetState,
        containerColor = MaterialTheme.colorScheme.surface,
        shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp),
        tonalElevation = 4.dp
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(24.dp)
        ) {
            // Animated microphone icon
            PulsingMicIcon(isListening = voiceState == VoiceState.LISTENING)

            // State-dependent text
            when (voiceState) {
                VoiceState.LISTENING -> {
                    Text(
                        text = "Listening...",
                        style = MaterialTheme.typography.headlineMedium,
                        color = MaterialTheme.colorScheme.onSurface
                    )
                    AnimatedListeningDots()
                }

                VoiceState.RECOGNIZED -> {
                    Text(
                        text = "I heard:",
                        style = MaterialTheme.typography.titleMedium,
                        color = NeutralGrey
                    )
                    Text(
                        text = "\"Pay 15 Ringgit\"",
                        style = MaterialTheme.typography.headlineLarge,
                        color = OmniOrange,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        text = "Opening scanner...",
                        style = MaterialTheme.typography.bodyLarge,
                        color = NeutralGrey
                    )
                }
            }

            Spacer(Modifier.height(32.dp))
        }
    }
}

// ── Pulsing Mic with expanding ring effect ──────────────────

@Composable
private fun PulsingMicIcon(isListening: Boolean) {
    val infiniteTransition = rememberInfiniteTransition(label = "micPulse")

    val iconScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = if (isListening) 1.15f else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(600, easing = EaseInOutSine),
            repeatMode = RepeatMode.Reverse
        ),
        label = "micScale"
    )

    val ringAlpha by infiniteTransition.animateFloat(
        initialValue = 0.5f,
        targetValue = 0f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseOut),
            repeatMode = RepeatMode.Restart
        ),
        label = "ringAlpha"
    )

    val ringScale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.8f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = EaseOut),
            repeatMode = RepeatMode.Restart
        ),
        label = "ringScale"
    )

    Box(contentAlignment = Alignment.Center) {
        // Expanding sonar ring (only when listening)
        if (isListening) {
            Surface(
                modifier = Modifier
                    .size(96.dp)
                    .scale(ringScale),
                shape = CircleShape,
                color = OmniOrange.copy(alpha = ringAlpha)
            ) {}
        }

        // Main mic circle
        Surface(
            modifier = Modifier
                .size(80.dp)
                .scale(iconScale),
            shape = CircleShape,
            color = if (isListening) OmniOrange else SuccessGreen,
            shadowElevation = 8.dp
        ) {
            Box(contentAlignment = Alignment.Center) {
                Icon(
                    imageVector = Icons.Filled.Mic,
                    contentDescription = "Microphone",
                    tint = Color.White,
                    modifier = Modifier.size(40.dp)
                )
            }
        }
    }
}

// ── Animated "..." dots ─────────────────────────────────────

@Composable
private fun AnimatedListeningDots() {
    val infiniteTransition = rememberInfiniteTransition(label = "dots")

    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        repeat(3) { index ->
            val alpha by infiniteTransition.animateFloat(
                initialValue = 0.3f,
                targetValue = 1f,
                animationSpec = infiniteRepeatable(
                    animation = tween(600, delayMillis = index * 200),
                    repeatMode = RepeatMode.Reverse
                ),
                label = "dot$index"
            )
            Surface(
                modifier = Modifier.size(10.dp),
                shape = CircleShape,
                color = OmniOrange.copy(alpha = alpha)
            ) {}
        }
    }
}
