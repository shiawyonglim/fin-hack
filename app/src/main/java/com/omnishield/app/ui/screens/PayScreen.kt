package com.omnishield.app.ui.screens

import android.Manifest
import androidx.camera.core.CameraSelector
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
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
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.TouchApp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.rememberMultiplePermissionsState
import com.omnishield.app.OmniShieldViewModel
import com.omnishield.app.PaymentResult
import com.omnishield.app.ui.theme.NeutralGrey
import com.omnishield.app.ui.theme.OmniOrange
import com.omnishield.app.ui.theme.OnOmniOrange
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

// ============================================================
// PayScreen — Camera Scanner + Amount Input
// ============================================================

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun PayScreen(
    viewModel: OmniShieldViewModel,
    onNavigateBack: () -> Unit,
    onPaymentSuccess: () -> Unit,
    onPaymentFailed: () -> Unit,
    onFraudAlert: () -> Unit
) {
    val permissionsState = rememberMultiplePermissionsState(
        listOf(
            Manifest.permission.CAMERA,
            Manifest.permission.RECORD_AUDIO
        )
    )

    if (permissionsState.allPermissionsGranted) {
        CameraScannerContent(
            viewModel = viewModel,
            onNavigateBack = onNavigateBack,
            onPaymentSuccess = onPaymentSuccess,
            onPaymentFailed = onPaymentFailed,
            onFraudAlert = onFraudAlert
        )
    } else {
        PermissionGateContent(
            onRequestPermissions = { permissionsState.launchMultiplePermissionRequest() },
            onNavigateBack = onNavigateBack
        )
    }
}

