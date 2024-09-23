import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

patients_df = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll\\List of Patients.csv")
report_df = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll\\Billing_Vs_Payroll_MayOnwards.csv")

# Drop last 2 unnecessary rows
report_df = report_df[(report_df['Contract'] != 'Grand Total :') & (report_df['Contract'].notna())]

# Get location data from Patients
report_df = pd.merge(report_df, patients_df, on='Admission ID', how='left')

report_df['Year'] = pd.DatetimeIndex(report_df['Date of Service']).year
report_df['Month'] = pd.DatetimeIndex(report_df['Date of Service']).month