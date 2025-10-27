import pandas as pd
from lifelines import KaplanMeierFitter
from datetime import datetime

# 1. Load all data
df_patients = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
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
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidFeb25_MidSep.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})

# 2. Prep Data
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)
df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

visits_df = pd.concat([df_6, df_5, df_4, df_3, df_2, df_1, df_lehigh])
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Year'] = visits_df['VisitDate'].dt.year
visits_df['Month'] = visits_df['VisitDate'].dt.month

# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Merge patient data and contracts
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left',
                     suffixes=('', '_lehigh'))
visits_df['Date of Birth'] = pd.to_datetime(visits_df['DOB'].combine_first(visits_df['Date of Birth']), errors='coerce')

# Medicaid cleaning
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].replace(r'\.0$', '', regex=True).str.lstrip('0')

# Unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 and
                                  visits_df['ContractType'][i] not in ['CHHA', 'Private Pay']
    else visits_df['PatientName'][i] + str(visits_df['Date of Birth'][i]) for i in range(len(visits_df))
]

# 3. Patient-level aggregation
patients = (
    visits_df.groupby(["UniqueID", "Status"])
    .agg(
        FirstVisitDate=("VisitDate", "min"),
        LastVisitDate=("VisitDate", "max")
    )
    .reset_index()
)

# 3. Mark active patients (e.g., no visits in last X days)
patients["IsActive"] = patients["Status"] == 'Active'

# 4. Create duration and event columns
today = pd.to_datetime("today")
patients["EndDate"] = patients["LastVisitDate"]
patients.loc[patients["IsActive"], "EndDate"] = today

patients["DurationDays"] = (patients["EndDate"] - patients["FirstVisitDate"]).dt.days
patients["event"] = (~patients["IsActive"]).astype(int)

# Optional: Add segmentation fields (if available)
patients["StartYear"] = patients["FirstVisitDate"].dt.year

# 5. Fit Kaplan-Meier
kmf = KaplanMeierFitter()
kmf.fit(durations=patients["DurationDays"], event_observed=patients["event"])

# 6. Key stats
print("Median lifespan (days):", kmf.median_survival_time_)

for day in [30, 60, 90, 180, 365]:
    print(f"Survival after {day} days: {kmf.predict(day):.2%}")

# 7. Export for Power BI
export = patients[["UniqueID", "DurationDays", "event", "IsActive", "StartYear"]]

folder_path = "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Lifetime Expectancy\\"
export.to_csv(folder_path + "lifespan_summary.csv", index=False)

# Optional: Save survival curve
kmf.survival_function_.to_csv(folder_path + "survival_curve.csv")