// ============================================================
// Camera Scanner with Mock Scan + Amount Bottom Sheet
// ============================================================

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun CameraScannerContent(
    viewModel: OmniShieldViewModel,
    onNavigateBack: () -> Unit,
    onPaymentSuccess: () -> Unit,
    onPaymentFailed: () -> Unit,
    onFraudAlert: () -> Unit
) {
    var showAmountSheet by remember { mutableStateOf(false) }
    var amountText by remember { mutableStateOf(viewModel.preFillAmount ?: "") }
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val coroutineScope = rememberCoroutineScope()

    // ── Auto-show bottom sheet if voice pre-filled an amount ──
    LaunchedEffect(viewModel.preFillAmount) {
        if (viewModel.preFillAmount != null) {
            amountText = viewModel.preFillAmount ?: ""
            delay(800L) // Brief delay to show camera first
            showAmountSheet = true
        }
    }

    // ── Amount Input Bottom Sheet ────────────────────────────
    if (showAmountSheet) {
        ModalBottomSheet(
            onDismissRequest = {
                if (!viewModel.isProcessing) {
                    showAmountSheet = false
                }
            },
            sheetState = sheetState,
            containerColor = MaterialTheme.colorScheme.surface,
            shape = RoundedCornerShape(topStart = 28.dp, topEnd = 28.dp)
        ) {
            AmountInputSheet(
                amountText = amountText,
                onAmountChange = { amountText = it },
                isProcessing = viewModel.isProcessing,
                onConfirm = {
                    val amount = amountText.toDoubleOrNull()
                    if (amount != null && amount > 0) {
                        coroutineScope.launch {
                            // 1.5s simulated processing delay
                            viewModel.updateProcessingState(true)
                            delay(1500L)
                            viewModel.updateProcessingState(false)

                            // Process payment with ViewModel rules
                            val result = viewModel.processPayment(amount)
                            viewModel.clearPreFillAmount()
                            showAmountSheet = false

                            // Navigate based on result
                            when (result) {
                                PaymentResult.SUCCESS -> onPaymentSuccess()
                                PaymentResult.INSUFFICIENT_FUNDS -> onPaymentFailed()
                                PaymentResult.FRAUD_BLOCKED -> onFraudAlert()
                            }
                        }
                    }
                }
            )
        }
    }

    // ── Main Content: Camera + Overlays ─────────────────────
    Box(modifier = Modifier.fillMaxSize()) {

        // CameraX Preview (full-screen)
        CameraPreviewView(modifier = Modifier.fillMaxSize())

        // Semi-transparent Top Bar
        TopAppBar(
            title = {
                Text(
                    "Scan QR Code",
                    style = MaterialTheme.typography.titleLarge,
                    color = Color.White
                )
            },
            navigationIcon = {
                IconButton(onClick = onNavigateBack) {
                    Icon(
                        Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back",
                        tint = Color.White
                    )
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = Color.Black.copy(alpha = 0.3f)
            )
        )

        // ── "Tap to Simulate Scan" override button ──────────
        Button(
            onClick = { showAmountSheet = true },
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(bottom = 40.dp)
                .height(56.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = OmniOrange,
                contentColor = OnOmniOrange
            ),
            elevation = ButtonDefaults.buttonElevation(defaultElevation = 8.dp)
        ) {
            Icon(
                Icons.Filled.TouchApp,
                contentDescription = null,
                modifier = Modifier.size(24.dp)
            )
            Spacer(Modifier.width(8.dp))
            Text(
                "Tap to Simulate Scan",
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}

// ============================================================
// CameraX Preview (AndroidView wrapper)
// ============================================================

@Composable
@Suppress("DEPRECATION") // LocalLifecycleOwner location
private fun CameraPreviewView(modifier: Modifier = Modifier) {
    val context = LocalContext.current
    val lifecycleOwner = androidx.compose.ui.platform.LocalLifecycleOwner.current

    AndroidView(
        factory = { ctx ->
            val previewView = PreviewView(ctx).apply {
                implementationMode = PreviewView.ImplementationMode.COMPATIBLE
                scaleType = PreviewView.ScaleType.FILL_CENTER
            }

            val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
            cameraProviderFuture.addListener({
                try {
                    val cameraProvider = cameraProviderFuture.get()
                    val preview = Preview.Builder().build().also {
                        it.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    cameraProvider.unbindAll()
                    cameraProvider.bindToLifecycle(
                        lifecycleOwner,
                        CameraSelector.DEFAULT_BACK_CAMERA,
                        preview
                    )
                } catch (_: Exception) {
                    // Camera unavailable (emulator) — fail silently for demo
                }
            }, ContextCompat.getMainExecutor(ctx))

            previewView
        },
        modifier = modifier
    )
}

// ============================================================
// Amount Input Bottom Sheet Content
// ============================================================

@Composable
private fun AmountInputSheet(
    amountText: String,
    onAmountChange: (String) -> Unit,
    isProcessing: Boolean,
    onConfirm: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 24.dp, vertical = 16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(20.dp)
    ) {
        Text(
            text = "Enter Amount",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            color = MaterialTheme.colorScheme.onSurface
        )

        // Numeric amount input
        OutlinedTextField(
            value = amountText,
            onValueChange = onAmountChange,
            modifier = Modifier.fillMaxWidth(),
            label = { Text("Amount (RM)") },
            placeholder = { Text("0.00") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Decimal),
            textStyle = MaterialTheme.typography.headlineLarge,
            singleLine = true,
            enabled = !isProcessing,
            shape = RoundedCornerShape(16.dp)
        )

        // Confirm & Lock Funds button with loading state
        Button(
            onClick = onConfirm,
            modifier = Modifier
                .fillMaxWidth()
                .height(60.dp),
            enabled = amountText.isNotBlank()
                    && amountText.toDoubleOrNull() != null
                    && !isProcessing,
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(
                containerColor = OmniOrange,
                contentColor = OnOmniOrange
            ),
            elevation = ButtonDefaults.buttonElevation(defaultElevation = 4.dp)
        ) {
            if (isProcessing) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = OnOmniOrange,
                    strokeWidth = 3.dp
                )
                Spacer(Modifier.width(12.dp))
                Text(
                    "Processing...",
                    style = MaterialTheme.typography.titleLarge
                )
            } else {
                Icon(
                    Icons.Filled.Lock,
                    contentDescription = null,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(Modifier.width(8.dp))
                Text(
                    "Confirm & Lock Funds",
                    style = MaterialTheme.typography.titleLarge
                )
            }
        }

        Spacer(Modifier.height(16.dp))
    }
}

// ============================================================
// Permission Gate — Graceful camera/audio request
// ============================================================

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun PermissionGateContent(
    onRequestPermissions: () -> Unit,
    onNavigateBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        "Camera Permission",
                        style = MaterialTheme.typography.titleLarge
                    )
                },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = Color.Transparent
                )
            )
        },
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
            Icon(
                Icons.Filled.CameraAlt,
                contentDescription = null,
                modifier = Modifier.size(80.dp),
                tint = NeutralGrey
            )

            Spacer(Modifier.height(24.dp))

            Text(
                text = "Camera Access Required",
                style = MaterialTheme.typography.headlineMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onBackground
            )

            Spacer(Modifier.height(12.dp))

            Text(
                text = "We need camera and microphone access\nto scan QR codes and use voice commands.",
                style = MaterialTheme.typography.bodyLarge,
                color = NeutralGrey,
                textAlign = TextAlign.Center
            )

            Spacer(Modifier.height(32.dp))

            Button(
                onClick = onRequestPermissions,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(56.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(
                    containerColor = OmniOrange,
                    contentColor = OnOmniOrange
                )
            ) {
                Text(
                    "Grant Permissions",
                    style = MaterialTheme.typography.titleLarge
                )
            }
        }
    }
}
