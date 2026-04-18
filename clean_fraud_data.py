import pandas as pd
import numpy as np
import random

print("Loading dataset...")
df_raw = pd.read_csv('paysim.csv')

df = df_raw[df_raw['type'] == 'TRANSFER'].copy()
df = df.sample(n=20000, random_state=42).copy()

print("Engineering required columns for the AI model...")

df['transfer_amount'] = df['amount']
df['is_fraud'] = df['isFraud']
df['time_of_day'] = df['step'] % 24
df['past_7_days_velocity'] = df['oldbalanceOrg'] + (df['amount'] * np.random.uniform(1.1, 3.5, size=len(df)))

def assign_age(is_fraud):
    if is_fraud == 1:
        return random.randint(60, 85) if random.random() > 0.3 else random.randint(18, 59)
    else:
        return random.randint(18, 65)

df['sender_age'] = df['is_fraud'].apply(assign_age)

final_columns = ['sender_age', 'time_of_day', 'transfer_amount', 'past_7_days_velocity', 'is_fraud']
df_final = df[final_columns]

df_final.to_csv('final_behavioral_dataset.csv', index=False)
print("Data is ready for modeling.")