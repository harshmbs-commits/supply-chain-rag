import pandas as pd

df = pd.read_csv('SCMS_Delivery_History_Dataset.csv')

print("Total Rows: ", len(df))
print("Total Columns: ", len(df.columns))
print("\ncolumn names:")
print(df.columns.tolist())
print("\nFirst 3 rows:")
print(df.head(3))