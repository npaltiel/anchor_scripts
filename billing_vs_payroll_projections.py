import pandas as pd
import numpy as np
import sqlite3


# Custom function for hours: Replace ':' with '.', convert to float, and apply the floor + decimal transformation
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


# Custom function for dollars: Remove '$', convert to float without any additional transformation
def convert_dollars(value):
    if isinstance(value, str) and value.strip() == '':
        return np.nan  # Handle empty strings
    if isinstance(value, str):
        value = value.replace('$', '').replace(',', '')
    try:
        return float(value)
    except ValueError:
        return np.nan


# List of hour and dollar columns
hour_columns = ['Billed Hours', 'Pay Hours', 'OT Hours', 'Holiday Hours', 'Total Paid Hours']
dollar_columns = ['Billed Rate', 'Billed Rate', 'Pay Rate', 'Billed Amount', 'Paid Amount', 'OT Pay Rate', 'OT Amount',
                  'Holiday Pay Rate', 'Holiday Amount', 'Total Payroll Amount']  # Replace with actual dollar columns

# Create a dictionary for converters
converters = {col: convert_hours for col in hour_columns}
converters.update({col: convert_dollars for col in dollar_columns})

# # Read CSV and apply converters
# df1 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_2020.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df2 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_2021.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df3 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_2022.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df4 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_2023_Jan_Jul.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df5 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Aug23.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df6 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Sep23.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df7 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Oct23.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df8 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Nov23.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df9 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Dec23.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df10 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_January.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df11 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_February.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df12 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_March.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df13 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_April.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df14 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_May.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df15 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_June.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df16 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_July.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df17 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Aug_Nov.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df19 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_December.xlsx",
#     sheet_name='Detail Data', converters=converters)
# df20 = pd.read_excel(
#     "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Jan_25_half.xlsx",
#     sheet_name='Detail Data', converters=converters)
df21 = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Billing vs Payroll Monthly Reports (Invoice Date)\\Billing_Vs_Payroll_Jan25_21_27.xlsx",
    sheet_name='Detail Data', converters=converters)

report_df = pd.concat(
    [df21])

patients_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
patients_df = patients_df.groupby(['Admission ID - Office', 'Contract Name'], as_index=False).first()
counties_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\County Lookup.csv")

# Drop last 2 unnecessary rows
report_df = report_df[(report_df['Contract'] != 'Grand Total :') & (report_df['Contract'].notna())]

# Get Live In hours into Billed Hours
report_df['Billed Hours'] = report_df['Billed Hours'] + 13 * report_df['Billed Live-In']

# Get location data from Patients
report_df = pd.merge(report_df, patients_df, left_on=['Admission ID', 'Contract'],
                     right_on=['Admission ID - Office', 'Contract Name'], how='left')
report_df = pd.merge(report_df, counties_df, on='County', how='left')

'''# Get Discipline/Get rid of RN
####################
###################
###################'''

report_df['Year'] = pd.DatetimeIndex(report_df['Date of Service']).year
report_df['Month'] = pd.DatetimeIndex(report_df['Date of Service']).month

office, wp = [], []
for i in range(len(report_df)):
    if "CDP" in report_df['Admission ID'][i]:
        office.append("CDPAP")
    elif "OHZ" in report_df['Admission ID'][i]:
        office.append("PA")
    else:
        office.append("HHA/PCA")

    wp_hours = report_df['Total Paid Hours'][i] - report_df['Holiday Hours'][i] - report_df['OT Hours'][i]
    if report_df['Location'][i] == 'NYC':
        wp_amount = max(21.64 - report_df['Pay Rate'][i], 0.6)
    elif report_df['Location'][i] == 'Westchester - Long Island':
        wp_amount = max(20.77 - report_df['Pay Rate'][i], 0.6)
    else:
        wp_amount = 0.6
    wp.append(wp_amount * wp_hours)

report_df['Office'] = office
report_df['Tax'] = report_df['Total Payroll Amount'] * 0.13
report_df['Wage Parity'] = wp
report_df['Overhead'] = 1.88 * report_df['Billed Hours']

pmpm = report_df.groupby(['Office', 'Admission ID', 'Month', 'Year'], as_index=False)['Billed Hours'].sum()
pmpm = pmpm[(pmpm['Year'] == 2024) & (pmpm['Month'] >= 8) & (pmpm['Office'] == "CDPAP")].reset_index()
total = []
for i in range(len(pmpm)):
    if pmpm['Billed Hours'][i] < 160:
        total.append(146.45)
    elif pmpm['Billed Hours'][i] < 480:
        total.append(387.84)
    else:
        total.append(1046.36)

pmpm['Total'] = total
pmpm['PMPM Hourly'] = pmpm['Total'] / pmpm['Billed Hours']
report_df = pd.merge(report_df, pmpm, on=['Admission ID', 'Month', 'Year'], how='left', suffixes=['', 'pmpm'])
report_df['PMPM'] = report_df['PMPM Hourly'] * report_df['Billed Hours']


def insert_or_replace(table_name, df, conn):
    # Get the columns of the DataFrame
    columns = ", ".join(df.columns)
    # Create placeholders for the values
    placeholders = ", ".join(["?"] * len(df.columns))
    # Create the SQL statement
    sql = f"INSERT OR REPLACE INTO {table_name} ({columns}) VALUES ({placeholders})"
    # Execute the SQL statement for each row in the DataFrame
    cur = conn.cursor()
    for row in df.itertuples(index=False, name=None):
        cur.execute(sql, row)
    conn.commit()


report_df.columns = report_df.columns.str.replace(' ', '')
report_df.columns = report_df.columns.str.replace('-', '')
report_df.drop(columns=['index'], inplace=True)
conn = sqlite3.connect(
    "C:\\Users\\nochum.paltiel\\Documents\\PycharmProjects\\anchor_scripts\\billing_vs_payroll.db")


def create_table_from_df(table_name, df, conn):
    # Generate the CREATE TABLE statement based on DataFrame columns and data types
    col_defs = []
    for col_name, dtype in df.dtypes.items():
        if "int" in str(dtype):
            col_type = "INTEGER"
        elif "float" in str(dtype):
            col_type = "REAL"
        elif "datetime64" in str(dtype):  # Check for datetime64 type
            col_type = "DATETIME"
        else:
            col_type = "TEXT"
        col_defs.append(f"{col_name} {col_type}")

    columns_sql = ", ".join(col_defs)

    # Add a UNIQUE constraint on all columns combined to ensure the entire row is unique
    unique_columns_sql = ", ".join(df.columns)
    unique_constraint_sql = f", UNIQUE({unique_columns_sql})"

    sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_sql}{unique_constraint_sql})"

    # Execute the SQL statement
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


# create_table_from_df("billing_vs_payroll", report_df, conn)
insert_or_replace("billing_vs_payroll", report_df, conn)

conn.close()
