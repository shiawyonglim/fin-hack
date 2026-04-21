import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import onnx
import glob
from onnxruntime.quantization import quantize_dynamic, QuantType, shape_inference

# ==========================================
# 1. SETUP & LOAD
# ==========================================

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🔥 NEURAL NETWORK ENGINE: Firing up on {device.type.upper()}")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: Ensure the dataset is in the correct folder, adjust path if needed
dataset_path = os.path.join(SCRIPT_DIR, "enterprise_finhack_dataset.csv")

print(f"🚀 Loading MASSIVE dataset: {dataset_path} ...")
df = pd.read_csv(dataset_path)

print("Engineering the 18-Feature Enterprise Tensor Matrix...")

# ==========================================
# 2. FEATURE ENGINEERING (18 Features)
# ==========================================
# ── THE FIX: INJECT OVERLAP NOISE ──
# 1. Give 5% of SAFE users a "Rent Payment" behavior (Draining their account normally)
safe_buffers = np.random.uniform(100, 20000, len(df))
rent_day_mask = np.random.rand(len(df)) < 0.05
safe_buffers[rent_day_mask] = np.random.uniform(0, 50, sum(rent_day_mask))

# 2. Give 10% of SCAMMERS a "Sloppy Scammer" behavior (Leaving money behind)
scam_buffers = np.random.uniform(0, 50, len(df))
sloppy_mask = np.random.rand(len(df)) < 0.10
scam_buffers[sloppy_mask] = np.random.uniform(500, 2000, sum(sloppy_mask))

df['oldbalanceOrg'] = np.where(df['isFraud'] == 1, df['amount'] + scam_buffers, df['amount'] + safe_buffers)

df['newbalanceOrig'] = np.where(df['type'] == 'CASH_IN', df['oldbalanceOrg'] + df['amount'], df['oldbalanceOrg'] - df['amount'])
df['newbalanceOrig'] = df['newbalanceOrig'].clip(lower=0)

df['oldbalanceDest'] = np.where(df['isFraud'] == 1, 0.0, np.random.uniform(100, 5000, len(df)))
df['newbalanceDest'] = df['oldbalanceDest'] + df['amount']

df['drain_ratio'] = df['amount'] / df['oldbalanceOrg'].clip(lower=0.01)

# Reconstruct Velocity
df['hour'] = df['step'] % 24
df = df.sort_values(by=['nameOrig', 'step'])
df['daily_transfer_count'] = df.groupby('nameOrig').cumcount()

user_avg = df.groupby('nameOrig')['amount'].transform('mean')
df['amount_vs_average'] = df['amount'] / user_avg.clip(lower=1.0)

# Hardcode Type Encoding so it perfectly matches Javascript
type_mapping = {'CASH_IN': 0, 'CASH_OUT': 1, 'DEBIT': 2, 'PAYMENT': 3, 'TRANSFER': 4}
df['type_encoded'] = df['type'].map(type_mapping)

features = [
    'type_encoded', 'amount', 'oldbalanceOrg', 'newbalanceOrig', 
    'oldbalanceDest', 'newbalanceDest', 'daily_transfer_count', 
    'amount_vs_average', 'hour', 'drain_ratio', 'receiver_inbound_count', 
    'is_new_device', 'is_weekend', 'age_disparity', 'sender_acc_age', 
    'is_round_number', 'receiver_acc_age', 'sender_age'
]

X = df[features].values
y = df['isFraud'].values.reshape(-1, 1)

# ==========================================
# 3. SCALE & SPLIT
# ==========================================
print("Scaling Tensors...")
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)

train_dataset = TensorDataset(torch.FloatTensor(X_train), torch.FloatTensor(y_train))
val_dataset = TensorDataset(torch.FloatTensor(X_test), torch.FloatTensor(y_test))

# Massive batch size for 1.5 million rows
train_loader = DataLoader(train_dataset, batch_size=2048, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=2048)

# ==========================================
# 4. NEURAL NETWORK & LOSS
# ==========================================
class EnterpriseFraudNet(nn.Module):
    def __init__(self, input_size=18):
        super(EnterpriseFraudNet, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, 64),
            nn.BatchNorm1d(64),
            nn.ReLU(),
            nn.Dropout(0.3),
            
            nn.Linear(64, 32),
            nn.BatchNorm1d(32),
            nn.ReLU(),
            nn.Dropout(0.2),
            
            nn.Linear(32, 1) 
        )

    def forward(self, x):
        return self.network(x)

