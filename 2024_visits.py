import pandas as pd

df_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June24.csv")
df_3 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_May_Nov24.csv")
df_4 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_MidAug24_MidMar25.csv")
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)
df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

visits_df = pd.concat([df_4, df_3, df_2])
visits_df = visits_df.drop_duplicates(subset=['VisitID'])
visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes')].copy()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['Year'] = visits_df['VisitDate'].dt.year
visits_df['Month'] = visits_df['VisitDate'].dt.month
visits_2024 = visits_df[visits_df['Year'] == 2024].copy()

split_df = visits_2024['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_2024[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

visits_2024 = pd.merge(visits_2024, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

split_df = df_lehigh['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
df_lehigh[['PatientName', 'AdmissionID']] = split_df[[0, 1]]
df_lehigh['State'] = 'PA'
df_lehigh['Year'] = pd.to_datetime(df_lehigh['VisitDate'], errors='coerce').dt.year
df_lehigh_2024 = df_lehigh[df_lehigh['Year'] == 2024]

visits_2024 = pd.concat([visits_2024, df_lehigh_2024], ignore_index=True)
visits_2024 = visits_2024.drop_duplicates(subset=['VisitID'])

visits_2024['AdmissionPrefix'] = visits_2024['AdmissionID'].astype(str).str[:3]

county_state_prefix_counts = (
    visits_2024
    .groupby(['State', 'County', 'AdmissionPrefix'], dropna=False)
    .size()
    .reset_index(name='Visit Count')
)

county_state_prefix_counts.to_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Lennie\\2024_Visits_County_Breakdown2.csv",
    index=False)
