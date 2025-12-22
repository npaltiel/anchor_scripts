import pandas as pd

# -----------------------------
# 1. DEFINE CLUSTER CONTRACTS
# -----------------------------
cl_contracts = [
    ("Hamaspik Choice MLTC (PCA)", "Cluster Care"),
    ("Hamaspik MAP PCA", "Cluster Care"),
    ("VillageCare PCA", "Cluster Care"),
    ("VillageCare PCA", "PCA Cluster Care"),
    ("SWHNY-MLTC (ANT)", "T1019:U3")
]

# -----------------------------
# 2. LOAD PATIENT & VISIT FILES
# -----------------------------
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Yekusiel Medcheck file.csv"
)

df_1 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv"
)
df_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv"
)
df_3 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_May_Nov.csv"
)
df_4 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidAug_MidMar.csv"
)
df_5 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidNov_MidJune.csv"
)
df_6 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidMar25_MidOct.csv"
)
df_7 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidApr25_MidNov.csv"
)
df_8 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Nov25_Dec25.csv"
)

# -----------------------------
# 3. COMBINE & CLEAN VISITS
# -----------------------------
visits_df = pd.concat([df_8, df_7, df_6, df_5, df_4, df_3, df_2, df_1])

# Remove duplicates
visits_df = visits_df.drop_duplicates(subset=['VisitID'])

# Keep only valid (non-missed, billed) visits
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

# Ensure correct date type
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')

# Normalize important column types
visits_df['ContractName'] = visits_df['ContractName'].astype(str)
visits_df['ServiceCode'] = visits_df['ServiceCode_1'].astype(str)
visits_df['MedicaidID'] = visits_df['MedicaidNo'].astype(str)
df_patients['MedicaidID'] = df_patients['Medicaid ID'].astype(str)

# -----------------------------
# 4. IDENTIFY CLUSTER VISITS
# -----------------------------
cl_df = pd.DataFrame(cl_contracts, columns=["ContractName", "ServiceCode"])

visits_df = visits_df.merge(
    cl_df.assign(IsCluster=1),
    on=["ContractName", "ServiceCode"],
    how="left"
)

visits_df['IsCluster'] = visits_df['IsCluster'].fillna(0).astype(int)

# -----------------------------
# 5. FILTER TO TARGET MEDICAIDS
# -----------------------------
target_medicaids = df_patients['MedicaidID'].unique().tolist()

visits_sub = visits_df[visits_df['MedicaidID'].isin(target_medicaids)].copy()

# -----------------------------
# 6. CALCULATE CLUSTER METRICS
# -----------------------------
grouped = visits_sub.groupby("MedicaidID").agg(
    total_visits=("VisitID", "count"),
    cluster_visits=("IsCluster", "sum"),
    last_visit_date=("VisitDate", "max")
).reset_index()

# Keep only those with ≥1 cluster visit
patient_cluster_summary = grouped[grouped["cluster_visits"] >= 1].copy()

# Sort for readability
patient_cluster_summary = patient_cluster_summary.sort_values(
    "cluster_visits", ascending=False
)

# -----------------------------
# 7. OUTPUT
# -----------------------------
print(patient_cluster_summary)
