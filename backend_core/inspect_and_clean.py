import pandas as pd

# Load the sample dataset
df = pd.read_csv("data/sample_dataset.csv")

print("Shape:", df.shape)
print("\nColumns:")
print(list(df.columns))

print("\nData types:")
print(df.dtypes)

print("\nMissing values per column:")
print(df.isna().sum())

print("\nDuplicate rows:", df.duplicated().sum())

# Convert InvoiceDate to datetime
if "InvoiceDate" in df.columns:
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"], errors="coerce")

# Create Revenue column
if "Quantity" in df.columns and "UnitPrice" in df.columns:
    df["Revenue"] = df["Quantity"] * df["UnitPrice"]

print("\nAfter conversions:")
print(df.dtypes)

if "Revenue" in df.columns:
    print("\nRevenue preview:")
    print(df["Revenue"].head())