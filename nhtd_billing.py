import pandas as pd
from datetime import date, datetime, timedelta
from openpyxl import load_workbook

current = datetime.now() - timedelta(days=30)

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
prev_admissions = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Prev Patients.csv")
visits_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Visit_Report.csv")

# Filter out missed visits and for NHTD
visits_df = visits_df[(visits_df['ContractName'] == 'NHTD') | (visits_df['ContractName'] == 'TBI')]
visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[pd.notna(visits_df['VisitTime'])]

split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Dynamically create the aggregation dictionary
aggregation_functions = {col: 'first' for col in df_patients.columns}
# Group by 'key' and apply the aggregation functions
df_patients = df_patients[
    (~df_patients['Admission ID - Office'].str.contains("CDP", na=False)) &
    (~df_patients['Admission ID - Office'].str.contains("ANS", na=False)) &
    (~df_patients['Admission ID - Office'].str.contains("OHZ", na=False))
    ].copy().reset_index(drop=True)
df_patients_agg = df_patients.groupby('Admission ID - Office', as_index=False).agg(aggregation_functions)

visits_df['AdmissionID'] = visits_df['AdmissionID'].str.strip()
df_patients_agg['Admission ID - Office'] = df_patients_agg['Admission ID - Office'].str.strip()
visits_df = pd.merge(visits_df, df_patients_agg, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

# Again drop duplicates based on Unique ID, Category and the Month
visits_df = visits_df.drop_duplicates(subset=['MedicaidNo']).reset_index(drop=True)

prev_ids = []
for i in range(len(prev_admissions)):
    prev_ids.append(prev_admissions['MedicaidNo'][i])

visits_df['Address'] = visits_df['Address Line 1'].fillna('').str.title() + ' ' + visits_df['Address Line 2'].fillna(
    '').str.title()
visits_df['City, State'] = visits_df['City'].fillna('').str.title() + ', ' + visits_df['State'].fillna('').str.title()
nhtd_df = visits_df[
    ['Last Name', 'First Name', 'Address', 'City, State', 'Zip', 'DOB', 'Gender',
     'AdmissionID', 'MedicaidNo']].copy()
nhtd_df['Gender'] = [nhtd_df['Gender'][i][0] for i in range(len(nhtd_df))]
nhtd_df['DX Code'] = 'F03.90'
nhtd_df['Visit Date'] = [
    f'{current.month}/1/{current.year}' if nhtd_df['MedicaidNo'][i] in prev_ids else f'{current.month}/3/{current.year}'
    for i in
    range(len(nhtd_df))]
nhtd_df['DOB'] = pd.to_datetime(nhtd_df['DOB'], errors='coerce').dt.strftime('%m/%d/%Y')

anchor_active = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Anchor).xlsx")
abode_active = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Abode).xlsx")
attentive_active = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Attentive).xlsx")

anchor_active = anchor_active[
    ["Name", "SC Agency", "Start Date with SC", "Previous SC", "CIN", "Trans/Diversion", "HCSS Agency"]]
abode_active = abode_active[
    ["Name", "SC Agency", "Start Date with SC", "Previous SC", "CIN", "Trans/Diversion", "HCSS Agency"]]
attentive_active = attentive_active[
    ["Name", "SC Agency", "Start Date with SC", "Previous SC", "CIN", "Trans/Diversion", "HCSS Agency"]]

agencies_df = pd.concat([anchor_active, abode_active, attentive_active]).reset_index()
agencies_df = agencies_df.drop_duplicates().reset_index(drop=True)

agencies_df['Start Date with SC'] = pd.to_datetime(agencies_df['Start Date with SC'], errors='coerce')

last_month_28th = (datetime.today().replace(day=1) - timedelta(days=1)).replace(day=28)
agencies_df['Current SC'] = [
    agencies_df["SC Agency"][i].strip() if pd.isna(agencies_df['Start Date with SC'][i]) or
                                           agencies_df['Start Date with SC'][i] <= last_month_28th else
    agencies_df["Previous SC"][i].strip() for i in
    range(len(agencies_df))]

discharged_anchor = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Discharged (Anchor).xlsx")
discharged_abode = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Discharged (Abode).xlsx")
discharged_abode['SC Agency'] = 'Abode'
discharged_attentive = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Discharged (Attentive).xlsx")
discharged_attentive['SC Agency'] = 'Attentive'

nhtd_df['MedicaidNo'] = nhtd_df['MedicaidNo'].str.strip()
agencies_df['CIN'] = agencies_df['CIN'].str.strip()
discharged_anchor['Admission ID'] = discharged_anchor['Admission ID'].str.strip()
discharged_abode['CIN'] = agencies_df['CIN'].str.strip()
discharged_attentive['CIN'] = agencies_df['CIN'].str.strip()
nhtd_df = nhtd_df.merge(agencies_df[['CIN', 'Current SC', 'Trans/Diversion']], left_on='MedicaidNo', right_on='CIN',
                        how='left')
