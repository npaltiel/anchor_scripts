import pandas as pd
import numpy as np
import sqlite3
from datetime import date, datetime
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

df_patients = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
invoiced_visits = pd.read_excel("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Team Hours\\Billing_Vs_Payroll_1019_1025.xlsx", sheet_name='Detail Data', converters=converters)

invoiced_visits = invoiced_visits[invoiced_visits['Contract'] != 'Grand Total :']

df_patients = df_patients.groupby('Admission ID - Office', as_index=False).first()
invoiced_visits = pd.merge(invoiced_visits, df_patients, left_on='Admission ID', right_on='Admission ID - Office', how='left')

# Group the invoiced_visits by team