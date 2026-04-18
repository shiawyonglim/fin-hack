import pandas as pd

df = pd.read_csv('ai_engine/data/paysim_database.csv')

df.columns = [col.lower() for col in df.columns]
df = df.rename(columns={
    'oldbalanceorg': 'old_balance_orig',
    'newbalanceorig': 'new_balance_orig',
    'namedest': 'name_dest',
    'oldbalancedest': 'old_balance_dest',
    'newbalancedest': 'new_balance_dest'
})

df = df.drop(columns=['nameorig'], errors='ignore')

df_cleaned = df[df['type'].isin(['TRANSFER', 'CASH_OUT'])].copy()

df_cleaned.to_csv('ai_engine/data/CLEAN_paysim.csv', index=False)

print("Success! PaySim data is now cleaned and saved in ai_engine/data.")