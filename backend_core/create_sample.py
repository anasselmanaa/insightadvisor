import pandas as pd


df = pd.read_csv('data/online_retail.csv')


print('Full shape:', df.shape)

sample = df.sample(n=200000, random_state=42)

sample.to_csv('data/sample_dataset.csv', index=False)

print('Sample saved:', sample.shape)
