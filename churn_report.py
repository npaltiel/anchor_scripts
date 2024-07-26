import pandas as pd

df_patients = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\List of Patients.csv")
df_contracts = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Contract Lookup.csv")
df_2023 = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_2023.csv")
df_jan_april = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_Jan_April.csv")
df_may_june = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_May_June.csv")

combined_df = pd.concat([df_may_june,df_jan_april,df_2023])
combined_df = combined_df[combined_df['Missed Visit'] == 'No']

split_df = combined_df['Patient (Admission ID)'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')','')
combined_df[['Patient Name', 'Admission ID']] = split_df[[0, 1]]

combined_df['Year'] = pd.DatetimeIndex(combined_df['Visit Date']).year
combined_df['Month'] = pd.DatetimeIndex(combined_df['Visit Date']).month

combined_df = combined_df.drop_duplicates(subset = ['Admission ID', 'Month', 'Year'])
combined_df = pd.merge(combined_df, df_contracts, left_on='Contract', right_on='ContractName', how='left')
combined_df = pd.merge(combined_df, df_patients, on='Admission ID', how='left')

combined_df['Unique ID'] = [combined_df['Medicaid No.'][i] if pd.notna(combined_df['Medicaid No.'][i]) else combined_df['Patient Name'][i] + str(combined_df['Date of Birth'][i]) for i in range(len(combined_df))]