class FocalLoss(nn.Module):
    def __init__(self, alpha=0.85, gamma=2.0):
        super(FocalLoss, self).__init__()
        self.alpha = alpha
        self.gamma = gamma

    def forward(self, inputs, targets):
        bce_loss = F.binary_cross_entropy_with_logits(inputs, targets, reduction='none')
        pt = torch.exp(-bce_loss) 
        return (self.alpha * (1 - pt) ** self.gamma * bce_loss).mean()

model = EnterpriseFraudNet().to(device)
criterion = FocalLoss(alpha=0.85, gamma=2.0).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.005)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=2)

# ==========================================
# 5. TRAINING LOOP
# ==========================================
print("🧠 Training Enterprise Edge Model...")
max_epochs = 50
patience = 5
best_val_loss = float('inf')
patience_counter = 0

best_weights_path = os.path.join(SCRIPT_DIR, "best_enterprise_weights.pth")

for epoch in range(max_epochs):
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device) # <--- ADD THIS
        
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    train_loss = running_loss / len(train_loader)

    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for inputs, labels in val_loader:
            inputs, labels = inputs.to(device), labels.to(device) # <--- ADD THIS
            
            val_outputs = model(inputs)
            val_loss += criterion(val_outputs, labels).item()
    
    val_loss /= len(val_loader)
    current_lr = optimizer.param_groups[0]['lr']
    
    print(f"Epoch [{epoch+1}/{max_epochs}] | LR: {current_lr:.6f} | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    scheduler.step(val_loss)

    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), best_weights_path)
        patience_counter = 0
    else:
        patience_counter += 1
        if patience_counter >= patience:
            print(f"\n🛑 EARLY STOPPING TRIGGERED! The AI peaked {patience} epochs ago.")
            break

# ==========================================
# 6. EXPORT TO ONNX (With Quantization)
# ==========================================
print("Loading the smartest epoch weights for ONNX export...")
model.load_state_dict(torch.load(best_weights_path, weights_only=True))
model.eval()

# Create dummy tensor and move it to the GPU
dummy_input = torch.randn(1, 18).to(device)
onnx_filename = os.path.join(SCRIPT_DIR, "fraud_detection_model.onnx")

torch.onnx.export(model, 
                  dummy_input, 
                  onnx_filename, 
                  export_params=True, 
                  do_constant_folding=True, 
                  input_names=['input'], 
                  output_names=['output'])

print("Consolidating ONNX external resources...")
exported_model = onnx.load(onnx_filename)
onnx.save_model(exported_model, onnx_filename, save_as_external_data=False)

for external_data_file in glob.glob(onnx_filename + ".data"):
    os.remove(external_data_file)

print("Preprocessing ONNX graph to fix PyTorch shape bugs...")
preprocessed_path = os.path.join(SCRIPT_DIR, "fraud_detection_model_prep.onnx")

shape_inference.quant_pre_process(
    input_model_path=onnx_filename,
    output_model_path=preprocessed_path,
    skip_optimization=False
)

print("Quantizing cleaned model for budget Android devices...")
quantized_model_path = os.path.join(SCRIPT_DIR, "fraud_detection_model_quantized.onnx")

quantize_dynamic(
    model_input=preprocessed_path, 
    model_output=quantized_model_path, 
    weight_type=QuantType.QUInt8
)

if os.path.exists(preprocessed_path):
    os.remove(preprocessed_path)

print(f"\n✅ Quantization complete! Models saved to {SCRIPT_DIR}")

# ==========================================
# 7. JAVASCRIPT UI EXPORT
# ==========================================
print("\n" + "="*60)
print("ACTION REQUIRED: COPY THESE 18-FEATURE ARRAYS INTO index.html!")
print(f"const SCALER_MEANS = [{', '.join([str(round(x, 4)) for x in scaler.mean_])}];")
print(f"const SCALER_SCALES = [{', '.join([str(round(x, 4)) for x in scaler.scale_])}];")
print("="*60 + "\n")