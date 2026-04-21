import pandas as pd
import numpy as np
import os

print("🧬 Initiating Enterprise-Paysim Fusion...")

# 1. BULLETPROOF DIRECTORY SETUP
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, '..', 'data')

synth_path = os.path.join(DATA_DIR, "enterprise_finhack_dataset.csv")
paysim_path = os.path.join(DATA_DIR, "paysim_database.csv")

# 2. LOAD DATASETS
print(f"Loading synthetic 1.5M Matrix from: {synth_path}")
df_synth = pd.read_csv(synth_path)

print(f"Loading Paysim Database from: {paysim_path}")
df_paysim = pd.read_csv(paysim_path)

# Extract ALL real fraud, but only sample 200,000 safe rows to protect your RAM
paysim_fraud = df_paysim[df_paysim['isFraud'] == 1]
paysim_safe = df_paysim[df_paysim['isFraud'] == 0].sample(n=200000, random_state=42)
df_paysim_sampled = pd.concat([paysim_fraud, paysim_safe])

print(f"Extracted {len(paysim_fraud)} real fraud and {len(paysim_safe)} real safe transactions from Paysim.")

# ... (Continue with the rest of the script: GRAFT THE 8 MISSING FEATURES ONTO PAYSIM)
# 3. GRAFT THE 8 MISSING FEATURES ONTO PAYSIM
print("Upgrading Paysim to the 18-Feature Standard...")

num_rows = len(df_paysim_sampled)

# Give them realistic ages and account ages
df_paysim_sampled['sender_acc_age'] = np.random.randint(100, 4000, num_rows)
df_paysim_sampled['sender_age'] = np.random.randint(18, 80, num_rows)
df_paysim_sampled['receiver_acc_age'] = np.random.randint(100, 4000, num_rows)
df_paysim_sampled['receiver_age'] = np.random.randint(18, 80, num_rows)

# Calculate the new math columns
df_paysim_sampled['is_new_device'] = 0 # Assume normal devices for Paysim
df_paysim_sampled['is_weekend'] = np.where((df_paysim_sampled['step'] % 168) >= 120, 1, 0)
df_paysim_sampled['is_round_number'] = np.where(df_paysim_sampled['amount'] % 100 == 0, 1, 0)
df_paysim_sampled['age_disparity'] = abs(df_paysim_sampled['sender_age'] - df_paysim_sampled['receiver_age'])
df_paysim_sampled['receiver_inbound_count'] = np.random.randint(0, 3, num_rows) # Normal velocity

# Ensure column names exactly match your synthetic dataset
paysim_aligned = df_paysim_sampled[[
    'step', 'type', 'amount', 'nameOrig', 'sender_acc_age', 'sender_age',
    'nameDest', 'receiver_acc_age', 'receiver_age',
    'is_new_device', 'is_weekend', 'is_round_number', 'age_disparity', 
    'receiver_inbound_count', 'isFraud'
]]

# 4. THE GRAND FUSION
print("Fusing datasets...")
df_master = pd.concat([df_synth, paysim_aligned], ignore_index=True)

# Shuffle the data so PyTorch doesn't learn them in separate chunks
df_master = df_master.sample(frac=1, random_state=42).reset_index(drop=True)

output_name = "OMNI_finhack_dataset.csv"
df_master.to_csv(output_name, index=False)

print("\n" + "="*50)
print(f"✅ OMNI DATASET CREATED: {output_name}")
print(f"Total Rows: {len(df_master)}")
print(f"Total Fraud: {len(df_master[df_master['isFraud'] == 1])}")
print("="*50)