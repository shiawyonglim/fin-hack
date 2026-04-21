package com.omnishield.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.navigation.compose.rememberNavController
import com.omnishield.app.navigation.OmniShieldNavGraph
import com.omnishield.app.ui.theme.OmniShieldTheme

// ============================================================
// MainActivity — Single entry point, edge-to-edge, Compose only
// ============================================================

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            OmniShieldTheme {
                val navController = rememberNavController()
                OmniShieldNavGraph(navController = navController)
            }
        }
    }
}
