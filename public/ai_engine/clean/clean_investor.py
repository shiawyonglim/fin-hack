import pandas as pd

# 1. Load the raw data (make sure the filename matches your actual file)
# If the file is a CSV, use this:
df = pd.read_csv('ai_engine/data/investor_alert_list.csv')

# 2. Keep only the columns useful for a search engine
# We want the 'name' and any 'aliases' (other names they go by)
columns_to_keep = ['name', 'aliases', 'countries', 'addresses']
df_clean = df[columns_to_keep].copy()

# 3. Clean up the text
# Remove quotes and extra whitespace that make searching hard
for col in df_clean.columns:
    df_clean[col] = df_clean[col].astype(str).str.replace('"', '').str.strip()

# 4. Handle "empty" values
# Replace 'nan' (empty cells) with an empty string so the AI doesn't get confused
df_clean = df_clean.replace('nan', '')


df_clean.to_csv('ai_engine/data/CLEAN_investor_alert_list.csv', index=False)

print("Category 3 data is ready! Cleaned Investor Alert List saved.")