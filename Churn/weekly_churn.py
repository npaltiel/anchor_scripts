import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_caregivers = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Caregivers.csv")
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
visits_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Weekly Churn\\Visit_Report.csv")
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[pd.notna(visits_df['VisitTime'])]

today = date.today()
start_of_2_weeks = today - pd.DateOffset(days=today.weekday() + 16 - (7 if today.weekday() == 5 else 0))
start_of_3_weeks_ago = start_of_2_weeks - pd.DateOffset(days=7)
week = start_of_2_weeks - pd.DateOffset(days=1)

# Caregiver Churn
caregiver_df = visits_df.copy()

split_df = caregiver_df['CaregiverName_Code'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
caregiver_df[['CaregiverName', 'CaregiverCode']] = split_df[[0, 1]]

caregiver_df = pd.merge(caregiver_df, df_caregivers, left_on='CaregiverCode', right_on='Caregiver Code - Office',
                        how='left')

caregivers_recent = caregiver_df[caregiver_df['VisitDate'] >= start_of_2_weeks]
caregivers_three_weeks_ago = caregiver_df[
    (caregiver_df['VisitDate'] >= start_of_3_weeks_ago) & (caregiver_df['VisitDate'] < start_of_2_weeks)]

caregivers_recent = caregivers_recent.drop_duplicates(subset=['CaregiverCode']).reset_index(drop=True)
caregivers_three_weeks_ago = caregivers_three_weeks_ago.drop_duplicates(subset=['CaregiverCode']).reset_index(drop=True)

caregivers_missing = \
    caregivers_three_weeks_ago[~caregivers_three_weeks_ago['CaregiverCode'].isin(caregivers_recent['CaregiverCode'])][[
        'Status', 'CaregiverCode', 'Primary Office']]

caregivers_missing.insert(0, 'Week Ending', week.strftime("%m-%d-%Y"))

# Patient Churn
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.replace(r'\.0$', '', regex=True)
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 else
    visits_df['PatientName'][
        i] + str(
        visits_df['DOB'][i]) for i in range(len(visits_df))]

recent = visits_df[visits_df['VisitDate'] >= start_of_2_weeks]
three_weeks_ago = visits_df[
    (visits_df['VisitDate'] >= start_of_3_weeks_ago) & (visits_df['VisitDate'] < start_of_2_weeks)]

recent = recent.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
three_weeks_ago = three_weeks_ago.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

patients_missing = three_weeks_ago[~three_weeks_ago['UniqueID'].isin(recent['UniqueID'])][[
    'Status', 'AdmissionID', 'ContractType']]

patients_missing.insert(0, 'Week Ending', week.strftime("%m-%d-%Y"))

file_path = "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Weekly Churn\\Weekly Churn Report.xlsx"
caregiver_sheet_name = "Caregiver Data"
patient_sheet_name = "Patient Data"

with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
    caregivers_missing.to_excel(writer, sheet_name=caregiver_sheet_name, index=False, header=False,
                                startrow=writer.sheets[caregiver_sheet_name].max_row)
with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
    patients_missing.to_excel(writer, sheet_name=patient_sheet_name, index=False, header=False,
                              startrow=writer.sheets[patient_sheet_name].max_row)

# Send Email to Mendy Wineberg, Rivke, Chaya and David
# Active churn without PA and CDPAP
