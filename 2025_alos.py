import pandas as pd

# -----------------------------
# Load Data
# -----------------------------
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_1 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidAug24_MidMar25.csv")
df_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidNov24_MidJune25.csv")
df_3 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidMar25_MidOct.csv")
df_4 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Sep25_MidJan26.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)
df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

# -----------------------------
# Visit Preparation
# -----------------------------
visits_df = pd.concat([df_4, df_3, df_2, df_1, df_lehigh])
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Year'] = visits_df['VisitDate'].dt.year
visits_df['Month'] = visits_df['VisitDate'].dt.month

visits_df = visits_df[visits_df['Year'] == 2025]

# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]
visits_df['PatientName'] = visits_df['PatientName'].str.strip()

# Merge patient data and contracts
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

# Medicaid cleaning
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].replace(r'\.0$', '', regex=True).str.lstrip('0')

# Unique ID
visits_df['UniqueID'] = (
    visits_df['MedicaidNo']
    .where(
        visits_df['MedicaidNo'].notna() &
        (visits_df['MedicaidNo'] != '0') &
        (~visits_df['ContractType'].isin(['CHHA', 'Private Pay']))
    )
    .fillna(
        visits_df['PatientName'] + visits_df['DOB'].astype(str)
    )
)

df_2025_visits_summary = (
    visits_df
    .groupby(
        ['UniqueID', 'PatientName', 'ContractType', 'Status'],
        as_index=False
    )
    .agg(
        First_Visit_Date=('VisitDate', 'min'),
        Last_Visit_Date=('VisitDate', 'max')
    )
)

df_2025_visits_summary = df_2025_visits_summary.rename(
    columns={'ContractType': 'Contract Category'}
)

output_path = (
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Lennie\\2025_Patient_First_Last_Visit2.xlsx")

df_2025_visits_summary.to_excel(output_path, index=False, engine="openpyxl")
