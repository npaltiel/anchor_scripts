import pandas as pd
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
prev_admissions = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\List of Patients.csv")
visits_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Visit_Report.csv")

# Filter out missed visits and for NHTD
visits_df = visits_df[(visits_df['ContractName'] == 'NHTD') | (visits_df['ContractName'] == 'TBI')]
visits_df = visits_df[visits_df['MissedVisit'] == 'No']

split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Specify the column to concatenate
concat_column = 'Diagnosis Code -Clinical'
# Dynamically create the aggregation dictionary
aggregation_functions = {col: 'first' for col in df_patients.columns}
# Group by 'key' and apply the aggregation functions
df_patients_agg = df_patients.groupby('Admission ID - Office', as_index=False).agg(aggregation_functions)

visits_df = pd.merge(visits_df, df_patients_agg, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) else visits_df['PatientName'][
                                                                                i] + str(
        visits_df['DOB'][i]) for i in range(len(visits_df))]

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
current = datetime.now() - timedelta(days=30)
start_date = f'{current.month - 1 if current.month != 1 else 12}/26/{current.year if current.month != 1 else current.year - 1}'
end_date = f'{current.month}/25/{current.year}'
cur_df = visits_df[(visits_df['VisitDate'] >= start_date) & (visits_df['VisitDate'] <= end_date)]
prev_df = visits_df[visits_df['VisitDate'] < start_date]

# Again drop duplicates based on Unique ID, Category and the Month
prev_df = prev_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
cur_df = cur_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

prev_ids = []
for i in range(len(prev_df)):
    prev_ids.append(prev_df['UniqueID'][i])

for i in range(len(prev_admissions)):
    prev_ids.append(prev_admissions['MedicaidNo'][i])

cur_df['Address'] = cur_df['Address Line 1'].fillna('').str.title() + ' ' + cur_df['Address Line 2'].fillna(
    '').str.title()
cur_df['City, State'] = cur_df['City'].fillna('').str.title() + ', ' + cur_df['State'].fillna('').str.title()
nhtd_df = cur_df[
    ['Last Name', 'First Name', 'Address', 'City, State', 'Zip', 'DOB', 'Diagnosis Code -Clinical', 'Gender',
     'AdmissionID', 'MedicaidNo']].copy()
nhtd_df['Gender'] = [nhtd_df['Gender'][i][0] for i in range(len(nhtd_df))]
nhtd_df['Visit Date'] = [f'{current.month}/1/{current.year}' if nhtd_df['MedicaidNo'][i] in prev_ids else "" for i in
                         range(len(nhtd_df))]
nhtd_df['DOB'] = pd.to_datetime(nhtd_df['DOB'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce').dt.strftime('%m/%d/%Y')

for i in range(len(nhtd_df)):
    prev_ids.append(nhtd_df['MedicaidNo'][i])

prev_ids_df = pd.DataFrame(prev_ids, columns=['MedicaidNo'])
prev_ids_df = prev_ids_df.drop_duplicates(subset=['MedicaidNo']).reset_index(drop=True)
prev_ids_df.to_csv(
    'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\List of Patients.csv',
    index=False)

# Output Excel file path
excel_file = f'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\All Patients - {current.month} {current.year}.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
nhtd_df.to_excel(excel_file, index=False, sheet_name='Sheet1')
