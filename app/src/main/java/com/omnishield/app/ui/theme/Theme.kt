package com.omnishield.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

// ============================================================
// Omni-Shield MD3 Theme — Light-only, Orange primary, Kanso
// ============================================================

private val OmniShieldColorScheme = lightColorScheme(
    primary = OmniOrange,
    onPrimary = OnOmniOrange,
    primaryContainer = OmniOrangeContainer,
    onPrimaryContainer = OnOmniOrangeContainer,
    secondary = OmniOrange,
    onSecondary = OnOmniOrange,
    background = NeutralWhite,
    onBackground = NeutralBlack,
    surface = NeutralWhite,
    onSurface = NeutralBlack,
    surfaceVariant = NeutralLightGrey,
    onSurfaceVariant = NeutralGrey,
    error = ErrorDeepRed,
    onError = OnError,
    errorContainer = ErrorRedContainer,
)

@Composable
fun OmniShieldTheme(
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = OmniShieldColorScheme,
        typography = OmniTypography,
        content = content
    )
}
