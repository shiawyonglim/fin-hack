import pandas as pd
import numpy as np
import random
import time

print("Booting MASSIVE Enterprise Behavioral Matrix (Target: 1.5M+ Rows)...")
start_time = time.time()

# ── 1. MASSIVE USER BASE ──
NUM_NORMAL_USERS = 50000 
NUM_SCAMMERS = 2000
data = []

print(f"Generating identities for {NUM_NORMAL_USERS} users and {NUM_SCAMMERS} scammers...")
user_catalog = {}
for i in range(1, NUM_NORMAL_USERS + 1):
    uid = f"USER_{i}"
    user_catalog[uid] = {
        'age': random.randint(18, 80), 
        'acc_age': random.randint(300, 4000) 
    }

scam_catalog = {}
for i in range(1, NUM_SCAMMERS + 1):
    sid = f"SCAM_{i}"
    scam_catalog[sid] = {
        'age': random.randint(18, 30), 
        'acc_age': random.randint(1, 7) 
    }

user_ids = list(user_catalog.keys())
scammer_ids = list(scam_catalog.keys())

# Highly optimized dictionary for tracking Money Mules
receiver_history = {uid: [] for uid in user_ids + scammer_ids}

def get_inbound_count(receiver_id, current_step):
    history = receiver_history[receiver_id]
    recent = [s for s in history if s > current_step - 24]
    receiver_history[receiver_id] = recent 
    return len(recent)

# ── 2. SCALED BASELINE BEHAVIOR (1.44 Million Rows) ──
TOTAL_STEPS = 720 # 30 Days of continuous simulation
TXNS_PER_HOUR = 2000

print(f"Injecting Safe Baseline: Simulating {TOTAL_STEPS} hours at {TXNS_PER_HOUR} txns/hour...")
for step in range(1, TOTAL_STEPS + 1):
    if step % 100 == 0:
        print(f"  -> Simulating Hour {step}/{TOTAL_STEPS}...")
        
    for _ in range(TXNS_PER_HOUR): 
        sender = random.choice(user_ids)
        receiver = random.choice(user_ids)
        
        amount = round(random.uniform(10, 800), 2)
        txn_type = random.choices(['PAYMENT', 'TRANSFER', 'CASH_IN', 'CASH_OUT', 'DEBIT'], weights=[0.4, 0.2, 0.2, 0.1, 0.1])[0]
        
        s_age = user_catalog[sender]['age']
        r_age = user_catalog[receiver]['age']
        
        is_weekend = 1 if (step % 168) >= 120 else 0
        is_new_device = 0 
        is_round_number = 1 if amount % 100 == 0 else 0
        age_disparity = abs(s_age - r_age)
        
        data.append([
            step, txn_type, amount, sender, user_catalog[sender]['acc_age'], s_age,
            receiver, user_catalog[receiver]['acc_age'], r_age,
            is_new_device, is_weekend, is_round_number, age_disparity, get_inbound_count(receiver, step), 0
        ])
        receiver_history[receiver].append(step)

# ── 3. SCALED ZERO-DAY VECTORS (80,000 Fraud Rows) ──
print("Injecting 80,000 Advanced Criminal Fingerprints...")

# Vector 1: Account Takeovers (20,000 instances)
for _ in range(20000):
    step = random.randint(50, TOTAL_STEPS)
    is_weekend = 1 if (step % 168) >= 120 else 0
    victim = random.choice(user_ids)
    scammer = random.choice(scammer_ids)
    s_age, r_age = user_catalog[victim]['age'], scam_catalog[scammer]['age']
    
    data.append([
        step, 'TRANSFER', float(random.choice([5000, 10000, 15000])), 
        victim, user_catalog[victim]['acc_age'], s_age,
        scammer, scam_catalog[scammer]['acc_age'], r_age,
        1, is_weekend, 1, abs(s_age - r_age), get_inbound_count(scammer, step), 1
    ])
    receiver_history[scammer].append(step)

# Vector 2: Grandparent Scams (20,000 instances)
elderly_pool = [u for u in user_ids if user_catalog[u]['age'] > 65]
for _ in range(20000):
    step = random.randint(50, TOTAL_STEPS)
    is_weekend = 1 if (step % 168) >= 120 else 0
    victim = random.choice(elderly_pool)
    scammer = random.choice(scammer_ids)
    
    data.append([
        step, 'TRANSFER', float(random.choice([2000, 5000, 8000])), 
        victim, user_catalog[victim]['acc_age'], user_catalog[victim]['age'],
        scammer, scam_catalog[scammer]['acc_age'], scam_catalog[scammer]['age'],
        0, is_weekend, 1, abs(user_catalog[victim]['age'] - scam_catalog[scammer]['age']), get_inbound_count(scammer, step), 1
    ])
    receiver_history[scammer].append(step)

# Vector 3: Money Mules (4,000 rings x 10 victims = 40,000 instances)
for _ in range(4000):
    step = random.randint(50, TOTAL_STEPS)
    is_weekend = 1 if (step % 168) >= 120 else 0
    mule = random.choice(scammer_ids)
    
    for _ in range(10):
        mule_victim = random.choice(user_ids)
        data.append([
            step, 'TRANSFER', round(random.uniform(500, 2000), 2), 
            mule_victim, user_catalog[mule_victim]['acc_age'], user_catalog[mule_victim]['age'],
            mule, scam_catalog[mule]['acc_age'], scam_catalog[mule]['age'],
            0, is_weekend, 0, abs(user_catalog[mule_victim]['age'] - scam_catalog[mule]['age']), get_inbound_count(mule, step), 1
        ])
        receiver_history[mule].append(step)

# ── 4. COMPILE AND EXPORT ──
print("Compiling massive Pandas DataFrame... (this may take a moment)")
columns = [
    'step', 'type', 'amount', 'nameOrig', 'sender_acc_age', 'sender_age',
    'nameDest', 'receiver_acc_age', 'receiver_age',
    'is_new_device', 'is_weekend', 'is_round_number', 'age_disparity', 
    'receiver_inbound_count', 'isFraud'
]

df = pd.DataFrame(data, columns=columns)
df = df.sort_values(by=['step']).reset_index(drop=True)

output_file = "enterprise_finhack_dataset.csv"
print("Writing 1.5M+ rows to CSV...")
df.to_csv(output_file, index=False)

end_time = time.time()
print(f"✅ MEGA DATASET CREATED: '{output_file}'")
print(f"Total Rows: {len(df)}")
print(f"Time Taken: {round(end_time - start_time, 1)} seconds")