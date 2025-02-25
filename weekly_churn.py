import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
visits_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Weekly Churn\\Visit_Report.csv")
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[pd.notna(visits_df['VisitTime'])]

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

today = date.today()
start_of_2_weeks = today - pd.DateOffset(days=today.weekday() + 16 - (7 if today.weekday() == 5 else 0))
start_of_3_weeks_ago = start_of_2_weeks - pd.DateOffset(days=7)

recent = visits_df[visits_df['VisitDate'] >= start_of_2_weeks]
three_weeks_ago = visits_df[
    (visits_df['VisitDate'] >= start_of_3_weeks_ago) & (visits_df['VisitDate'] < start_of_2_weeks)]

recent = recent.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
three_weeks_ago = three_weeks_ago.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

missing_from_last_week = three_weeks_ago[~three_weeks_ago['UniqueID'].isin(recent['UniqueID'])][[
    'Status', 'AdmissionID', 'ContractType']]

week = start_of_2_weeks - pd.DateOffset(days=1)
missing_from_last_week.insert(0, 'Week Ending', week.strftime("%m-%d-%Y"))

file_path = "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Weekly Churn\\Weekly Churn Report.xlsx"
sheet_name = "Data"

with pd.ExcelWriter(file_path, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
    missing_from_last_week.to_excel(writer, sheet_name=sheet_name, index=False, header=False,
                                    startrow=writer.sheets[sheet_name].max_row)