nhtd_df = nhtd_df.merge(discharged_anchor[['Admission ID', 'SC Agency']], left_on='AdmissionID',
                        right_on='Admission ID',
                        how='left')
nhtd_df = nhtd_df.merge(discharged_abode[['CIN', 'SC Agency']], left_on='MedicaidNo', right_on='CIN',
                        how='left')
nhtd_df = nhtd_df.merge(discharged_attentive[['CIN', 'SC Agency']], left_on='MedicaidNo', right_on='CIN',
                        how='left')
nhtd_df['Visit Type'] = ["SC monthly visit" if nhtd_df['MedicaidNo'][i] in prev_ids else nhtd_df['Trans/Diversion'][i]
                         for i in
                         range(len(nhtd_df))]

for i in range(len(nhtd_df)):
    prev_ids.append(nhtd_df['MedicaidNo'][i])

start_of_month = datetime(datetime.today().year, datetime.today().month, 1)
service_only = agencies_df[(~agencies_df['CIN'].isin(nhtd_df['MedicaidNo'])) &
                           (agencies_df['Start Date with SC'] < start_of_month) &
                           (~agencies_df['HCSS Agency'].str.contains('Anchor', case=False))]

df_patients_agg = df_patients_agg.groupby('Medicaid Number', as_index=False).agg(aggregation_functions)
service_only = pd.merge(service_only, df_patients_agg, left_on='CIN', right_on='Medicaid Number', how='left')
service_only['Address'] = service_only['Address Line 1'].fillna('').str.title() + ' ' + service_only[
    'Address Line 2'].fillna(
    '').str.title()
service_only['City, State'] = service_only['City'].fillna('').str.title() + ', ' + service_only['State'].fillna(
    '').str.title()
service_only = service_only.rename(columns={
    'Admission ID - Office': 'AdmissionID',
    'Medicaid Number': 'MedicaidNo'
})
service_only['MedicaidNo'] = (
    service_only['CIN']
    .fillna(service_only['MedicaidNo'])
)
service_only['Visit Type'] = 'Service Only'
service_only['DX Code'] = 'F03.90'
service_only = service_only[
    ['Current SC', 'Last Name', 'First Name', 'Address', 'City, State', 'Zip', 'DOB', 'DX Code',
     'Gender',
     'AdmissionID', 'MedicaidNo', 'Visit Type']]
service_only['Gender'] = [
    gender[0] if pd.notna(gender) else gender
    for gender in service_only['Gender']
]
service_only['Visit Date'] = f'{current.month}/1/{current.year}'

nhtd_df['Current SC'] = (
    nhtd_df['Current SC']
    .fillna(nhtd_df['SC Agency_x'])
    .fillna(nhtd_df['SC Agency_y'])
    .fillna(nhtd_df['SC Agency'])
)
nhtd_df = nhtd_df[
    ['Current SC', 'Last Name', 'First Name', 'Address', 'City, State', 'Zip', 'DOB', 'DX Code',
     'Gender',
     'AdmissionID', 'MedicaidNo', 'Visit Date', 'Visit Type']]
nhtd_df = pd.concat([nhtd_df, service_only], ignore_index=True)

# Get Visit Rates
rates = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Visit Rates.csv")
nhtd_df = pd.merge(nhtd_df, rates, on='Visit Type', how='left')

nhtd_df = nhtd_df.rename(columns={
    'Last Name': 'Last',
    'First Name': 'First',
    'DX Code': 'DX',
    'MedicaidNo': 'CIN',
    'AdmissionID': 'Admission ID'
})

# Ouput individual SC agencies billing sheets
nhtd_df['Current SC'] = nhtd_df['Current SC'].str.strip()
nhtd_df = nhtd_df.drop_duplicates(subset=['CIN']).reset_index(drop=True)

agencies = ['Anchor', 'Abode', 'Attentive', 'Able']
for agency in agencies:
    df = nhtd_df[nhtd_df['Current SC'] == agency].drop(columns=['Current SC'])
    file_path = f"C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\SC Billing\\{agency} Billing.xlsx"
    # File exists: Load the workbook and write to a new sheet
    with pd.ExcelWriter(file_path, engine='openpyxl', mode='a') as writer:
        workbook = load_workbook(file_path)
        df.to_excel(writer, sheet_name=current.strftime("%B %Y"), index=False)

# Output Excel file path
excel_file = f'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\All Patients - {current.month} {current.year}.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
nhtd_df.to_excel(excel_file, index=False, sheet_name='Sheet1')

prev_ids_df = pd.DataFrame(prev_ids, columns=['MedicaidNo'])
prev_ids_df = prev_ids_df.drop_duplicates(subset=['MedicaidNo']).reset_index(drop=True)
# prev_ids_df.to_csv(
#     'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Prev Patients.csv',
#     index=False)
