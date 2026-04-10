import pandas as pd
from cleaning import clean_dataframe
from eda import generate_eda_report
import json

# 1. Load data
df = pd.read_csv("data/sample_dataset.csv")

print("Original shape:", df.shape)

# 2. Clean data
cleaned_df, cleaning_report = clean_dataframe(df)

print("After cleaning:", cleaned_df.shape)

# 3. Run EDA
eda_report = generate_eda_report(cleaned_df)

# 4. Save cleaned dataset
cleaned_df.to_csv("data/cleaned_dataset.csv", index=False)

# 5. Save reports
with open("cleaning_report.json", "w") as f:
    json.dump(cleaning_report, f, indent=4)

with open("eda_report.json", "w") as f:
    json.dump(eda_report, f, indent=4)

print("Pipeline finished successfully.")