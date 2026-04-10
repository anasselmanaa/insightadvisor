import pandas as pd
from cleaning import clean_dataframe

df = pd.read_csv("data/sample_dataset.csv")

cleaned_df, report = clean_dataframe(df)

print("CLEANED SHAPE:", cleaned_df.shape)
print("\nREPORT:")
for k, v in report.items():
    print(k, ":", v)