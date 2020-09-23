import pandas as pd

df = pd.read_excel("uds_test.xlsx",sheet_name="1_1_DiagAndCommMgtFuncUnit")

# print(df.shape,df.dtypes)
# print(df.iloc[[9],[3,10]])

# print(df.iloc[9:129,3:11])

print(df.iloc[64,3:11])