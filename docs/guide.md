🛡️ FRAUD DETECTION GUIDE: Zero-Trust Edge Architecture
This is the official engineering guide and architectural blueprint for the Hackathon Fraud Detection Engine. It outlines how the system operates entirely offline on Android devices using a combination of edge-optimized AI and hardcoded deterministic rules.

Share this document with your Android Developer, UI/UX Designer, and use it as your script for the judges' pitch.

🧠 1. The 10-Feature Input Matrix
The core of the AI is a PyTorch-trained Neural Network that has been converted into a highly compressed ONNX Int8 model. For the AI to make a prediction, the Android frontend must pass exactly 10 numerical features in this precise order:

Transaction Type: Encoded integer (0=CASH_IN, 1=CASH_OUT, 2=DEBIT, 3=PAYMENT, 4=TRANSFER).

Amount: The raw transaction value (e.g., 50.0).

Sender Old Balance: Total balance before transfer.

Sender New Balance: Total balance after transfer (Old - Amount).

Receiver Old Balance: Always pass 0.0 (Offline edge privacy constraint).

Receiver New Balance: Pass the Amount (Approximation).

Hour of Day: The current local hour (0 to 23).

Balance Drain Ratio: Amount / Sender Old Balance (e.g., 0.95 means transferring 95% of wealth).

Daily Transfer Count (Velocity): Number of transactions the user has made in the last 24 hours.

Amount vs Average (Velocity): Current Amount / Historical Average Amount (e.g., a 10.0 ratio means a massive, unusual spike).

🛡️ 2. The Two-Tiered Defense System
The system does not rely on a "black box" AI. It uses a dual-engine approach to ensure 100% explainability (XAI) and absolute safety.

Tier 1: Deterministic Rule Engine (The Guardrails)
Before the AI even looks at the transaction, the rule engine runs strict, hardcoded mathematical checks. If any of these fail, the transaction is instantly blocked, and a plain-text ComplianceLog is generated for the user interface.

Scammer Database Lookup: Offline CSV/JSON check against the BNM FCA and SC Investor Alert List.

Time Anomalies: Blocks high-risk accounts (Elderly/Children) from transferring money between midnight and 6:00 AM.

Balance Drain Protection: Blocks Elderly accounts from transferring >80% of their total balance in a single transaction.

Hard Limits: Enforces maximum transaction limits based on the user's self-evaluated category (Child, Adult, Elderly).

Tier 2: The Edge AI Neural Network (Zero-Day Defense)
If the transaction passes the deterministic rules, it enters the ONNX AI model.

What it does: It hunts for "Zero-Day" scammers—fraudsters who created accounts yesterday and are not yet on the government blacklist.

How it works: It analyzes the velocity and behavioral features (e.g., a sudden 100x spike in transfer size combined with a high balance drain ratio).

Output: It returns a Fraud Probability (0.0 to 1.0). Scores above 0.5 trigger an AI Block.

📱 3. The Android Execution Pipeline
The entire transaction flow happens locally on the tablet. Your Android Developer must implement this exact sequence:

Voice Detection (Native OS): The user speaks (e.g., "Tolong transfer fifty ringgit to Uncle Muthu"). Android's native SpeechRecognizer (configured to en-MY for Bahasa Rojak) transcribes the audio into text instantly offline.

Intent Parsing (Regex): Kotlin Regex scripts extract the Amount (50) and Target (Uncle Muthu) from the transcribed text in milliseconds. Avoid heavy NLP tokenizers.

Scaler Math: Neural networks hate large numbers. The Kotlin app must subtract the SCALER_MEANS and divide by the SCALER_SCALES for all 10 features to match how the Python model was trained.

ONNX Inference: The scaled 10-number array is passed into fraud_detection_model_quantized.onnx using the onnxruntime-android library.

UI & Audio Feedback: * If Safe: Screen flashes Green. Native Text-to-Speech (TTS) says, "Transfer successful."

If Blocked: Screen flashes Red with a Stop Sign icon. The exact reason from the ComplianceLog is displayed, and TTS reads the warning out loud to assist elderly users.

⚙️ 4. The Model Generation Pipeline (Python Backend)
If you need to retrain the AI because the dataset changed, run train_fraud_detection.py on your PC. The pipeline executes automatically:

Feature Engineering: Sorts the data chronologically and calculates the velocity and drain ratios.

Data Balancing: Uses BCEWithLogitsLoss and calculates positive class weights so the AI learns from the massive legitimate dataset without ignoring the rare fraud cases.

Auto-Epoch Training: Uses Early Stopping with a patience of 4 to find the exact mathematical peak of the model without overfitting.

ONNX Export & Preprocessing: Translates the PyTorch weights to an ONNX graph and scrubs out dirty Dynamo shape metadata.

Int8 Quantization: Compresses the 32-bit model into an 8-bit .onnx file, shrinking it by 4x to ensure it runs instantly on older, budget Android tablets.

🎤 5. Pitch Strategy (Key Buzzwords)
When presenting to the hackathon judges, heavily index on these enterprise-grade concepts:

Zero-Trust Edge AI: "Our entire fraud engine runs locally on the user's device. No cloud latency, no server costs, and complete privacy."

Explainable AI (XAI): "We solved the 'Black Box' problem. Our deterministic rule engine outputs exact plain-text logs explaining why a transaction was blocked."

Zero-Day Behavioral Defense: "Our velocity tracking catches scammers based on behavior before they are even added to government blacklists."

Inclusive Offline Design: "Using ONNX Int8 Quantization, native Bahasa Rojak speech recognition, and Text-to-Speech, we ensure top-tier AI security is accessible to elderly users on budget devices without internet access."
