import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

df_patients = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_1 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv")
df_3 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_July_Sep.csv")
df_4 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Visit_Report_Sep_Oct.csv")
df_lehigh = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)

df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

visits_df = pd.concat([df_1, df_2, df_3, df_4, df_lehigh])

# Convert VisitDate to datetime format
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')

# Filter out missed visits
visits_df = visits_df[visits_df['MissedVisit'] == 'No']

# Extract Year and Month from VisitDate
visits_df['Year'] = pd.DatetimeIndex(visits_df['VisitDate']).year
visits_df['Month'] = pd.DatetimeIndex(visits_df['VisitDate']).month

# Patient Churn: Split patient name and admission ID
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Lookup contracts and patient information
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left', suffixes=('','_lehigh'))
visits_df['Date of Birth'] = visits_df['DOB'].combine_first(visits_df['Date of Birth'])

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.replace(r'\.0$', '', regex=True)

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 and visits_df['ContractType'][i] not in ['CHHA','Private Pay']
    else visits_df['PatientName'][i] + str(visits_df['Date of Birth'][i]) for i in range(len(visits_df))
]

# Sort the DataFrame by 'Unique ID', 'VisitDate', and 'ContractType'
visits_df = visits_df.sort_values(by=['UniqueID', 'VisitDate', 'ContractType'])

# Check for earlier visits within the last 6 months
# Group by 'UniqueID' and 'ContractType', and shift visit dates to compare with previous visits
visits_df['PrevVisitDate'] = visits_df.groupby(['UniqueID', 'ContractType'])['VisitDate'].shift(1)
visits_df['TimeDiff'] = visits_df['VisitDate'] - visits_df['PrevVisitDate']

# Flag visits that occurred within the last 6 months for both contract-specific and overall checks
visits_df['Earlier'] = (visits_df['TimeDiff'] <= pd.Timedelta(days=182)) & visits_df['PrevVisitDate'].notna()

# Reset index
visits_df.reset_index(inplace=True, drop=True)

# Work with only columns you require
patients_df = visits_df[visits_df['Earlier']==False][['AdmissionID', 'Date of Birth', 'Month', 'Year', 'Branch', 'Team','ContractName', 'ContractType', 'UniqueID', 'PatientName', 'Earlier']].copy()

patients_df.reset_index(inplace=True, drop=True)

patients_df['Branch_Updated'] = [
    'Baby' if pd.notna(patients_df['Date of Birth'][i]) and
    datetime.strptime(patients_df['Date of Birth'][i].strip(), "%m/%d/%Y").date() >= date.today() - relativedelta(years=2)
    else patients_df['Branch'][i]
    for i in range(len(patients_df))
]

patients_df = patients_df.drop_duplicates(subset=['AdmissionID', 'Month', 'Year']).reset_index(drop=True)

excel_file = 'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\soc_2024.xlsx'
patients_df.to_excel(excel_file, index=False, sheet_name='Sheet1')
