import pandas as pd
import numpy as np
import sqlite3
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

# month = datetime.today() - relativedelta(months=1)
month = 'October'


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
    f"C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Team Hours\\Billing_Vs_Payroll_{month}.xlsx",
    sheet_name='Detail Data', converters=converters)

invoiced_visits = invoiced_visits[invoiced_visits['Contract'] != 'Grand Total :']
invoiced_visits['Billed Hours'] = invoiced_visits['Billed Hours'] + 13 * invoiced_visits['Billed Live-In']

# Get Patient Data
# Create UniqueID for Patients
df_patients['UniqueID'] = [
    df_patients['Medicaid Number'][i] if pd.notna(df_patients['Medicaid Number'][i]) and df_patients['Medicaid Number'][
        i] != 0 else
    df_patients['Patient Name'][i] + str(df_patients['DOB'][i]) for i in range(len(df_patients))]
# Get original Patient Start Date
df_patients['Patient Start Date'] = pd.to_datetime(df_patients['Patient Start Date'])

earliest_start_date = df_patients.groupby(['UniqueID']).agg({
    'Patient Start Date': 'min'  # Earliest Patient Start Date for each Medicaid Number
}).reset_index()

# Get Medicaid, Team and County
df_patients = df_patients[
    ['Admission ID - Office', 'Contract Name', 'UniqueID', 'Team', 'County', 'Branch']]
df_patients = df_patients.groupby(['Admission ID - Office', 'Contract Name'], as_index=False).first()
invoiced_visits = pd.merge(invoiced_visits, df_patients, left_on=['Admission ID', 'Contract'],
                           right_on=['Admission ID - Office', 'Contract Name'],
                           how='left')
invoiced_visits = pd.merge(invoiced_visits, earliest_start_date, on='UniqueID',
                           how='left')

team_billed_hours = invoiced_visits.groupby(['Admission ID', 'Contract']).agg({
    'UniqueID': 'first',
    'Billed Hours': 'sum',  # Sum of Billed Hours for each Medicaid Number
    'Patient Start Date': 'first',
    'Team': 'first',
    'County': 'first',
    'Branch': 'first'
}).reset_index()

# Fix IC
team_billed_hours['Hours'] = [
    team_billed_hours['Billed Hours'][i] / 2 if team_billed_hours['Team'][i] is not None and isinstance(
        team_billed_hours['Team'][i], str) and 'IC' in team_billed_hours['Team'][i] and team_billed_hours['Contract'][
                                                    i] in [
                                                    'TBI', 'NHTD'] else team_billed_hours['Billed Hours'][i] for i in
    range(len(team_billed_hours))]

# Fix Non Billable Contracts
temp_patients = df_patients[~(df_patients['Contract Name'] == 'Non Billable')]
contract_lookup = temp_patients.set_index('Admission ID - Office')['Contract Name'].to_dict()

team_billed_hours['Contract'] = team_billed_hours.apply(
    lambda row: row['Contract'] if row['Contract'] != 'Non Billable'
    else contract_lookup.get(row['Admission ID'], row['Contract']),
    axis=1
)

# Get Contract Type
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
team_billed_hours = pd.merge(team_billed_hours, df_contracts, left_on='Contract', right_on='ContractName', how='left')
team_billed_hours['Contract Type'] = team_billed_hours['ContractType'].fillna('Unknown')
team_billed_hours['Contract Type'] = [
    'Cluster' if team_billed_hours['Branch'][i] == 'Cluster' else team_billed_hours['Contract Type'][i] for i in
    range(len(team_billed_hours))]

boroughs = ['new york', 'kings', 'queens', 'bronx', 'richmond']
grouping = []
for i in range(len(team_billed_hours)):
    if team_billed_hours['County'][i] is not None and team_billed_hours['County'][i].lower() in boroughs:
        grouping.append('In 5 Boroughs')
    else:
        grouping.append('Outside 5 Boroughs')
team_billed_hours['Group'] = grouping

# Final Report
team_hours_report = \
    team_billed_hours.groupby(['Team', 'Contract Type', 'Group'])[
        'Hours'].sum().reset_index()

# invoiced_visits['Invoice Date'] = pd.to_datetime(invoiced_visits['Invoice Date'], errors='coerce')
# temp_date = max(invoiced_visits['Invoice Date'])
# week_ending = (temp_date + timedelta(days=4 - temp_date.weekday())).strftime('%m-%d-%Y')
#
# team_hours_report.insert(0, 'Week Ending', week_ending)
# team_hours_report['Patient Start Date'] = team_hours_report['Patient Start Date'].dt.strftime('%m/%d/%Y')

excel_file = f"C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Team Hours\\Team Hours Reports\\Team_Hours_Report_{month}.xlsx"
team_hours_report.to_excel(excel_file, index=False, sheet_name='Sheet1')
