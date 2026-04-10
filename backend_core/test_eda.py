import pandas as pd
from pprint import pprint
from eda import generate_eda_report

df = pd.read_csv("data/sample_dataset.csv")
eda_report = generate_eda_report(df)

print("EDA Report:")
pprint(eda_report, width=120, sort_dicts=False)