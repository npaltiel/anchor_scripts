import pandas as pd
import numpy as np
import sqlite3
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


def convert_hours(value):
    if isinstance(value, str) and value.strip() == '':
        return np.nan  # Handle empty strings
    if isinstance(value, str):
        value = value.replace(':', '.')
    try:
        value = float(value)
    except ValueError:
        return np.nan
    return np.floor(value).astype(int) + (value % 1) / 0.6


hour_columns = ['Billed Hours', 'Pay Hours', 'OT Hours', 'Holiday Hours', 'Total Paid Hours']
converters = {col: convert_hours for col in hour_columns}

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
invoiced_visits = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Team Hours\\Billing_Vs_Payroll_1019_1025.xlsx",
    sheet_name='Detail Data', converters=converters)

invoiced_visits = invoiced_visits[invoiced_visits['Contract'] != 'Grand Total :']
invoiced_visits['Billed Hours'] = invoiced_visits['Billed Hours'] + 13 * invoiced_visits['Billed Live-In']

df_patients = df_patients[['Admission ID - Office', 'Medicaid Number', 'Contract Name', 'Team', 'County', 'Patient Start Date']]
df_patients = df_patients.sort_values(
    by=['Admission ID - Office', 'Contract Name'],
    key=lambda col: col != 'NHTD'
)
df_patients = df_patients.groupby('Admission ID - Office', as_index=False).first()
invoiced_visits = pd.merge(invoiced_visits, df_patients, left_on='Admission ID', right_on='Admission ID - Office',
                           how='left')

invoiced_visits['Invoice Date'] = pd.to_datetime(invoiced_visits['Invoice Date'], errors='coerce')
temp_date = max(invoiced_visits['Invoice Date'])
week_ending = temp_date + timedelta(days=4 - temp_date.weekday())

invoiced_visits['Patient Start Date'] = pd.to_datetime(invoiced_visits['Patient Start Date'])

earliest_start_date = invoiced_visits.groupby(['Medicaid Number', 'Contract']).agg({
    'Billed Hours': 'sum',  # Sum of Billed Hours for each Medicaid Number
    'Patient Start Date': 'min'  # Earliest Patient Start Date for each Medicaid Number
}).reset_index()

# Step 2: Get Team and County based on the latest Patient Start Date
latest_info = invoiced_visits.sort_values(by=['Medicaid Number', 'Patient Start Date'], ascending=[True, False])
latest_info = latest_info.groupby(['Medicaid Number','Contract']).agg({
    'Team': 'first',  # Team corresponding to the latest Patient Start Date
    'County': 'first'  # County corresponding to the latest Patient Start Date
}).reset_index()

# Step 3: Merge the two results
team_billed_hours = pd.merge(earliest_start_date, latest_info, on='Medicaid Number', suffixes=('','_x'))
team_billed_hours.insert(0, 'Week Ending', week_ending)

# Fix IC
ic_medicaids = {}
for i in range(len(invoiced_visits)):
    team = invoiced_visits['Team'][i]
    contract = invoiced_visits['Contract'][i]
    if team is not None and isinstance(team, str) and 'IC' in team and contract in ['TBI', 'NHTD']:
        ic_medicaids[invoiced_visits['Medicaid Number'][i]] = team

admission_ids = [id for id in ic_medicaids]

conn = sqlite3.connect(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visits.db")

query = "SELECT * FROM visits WHERE MedicaidNo IN ({seq})".format(
    seq=','.join(['?'] * len(admission_ids))
)

visits_df = pd.read_sql_query(query, conn, params=admission_ids)

conn.close

visits_df = visits_df[(visits_df['MissedVisit'] == 'No') & (visits_df['Billed'] == 'Yes') & ~(visits_df['ContractName'].isin(['TBI', 'NHTD']))]


def calculate_scheduled_hours(schedule_time):
    # Split the ScheduleTime to get start and end times
    start_str, end_str = schedule_time.split('-')

    # Parse start and end times to datetime objects
    start_time = datetime.strptime(start_str, '%H%M')
    end_time = datetime.strptime(end_str, '%H%M')

    # Calculate the difference, accounting for crossing midnight
    if end_time <= start_time:
        end_time += timedelta(days=1)  # Adjust end time to next day if it crosses midnight

    # Calculate total hours as a float
    scheduled_hours = (end_time - start_time).total_seconds() / 3600
    return scheduled_hours


# Apply the function to calculate ScheduledHours
visits_df['MaxHours'] = visits_df['ScheduleTime'].apply(calculate_scheduled_hours)

visits_df['Year'] = pd.DatetimeIndex(visits_df['VisitDate']).year
visits_df['Month'] = pd.DatetimeIndex(visits_df['VisitDate']).month

# Group by AdmissionId, Year, and Month and sum ScheduledHours
monthly_hours = visits_df.groupby(['MedicaidNo', 'Year', 'Month'])['MaxHours'].sum().reset_index()
max_hours = monthly_hours.groupby('MedicaidNo')['MaxHours'].max().reset_index()
max_hours['MaxHours'] = max_hours['MaxHours'] / 4.345

team_billed_hours = pd.merge(team_billed_hours, max_hours, left_on='Medicaid Number', right_on='MedicaidNo',
                             how='left')

team_billed_hours['Total Hours'] = [
    team_billed_hours['Billed Hours'][i] if pd.isna(team_billed_hours['MaxHours'][
        i]) or team_billed_hours['Billed Hours'][i] <= team_billed_hours['MaxHours'][
        i] else team_billed_hours['MaxHours'][i] for i in range(len(team_billed_hours))]

team_hours_report = team_billed_hours.groupby(['Team','Medicaid Number', 'Contract', 'County','Patient Start Date'])['Total Hours'].sum().reset_index()