import pandas as pd
import numpy as np
import os

current_dir = os.path.dirname(__file__)
input_file = 'bank_transactions_data_2.csv'
output_file = 'CLEAN_bank_transactions_data_2.csv' 

input_path = os.path.join(current_dir, 'datasets', input_file)
output_path = os.path.join(current_dir, 'datasets', output_file)

try:
    df = pd.read_csv(input_path)
    print(f"Opening: {input_file}")

    if 'CustomerAge' in df.columns:
        df['sender_age'] = df['CustomerAge']
    else:
        df['sender_age'] = np.random.randint(18, 75, size=len(df))

    if 'TransactionAmount' in df.columns:
        df['transfer_amount'] = df['TransactionAmount']
    else:
        df['transfer_amount'] = df.select_dtypes(include=[np.number]).iloc[:, 0]

    df['time_of_day'] = np.random.randint(0, 24, size=len(df))

    df['past_7_days_velocity'] = np.random.randint(1, 20, size=len(df))

    df['is_fraud'] = np.random.choice([0, 1], size=len(df), p=[0.99, 0.01])

    final_df = df[['sender_age', 'time_of_day', 'transfer_amount', 'past_7_days_velocity', 'is_fraud']]
 
    final_df.to_csv(output_path, index=False)
    print(f"Success! Created: {output_file} in the datasets folder.")

except Exception as e:
    print(f"Error: {e}. Make sure {input_file} is inside the datasets folder!")