import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report
import os

print("Loading dataset...")
# Load only a subset to save time during the hackathon / fast prototyping
df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/paysim_database.csv'), nrows=700000)

print("Feature Engineering & Preprocessing data...")

# CRITICAL: Sort by user and time (step) FIRST so velocity math works
df = df.sort_values(by=['nameOrig', 'step'])

# --- NEW: ADVANCED VELOCITY FEATURES ---
print("Calculating velocity features...")

# 1. daily_transfer_count: How many transactions has this user done so far?
df['daily_transfer_count'] = df.groupby('nameOrig').cumcount()

# 2. amount_vs_average: Current amount divided by their typical amount
# (Using transform('mean') for hackathon compilation speed)
user_avg_amount = df.groupby('nameOrig')['amount'].transform('mean')
df['amount_vs_average'] = np.where(user_avg_amount > 0, df['amount'] / user_avg_amount, 1.0)

# --- EXISTING BEHAVIORAL FEATURES ---
df['hour_of_day'] = df['step'] % 24
df['balance_drain_ratio'] = np.where(df['oldbalanceOrg'] > 0, df['amount'] / df['oldbalanceOrg'], 0)

# Convert categorical 'type' to numerical
label_encoder = LabelEncoder()
df['type'] = label_encoder.fit_transform(df['type'])

# We now have 10 Features total!
X = df.drop(columns=['step', 'nameOrig', 'nameDest', 'isFlaggedFraud', 'isFraud']).values
y = df['isFraud'].values

# Split data into train and test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# PRINT SCALERS FOR THE JAVASCRIPT UI!
print("\n" + "="*50)
print("ACTION REQUIRED: COPY THESE ARRAYS INTO ENGINE/UI!")
print(f"const SCALER_MEANS = [{', '.join([str(round(x, 4)) for x in scaler.mean_])}];")
print(f"const SCALER_SCALES = [{', '.join([str(round(x, 4)) for x in scaler.scale_])}];")
print("="*50 + "\n")

# Convert to PyTorch tensors
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

# Create DataLoader
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
train_loader = DataLoader(train_dataset, batch_size=64, shuffle=True)

# 3. UPGRADED NEURAL NETWORK ARCHITECTURE
# Added deeper layers, Batch Normalization to stabilize fast inputs, and Dropout to prevent overfitting
num_legit = len(df[df['isFraud'] == 0])
num_fraud = len(df[df['isFraud'] == 1])
weight = torch.tensor([num_legit / max(num_fraud, 1)], dtype=torch.float32)

class FraudDetectionNet(nn.Module):
    def __init__(self, input_size):
        super(FraudDetectionNet, self).__init__()
        self.fc1 = nn.Linear(input_size, 64)
        self.bn1 = nn.BatchNorm1d(64)
        self.relu1 = nn.ReLU()
        self.drop1 = nn.Dropout(0.2)
        
        self.fc2 = nn.Linear(64, 32)
        self.bn2 = nn.BatchNorm1d(32)
        self.relu2 = nn.ReLU()
        self.drop2 = nn.Dropout(0.2)
        
        self.fc3 = nn.Linear(32, 1)
        # REMOVED Sigmoid() here because BCEWithLogitsLoss handles it automatically and safely!

    def forward(self, x):
        out = self.drop1(self.relu1(self.bn1(self.fc1(x))))
        out = self.drop2(self.relu2(self.bn2(self.fc2(out))))
        out = self.fc3(out)
        return out

input_size = X_train.shape[1]
model = FraudDetectionNet(input_size)

# 1. The 1-Line Fix: Upgraded Loss Function
criterion = nn.BCEWithLogitsLoss(pos_weight=weight)
optimizer = optim.Adam(model.parameters(), lr=0.0005)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'min', patience=2, factor=0.5)

# --- AUTO-EPOCH: EARLY STOPPING ---
max_epochs = 100  # Set a massive ceiling, the AI will stop itself long before this
patience = 4      # How many epochs to wait if it stops improving
best_val_loss = float('inf')
patience_counter = 0

print("Training the robust edge model with Auto-Epoch (Early Stopping)...")

for epoch in range(max_epochs):
    # 1. Train the model
    model.train()
    running_loss = 0.0
    for inputs, labels in train_loader:
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()
    
    train_loss = running_loss / len(train_loader)

    # 2. Test the model (Validation Phase)
    model.eval()
    with torch.no_grad():
        val_outputs = model(X_test_tensor)
        val_loss = criterion(val_outputs, y_test_tensor).item()
    
    print(f"Epoch [{epoch+1}/{max_epochs}] | Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")

    # 3. The "Smart Stopping" Logic
    if val_loss < best_val_loss:
        # The AI got smarter! Save this exact version.
        best_val_loss = val_loss
        patience_counter = 0
        torch.save(model.state_dict(), "best_hackathon_weights.pth")
    else:
        # The AI didn't improve. Increase the patience counter.
        patience_counter += 1
        if patience_counter >= patience:
            print(f"\n🛑 EARLY STOPPING TRIGGERED! The AI peaked {patience} epochs ago.")
            break

# 4. CRITICAL: Load the absolute best version of the brain back into the model before exporting to ONNX!
print("Loading the smartest epoch weights for ONNX export...")
model.load_state_dict(torch.load("best_hackathon_weights.pth", weights_only=True))

print("Exporting resilient model to ONNX...")
model.eval()
dummy_input = torch.randn(1, input_size) 
onnx_filename = os.path.join(os.path.dirname(__file__), "../models/fraud_detection_model.onnx")

# FIX: Removed dynamic_axes. We lock the batch size to exactly 1 for edge inference.
# FIX: Removed opset_version so PyTorch auto-selects the best modern version.
torch.onnx.export(model, 
                  dummy_input, 
                  onnx_filename, 
                  export_params=True, 
                  do_constant_folding=True, 
                  input_names=['input'], 
                  output_names=['output'])

# Merge the potentially split external .data files
import onnx
import glob
print("Consolidating ONNX external resources...")
exported_model = onnx.load(onnx_filename)
onnx.save_model(exported_model, onnx_filename, save_as_external_data=False)

for external_data_file in glob.glob(onnx_filename + ".data"):
    os.remove(external_data_file)

print(f"Model successfully exported to {onnx_filename}!")

from onnxruntime.quantization import quantize_dynamic, QuantType, shape_inference

print("Preprocessing ONNX graph to fix PyTorch shape bugs...")
preprocessed_path = os.path.join(os.path.dirname(__file__), "../models/fraud_detection_model_prep.onnx")

# Step A: Scrub the dirty metadata
shape_inference.quant_pre_process(
    input_model_path=onnx_filename,
    output_model_path=preprocessed_path,
    skip_optimization=False
)

print("Quantizing cleaned model for budget Android devices...")
quantized_model_path = os.path.join(os.path.dirname(__file__), "../models/fraud_detection_model_quantized.onnx")

# Step B: Quantize the CLEANED model (Notice model_input is now preprocessed_path)
quantize_dynamic(
    model_input=preprocessed_path, 
    model_output=quantized_model_path, 
    weight_type=QuantType.QUInt8
)

# Optional cleanup: Delete the temporary preprocessed file to keep your folder clean
if os.path.exists(preprocessed_path):
    os.remove(preprocessed_path)

print(f"Quantization complete! Both normal and quantized models saved.")