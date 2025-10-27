# Enhanced Churn Report Script with Updated Grouping Logic

import pandas as pd
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta

# -----------------------------
# Load Data
# -----------------------------
df_caregivers = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Caregivers (Churn).csv")
df_patients = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_livein = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Live In Lookup.csv")
df_1 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv")
df_3 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_May_Nov.csv")
df_4 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidAug_MidMar.csv")
df_5 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidNov_MidJune.csv")
df_6 = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidMar25_MidOct.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)
df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

# -----------------------------
# Visit Preparation
# -----------------------------
visits_df = pd.concat([df_6, df_5, df_4, df_3, df_2, df_1, df_lehigh])
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Year'] = visits_df['VisitDate'].dt.year
visits_df['Month'] = visits_df['VisitDate'].dt.month

# -----------------------------
# Caregiver Churn
# -----------------------------
caregiver_df = visits_df[['CaregiverName_Code', 'Month', 'Year']].copy()
split_df = caregiver_df['CaregiverName_Code'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
caregiver_df[['CaregiverName', 'CaregiverCode']] = split_df[[0, 1]]
caregiver_df = caregiver_df[~caregiver_df['CaregiverCode'].str.contains('CDP', case=False, na=False)]
caregiver_df = caregiver_df.drop_duplicates(subset=['CaregiverCode', 'Month', 'Year']).reset_index(drop=True)

# Get Branch
caregiver_df = caregiver_df.merge(
    df_caregivers[['Caregiver Code - Office', 'Branch']],
    left_on='CaregiverCode',
    right_on='Caregiver Code - Office',
    how='left'
)
caregiver_df.drop(columns=['Caregiver Code - Office'], inplace=True)

# Previous month
caregiver_df['PreviousMonth'] = caregiver_df['Month'] - 1
caregiver_df['PreviousYear'] = caregiver_df['Year']
caregiver_df.loc[caregiver_df['Month'] == 1, 'PreviousMonth'] = 12
caregiver_df.loc[caregiver_df['Month'] == 1, 'PreviousYear'] -= 1

shifted_df = caregiver_df[['CaregiverCode', 'Year', 'Month']].copy()
shifted_df['Exists'] = 1

merged_df = caregiver_df.merge(
    shifted_df,
    left_on=['CaregiverCode', 'PreviousYear', 'PreviousMonth'],
    right_on=['CaregiverCode', 'Year', 'Month'],
    how='left',
    suffixes=('', '_y')
)
caregiver_df['Continued'] = merged_df['Exists'].fillna(0).astype(int)
caregiver_df = caregiver_df.sort_values(by=['CaregiverCode', 'Year', 'Month'])
caregiver_df['Earlier'] = caregiver_df.groupby(['CaregiverCode']).cumcount() > 0
caregiver_df['Retained'] = ((caregiver_df['Continued'] != 1) & caregiver_df['Earlier']).astype(int)
caregiver_df['New'] = (~caregiver_df['Earlier']).astype(int)

caregiver_df.drop(columns=['CaregiverName_Code', 'Earlier', 'PreviousMonth', 'PreviousYear'], inplace=True)

# -----------------------------
# Patient Churn
# -----------------------------
# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Compute duration in hours
hours = visits_df.copy()
hours[['Start Time', 'End Time']] = hours['ScheduleTime'].str.split('-', expand=True)
hours['Start Time'] = pd.to_datetime(hours['Start Time'], format='%H%M', errors='coerce')
hours['End Time'] = pd.to_datetime(hours['End Time'], format='%H%M', errors='coerce')
hours['End Time'] = hours.apply(
    lambda row: row['End Time'] + pd.Timedelta(days=1) if row['End Time'] <= row['Start Time'] else row['End Time'],
    axis=1)
hours['Duration (Hours)'] = (hours['End Time'] - hours['Start Time']).dt.total_seconds() / 3600

livein_pairs = set(zip(df_livein['Contract'], df_livein['Service Code']))
hours.loc[hours.apply(
    lambda row: (row['ContractName'], row['ServiceCode_1']) in livein_pairs and row['Duration (Hours)'] > 13,
    axis=1), 'Duration (Hours)'] = 13
grouped_hours = hours.groupby(['AdmissionID', 'Month', 'Year'], as_index=False).agg({'Duration (Hours)': 'sum'})

# Flag whether the visit is non-billable
visits_df['NonBillable'] = (visits_df['ContractName'] == 'Non Billable')

# Count visits per AdmissionID, Month, Year
visit_counts = visits_df.groupby(['AdmissionID', 'Month', 'Year'])['ContractName'].transform('count')

# Count how many are non-billable
nonbillable_counts = visits_df.groupby(['AdmissionID', 'Month', 'Year'])['NonBillable'].transform('sum')

# Keep only:
# - Non-billable rows if they're the only row for that AdmissionID/Month/Year
# - Or keep all other (billable) rows
visits_df = visits_df[
    ~((visits_df['ContractName'] == 'Non Billable') & (visit_counts > 1))
]

# Now drop duplicates (if more than one billable row remains)
visits_df = visits_df.drop_duplicates(subset=['AdmissionID', 'Month', 'Year'])

visits_df = pd.merge(visits_df, grouped_hours, on=['AdmissionID', 'Month', 'Year'], how='left')

# Merge patient data and contracts
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left',
                     suffixes=('', '_lehigh'))
