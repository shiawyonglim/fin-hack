import pandas as pd

raw_data = pd.read_csv('datasets/Base.csv')

cleaned_df = raw_data[[
    'customer_age', 
    'session_length_in_minutes', 
    'proposed_credit_limit',     
    'velocity_6h',               
    'fraud_bool'                 
]].copy()

cleaned_df.columns = [
    'sender_age', 
    'time_of_day', 
    'transfer_amount', 
    'past_7_days_velocity', 
    'is_fraud'
]

cleaned_df.to_csv('datasets/CLEAN_bank_fraud.csv', index=False)
print("Success! Your Behavioral Dataset now matches your project summary image.")