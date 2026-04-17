import pdfplumber
import pandas as pd

# 1. Point to your exact PDF path
pdf_path = "./datasets/Investor Alert List _ Securities Commission Malaysia.pdf"
all_data = []

print("Extracting tables page by page using pdfplumber...")

# 2. Open the PDF and loop through the pages
with pdfplumber.open(pdf_path) as pdf:
    for i, page in enumerate(pdf.pages):
        # extract_table() looks for the visual structure rather than strict lines
        table = page.extract_table()
        if table:
            all_data.extend(table)
        
        # Just to print progress so you know it hasn't frozen
        if i % 10 == 0:
            print(f"Processed {i} pages...")

print("Extraction finished! Cleaning data...")

# 3. The first row contains the headers (NAME, DETAILS, REMARKS, YEAR)
if all_data:
    headers = all_data[0]
    rows = all_data[1:]

    df = pd.DataFrame(rows, columns=headers)

    # Clean up PDF line breaks (\n) inside the cells
    df = df.replace('\n', ' ', regex=True)
    
    # Drop rows that are completely empty
    df = df.dropna(how='all')

    # Save to your working directory
    df.to_csv("./datasets/sc_alert_list.csv", index=False)
    print("Success! Conversion complete. Saved as sc_alert_list.csv")
    print(df.head())
else:
    print("Error: Could not find any readable tables in the PDF.")