visits_df['Date of Birth'] = pd.to_datetime(visits_df['DOB'].combine_first(visits_df['Date of Birth']), errors='coerce')

# Age calculation
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Age'] = (visits_df['VisitDate'] - visits_df['Date of Birth']).dt.days / 365.25

# Medicaid cleaning
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].replace(r'\.0$', '', regex=True).str.lstrip('0')

# Unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 and
                                  visits_df['ContractType'][i] not in ['CHHA', 'Private Pay']
    else visits_df['PatientName'][i] + str(visits_df['Date of Birth'][i]) for i in range(len(visits_df))
]

# Remove duplicates by UID+Contract+Month
visits_df = visits_df.drop_duplicates(subset=['UniqueID', 'ContractType', 'Month', 'Year']).reset_index(drop=True)

# Previous month flags
visits_df['PreviousMonth'] = visits_df['Month'] - 1
visits_df['PreviousYear'] = visits_df['Year']
visits_df.loc[visits_df['Month'] == 1, 'PreviousMonth'] = 12
visits_df.loc[visits_df['Month'] == 1, 'PreviousYear'] -= 1

shifted_df = visits_df[['UniqueID', 'ContractType', 'Year', 'Month']].copy()
shifted_df['Exists'] = True
merged_df = visits_df.merge(
    shifted_df,
    left_on=['UniqueID', 'ContractType', 'PreviousYear', 'PreviousMonth'],
    right_on=['UniqueID', 'ContractType', 'Year', 'Month'],
    how='left',
    suffixes=('', '_y')
)
visits_df['Previous (Category)'] = merged_df['Exists'].notna()

# Earlier Total
visits_df['Previous (Total)'] = False
index_df = visits_df.set_index(['UniqueID', 'Year', 'Month'])
for idx, row in visits_df.iterrows():
    uid, year, month = row['UniqueID'], row['Year'], row['Month']
    prev_month = 12 if month == 1 else month - 1
    prev_year = year - 1 if month == 1 else year
    visits_df.at[idx, 'Previous (Total)'] = (uid, prev_year, prev_month) in index_df.index

visits_df.drop(columns=['PreviousMonth', 'PreviousYear'], inplace=True)
visits_df = visits_df.sort_values(by=['UniqueID', 'Year', 'Month', 'ContractType'])
visits_df['Earlier (Category)'] = visits_df.groupby(['UniqueID', 'ContractType']).cumcount() > 0
visits_df['Earlier (Total)'] = visits_df.groupby(['UniqueID']).cumcount() > 0

# Final output table
patients_df = visits_df[[
    'Month', 'Year', 'Branch', 'ContractType', 'ContractName', 'UniqueID', 'AdmissionID', 'PatientName',
    'Team', 'CountyName', 'Duration (Hours)', 'CoordinatorName', 'Gender', 'Age',
    'Previous (Category)', 'Previous (Total)', 'Earlier (Category)', 'Earlier (Total)'
]].copy()

# Metrics
patients_df['Continued (Category)'] = (patients_df['Previous (Category)']).astype(int)
patients_df['Continued (Total)'] = (patients_df['Previous (Total)']).astype(int)
patients_df['Retained (Category)'] = ((~patients_df['Previous (Category)']) & patients_df['Earlier (Category)']).astype(
    int)
patients_df['Retained (Total)'] = ((~patients_df['Previous (Total)']) & patients_df['Earlier (Total)']).astype(int)
patients_df['New (Category)'] = (~patients_df['Earlier (Category)']).astype(int)
patients_df['New (Total)'] = (~patients_df['Earlier (Total)']).astype(int)

patients_df = patients_df[patients_df['ContractType'] != 'Unknown']

# -----------------------------
# Write to SQLite
# -----------------------------
conn = sqlite3.connect(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\PycharmProjects\\anchor_scripts\\Churn\\churn.db")
patients_df.to_sql("patient_churn", conn, if_exists='replace', index=False)
caregiver_df.to_sql("caregiver_churn", conn, if_exists='replace', index=False)
conn.close()
