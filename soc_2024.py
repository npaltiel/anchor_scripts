import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import sqlite3

df_patients = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_1 = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2 = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv")
df_3 = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_July_Sep.csv")
df_4 = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Visit_Report_Sep_Oct.csv")
df_lehigh = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)

df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

visits_df = pd.concat([df_1, df_2, df_3, df_4, df_lehigh])

visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df['Year'] = pd.DatetimeIndex(visits_df['VisitDate']).year
visits_df['Month'] = pd.DatetimeIndex(visits_df['VisitDate']).month

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
# Create a column for the cutoff date (6 months before the current visit)
visits_df['SixMonthCutoff'] = visits_df['VisitDate'] - pd.DateOffset(months=6)

# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left', suffixes=('','_lehigh'))
visits_df['Date of Birth'] = visits_df['DOB'].combine_first(visits_df['Date of Birth'])

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.replace(r'\.0$', '', regex=True)

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 and visits_df['ContractType'][i] not in ['CHHA','Private Pay'] else visits_df['PatientName'][
                                                                                        i] + str(
        visits_df['Date of Birth'][i]) for i in range(len(visits_df))]

visits_df = visits_df.sort_values(by=['VisitDate'])


visits_df = visits_df.sort_values(by=['UniqueID', 'VisitDate'])

# Group by 'UniqueID' and use shift to compare with the previous row within the group
visits_df['PrevVisitDate'] = visits_df.groupby('UniqueID')['VisitDate'].shift(1)

# Calculate the time difference between each visit and the previous visit
visits_df['TimeDiff'] = visits_df['VisitDate'] - visits_df['PrevVisitDate']

# Now, we can flag the visits that occurred within the last 6 months
visits_df['Earlier (Total)'] = (visits_df['TimeDiff'] <= pd.Timedelta(days=182)) & visits_df['PrevVisitDate'].notna()

# Drop the temporary columns you don't need after the computation
visits_df.drop(columns=['PrevVisitDate', 'TimeDiff', 'PrevVisitContractDate', 'ContractTimeDiff'], inplace=True)


# Lookup contracts and patient information from relevant sources
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')

# Again drop duplicates based on Unique ID, Category and the Month
visits_df = visits_df.drop_duplicates(subset=['UniqueID', 'Month', 'Year', 'Earlier (Total)']).reset_index(drop=True)

# Work with only columns I require
patients_df = visits_df[['Month', 'Year', 'Branch', 'ContractType', 'UniqueID', 'PatientName', 'Earlier (Total)']].copy()

# Get Metrics I need
patients_df['New (Total)'] = [1 if patients_df['Earlier (Total)'][i] != True else 0 for i in range(len(patients_df))]

patients_pa = patients_df[patients_df['ContractType']=='PA']
patients_df = patients_df[~(patients_df['ContractType']=='PA')]

patients_df['Branch_Updated'] = [
    'Baby' if pd.notna(patients_df['Date of Birth'][i]) and
    datetime.strptime(patients_df['Date of Birth'][i].strip(), "%m/%d/%Y").date() >= date.today() - relativedelta(years=2)
    else patients_df['Branch'][i]
    for i in range(len(patients_df))
]


