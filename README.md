# FinHack: Zero-Trust Edge Fraud Protection & Offline Mesh

An advanced, edge-computing financial application prototyped for the **TNG FinHack**. This application rethinks traditional finance apps by decentralizing core security protocols directly to the edge (the user's device) and enabling true offline money transfers. 

---

## 🌟 Core Concepts

- **Edge Fraud Detection (ONNX Runtime):** A "Stripe Radar"-style neural network running entirely locally. It evaluates fraud probability the millisecond a transfer starts without any cloud latency. If an anomaly is detected, it instantly drops down to a deterministic, white-box rule engine that provides plain-text compliance logs.
- **Offline Mesh Network:** Move money without the internet. When paying, the sender's phone cryptographically signs a receipt with a private digital key. This block bounces from phone to phone (acting as blind relays) via localized connections. The first device to connect to Wi-Fi uploads the ledger.
- **Voice-Activated Accessibility (Whisper-Tiny):** Designed primarily for elderly users who struggle with complex UIs. Users tap to speak in natural language (including *Bahasa Rojak*), and an offline AI parses their intent to automate the transfer forms.

---

## 🛠️ Technology Stack

**Local Training Pipeline**
- Python 3.11, PyTorch (`torch`), ONNX (`onnx`), Scikit-Learn, Pandas

**Edge Frontend (Client-Side)**
- Native Android / Svelte + Vite
- ONNX Runtime Edge / Web (`onnxruntime-web`)
- IndexedDB API

**Backend Server (Command Center)**
- FastAPI & Uvicorn (`uvicorn[standard]`)
- PyNaCl (`pynacl`) for Cryptography
- Oceanbase (Database), Docker, Alibaba Cloud & AWS Infrastructure

---

## 🔄 The User Experience (UX) Pipeline

1. **The Trigger: Voice Recognition** 
   A persistent "Microphone" button on the Home Screen. The user taps and holds to speak (e.g., *"Sila transfer liang bai wu shi kuai to Mr. Loy"*). Whisper-Tiny processes the audio offline.
2. **The UI Handoff (The Voice Router)** 
   The app automatically jumps to the transfer screen and fills the parameters: *Recipient: Mr. Loy, Amount: RM 250.00*. Text-to-Speech confirms the action to the user out loud.
3. **The Security Gate (WebAuthn)** 
   Instead of a traditional PIN, the app prompts FaceID / TouchID. The hardware verifies identity seamlessly.
4. **The Invisible Shield (Fraud Detection)** 
   Sitting exactly between FaceID and the final payment, the ONNX model analyzes the transaction data context (e.g., RM 250, 2:00 AM, Elderly Account). 
   - *If Safe:* Continues immediately.
   - *If Fraud:* The UI turns red, printing a terminal-style log: `[SYSTEM: ABNORMAL VELOCITY DETECTED. TRANSFER BLOCKED.]`
5. **The Vault (Offline Mesh Network)** 
   If there is no internet, the app writes: *"Transaction Signed & Queued."* A dynamic QR code representing the encrypted block is generated via `libsodium` and IndexedDB. It can be physically scanned by the receiver to complete the local ledger handover.

---

## 🛡️ Deep Dive: Security & AI Features

### 1. ONNX Fraud Engine & Self-Evaluation
- **Self-Evaluation:** The system categorizes the user based on history (e.g., Child, Adult, Elderly, Potential Scammer). Protection rules adjust automatically. For instance: elderly accounts face stricter time-transfer constraints but have easier money-back protocols.
- **Rules Engine Execution:** Detects hard boundaries like high-stake velocity (e.g., transfers `> 1000` occurring back-to-back), or stops elderly users from liquidating `90%` of their balance at 2 AM.
- **Zero-Trust Edge:** The sender's phone only evaluates the *sender's* behavior and checks the receiver against a local, offline database. It never inherently "trusts" the receiver's phone.

### 2. Scammer Database Matching
- Pre-caches well-known scammer lists when the phone connects to WiFi.
- References the **BNM Financial Consumer Alert (FCA) List** and the **Securities Commission (SC) Investor Alert List**. Matches block transfers instantly without a network call.

### 3. Asymmetric Offline Validation
- Decentralized Validation: The offline receipt has one main encrypted core and multiple validation keys. 
- Blind Relays: Bystanders in the mesh network act as couriers holding the encrypted ciphertext without being able to read the sender, receiver, or financial amount.
- Limit: Maximum 200 quota for offline transfers. Only 2 relays are required to validate a transfer, with the online server cross-validating 10 later.

---

## 👥 The Team & Roles

- **Integration Engineer:** Integrate and test components *(Khee En)*
- **AI Engineer:** ONNX models and pipeline *(Rap)*
- **Pitcher & Slide Deck:** Present the core vision *(Log Ming Ming)*
- **Backend Developer:** Python FastAPI and HTTP control *(Ong Zi Xuan)*
- **Data Engineer:** Locate datasets, clean data, and text fixtures *(Amber)*
