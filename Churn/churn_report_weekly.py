# Enhanced Churn Report Script with Week Ending Logic

import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

# -----------------------------
# Load Data
# -----------------------------
df_caregivers = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Caregivers (Churn).csv")
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_livein = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Live In Lookup.csv")
df_1 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv")
df_3 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_May_Nov.csv")
df_4 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidAug_MidMar.csv")
df_5 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidNov_MidJune.csv")
df_6 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidMar25_MidOct.csv")
df_7 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidApr25_MidNov.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)
df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

# -----------------------------
# Visit Preparation
# -----------------------------
visits_df = pd.concat([df_7, df_6, df_5, df_4, df_3, df_2, df_1, df_lehigh])
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Year'] = visits_df['VisitDate'].dt.year
visits_df['Month'] = visits_df['VisitDate'].dt.month

# Calculate Week Ending (Friday)
# dayofweek: Monday=0, Sunday=6, so Friday=4
visits_df['WeekEnding'] = visits_df['VisitDate'] + pd.to_timedelta(
    (4 - visits_df['VisitDate'].dt.dayofweek) % 7, unit='D'
)

# -----------------------------
# Caregiver Churn (Week-Based)
# -----------------------------
caregiver_df = visits_df[['CaregiverName_Code', 'WeekEnding']].copy()
split_df = caregiver_df['CaregiverName_Code'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
caregiver_df[['CaregiverName', 'CaregiverCode']] = split_df[[0, 1]]
caregiver_df = caregiver_df[~caregiver_df['CaregiverCode'].str.contains('CDP', case=False, na=False)]
caregiver_df = caregiver_df.drop_duplicates(subset=['CaregiverCode', 'WeekEnding']).reset_index(drop=True)

# Get Branch
caregiver_df = caregiver_df.merge(
    df_caregivers[['Caregiver Code - Office', 'Branch']],
    left_on='CaregiverCode',
    right_on='Caregiver Code - Office',
    how='left'
)
caregiver_df.drop(columns=['Caregiver Code - Office'], inplace=True)

# Previous week (7 days before)
caregiver_df['PreviousWeekEnding'] = caregiver_df['WeekEnding'] - pd.Timedelta(days=7)

shifted_df = caregiver_df[['CaregiverCode', 'WeekEnding']].copy()
shifted_df['Exists'] = 1

merged_df = caregiver_df.merge(
    shifted_df,
    left_on=['CaregiverCode', 'PreviousWeekEnding'],
    right_on=['CaregiverCode', 'WeekEnding'],
    how='left',
    suffixes=('', '_y')
)
caregiver_df['Continued'] = merged_df['Exists'].fillna(0).astype(int)
caregiver_df = caregiver_df.sort_values(by=['CaregiverCode', 'WeekEnding'])
caregiver_df['Earlier'] = caregiver_df.groupby(['CaregiverCode']).cumcount() > 0
caregiver_df['Retained'] = ((caregiver_df['Continued'] != 1) & caregiver_df['Earlier']).astype(int)
caregiver_df['New'] = (~caregiver_df['Earlier']).astype(int)

caregiver_df.drop(columns=['CaregiverName_Code', 'Earlier', 'PreviousWeekEnding'], inplace=True)

# -----------------------------
# Patient Churn (Week-Based)
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
grouped_hours = hours.groupby(['AdmissionID', 'WeekEnding'], as_index=False).agg({'Duration (Hours)': 'sum'})

# Flag whether the visit is non-billable
visits_df['NonBillable'] = (visits_df['ContractName'] == 'Non Billable')

# Count visits per AdmissionID, WeekEnding
visit_counts = visits_df.groupby(['AdmissionID', 'WeekEnding'])['ContractName'].transform('count')

# Count how many are non-billable
nonbillable_counts = visits_df.groupby(['AdmissionID', 'WeekEnding'])['NonBillable'].transform('sum')

# Keep only:
# - Non-billable rows if they're the only row for that AdmissionID/WeekEnding
# - Or keep all other (billable) rows
visits_df = visits_df[
    ~((visits_df['ContractName'] == 'Non Billable') & (visit_counts > 1))
]

# Now drop duplicates (if more than one billable row remains)
visits_df = visits_df.drop_duplicates(subset=['AdmissionID', 'WeekEnding'])

visits_df = pd.merge(visits_df, grouped_hours, on=['AdmissionID', 'WeekEnding'], how='left')

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

# Remove duplicates by UID+Contract+WeekEnding
visits_df = visits_df.drop_duplicates(subset=['UniqueID', 'ContractType', 'WeekEnding']).reset_index(drop=True)

# Previous week flags
visits_df['PreviousWeekEnding'] = visits_df['WeekEnding'] - pd.Timedelta(days=7)

# Check if patient existed in previous week (Category)
shifted_df = visits_df[['UniqueID', 'ContractType', 'WeekEnding']].copy()
shifted_df['Exists'] = True
merged_df = visits_df.merge(
    shifted_df,
    left_on=['UniqueID', 'ContractType', 'PreviousWeekEnding'],
    right_on=['UniqueID', 'ContractType', 'WeekEnding'],
    how='left',
    suffixes=('', '_y')
)
visits_df['Previous (Category)'] = merged_df['Exists'].notna()

# Check if patient existed in previous week (Total - any contract)
shifted_total = visits_df[['UniqueID', 'WeekEnding']].drop_duplicates().copy()
shifted_total['Exists'] = True
merged_total = visits_df.merge(
    shifted_total,
    left_on=['UniqueID', 'PreviousWeekEnding'],
    right_on=['UniqueID', 'WeekEnding'],
    how='left',
    suffixes=('', '_total')
)
visits_df['Previous (Total)'] = merged_total['Exists'].notna()

visits_df.drop(columns=['PreviousWeekEnding'], inplace=True)
visits_df = visits_df.sort_values(by=['UniqueID', 'WeekEnding', 'ContractType'])
visits_df['Earlier (Category)'] = visits_df.groupby(['UniqueID', 'ContractType']).cumcount() > 0
visits_df['Earlier (Total)'] = visits_df.groupby(['UniqueID']).cumcount() > 0

visits_df['InvoiceDate'] = pd.to_datetime(visits_df['InvoiceDate'], errors='coerce')
visits_df['WeekEnding-Invoice'] = visits_df['InvoiceDate'] + pd.to_timedelta(
    (4 - visits_df['InvoiceDate'].dt.dayofweek) % 7, unit='D'
)

# Final output table
patients_df = visits_df[[
    'WeekEnding', 'WeekEnding-Invoice', 'Branch', 'ContractType', 'ContractName', 'UniqueID', 'AdmissionID',
    'PatientName',
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
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\PycharmProjects\\anchor_scripts\\Churn\\churn_weekly.db")
patients_df.to_sql("patient_churn", conn, if_exists='replace', index=False)
caregiver_df.to_sql("caregiver_churn", conn, if_exists='replace', index=False)
conn.close()
