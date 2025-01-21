import pandas as pd
import sqlite3
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
df_1 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Jan_June.csv")
df_3 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_May_Nov.csv")
df_4 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Oct_Dec.csv")
df_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Visit_Report_Lehigh.csv",
    dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)

df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

visits_df = pd.concat([df_1, df_2, df_3, df_4, df_lehigh])

visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[visits_df['Billed'] == 'Yes']
visits_df['Year'] = pd.DatetimeIndex(visits_df['VisitDate']).year
visits_df['Month'] = pd.DatetimeIndex(visits_df['VisitDate']).month

# Caregiver Churn
caregiver_df = visits_df[['CaregiverName_Code', 'Month', 'Year']].copy()

# Split Caregiver Name and Code
split_df = visits_df['CaregiverName_Code'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
caregiver_df[['CaregiverName', 'CaregiverCode']] = split_df[[0, 1]]
# Get rid of CDPAP
caregiver_df = caregiver_df[~caregiver_df['CaregiverCode'].str.contains('CDP', case=False, na=False)]

# Drop Duplicates within each month
caregiver_df = caregiver_df.drop_duplicates(subset=['CaregiverCode', 'Month', 'Year']).reset_index(drop=True)

# Create a column for the previous month and year
caregiver_df['PreviousMonth'] = caregiver_df['Month'] - 1
caregiver_df['PreviousYear'] = caregiver_df['Year']
caregiver_df.loc[caregiver_df['Month'] == 1, 'PreviousMonth'] = 12
caregiver_df.loc[caregiver_df['Month'] == 1, 'PreviousYear'] -= 1

# Create a shifted DataFrame for comparison
shifted_df = caregiver_df[['CaregiverCode', 'Year', 'Month']].copy()
shifted_df['Exists'] = 1

# Merge the original DataFrame with the shifted DataFrame
merged_df = caregiver_df.merge(
    shifted_df,
    left_on=['CaregiverCode', 'PreviousYear', 'PreviousMonth'],
    right_on=['CaregiverCode', 'Year', 'Month'],
    how='left',
    suffixes=('', '_y')
)

# Add a new column to indicate whether the previous entry exists
caregiver_df['Continued'] = merged_df['Exists']
caregiver_df['Continued'] = caregiver_df['Continued'].fillna(0).astype(int)

# Sort the DataFrame by 'CaregiverCode', 'Year', and 'Month'
caregiver_df = caregiver_df.sort_values(by=['CaregiverCode', 'Year', 'Month'])

# Group by 'Unique ID' and 'Contract Type' and calculate cumulative count of earlier records
caregiver_df['Earlier'] = caregiver_df.groupby(['CaregiverCode']).cumcount() > 0
caregiver_df = caregiver_df.reset_index(drop=True)
caregiver_df['Retained'] = [1 if caregiver_df['Continued'][i] != 1 and caregiver_df['Earlier'][i] == True else 0 for i
                            in range(len(caregiver_df))]
caregiver_df['New'] = [1 if caregiver_df['Earlier'][i] != True else 0 for i in range(len(caregiver_df))]

caregiver_pa = caregiver_df[caregiver_df['CaregiverCode'].str.contains('OHZ', case=False, na=False)]
caregiver_df = caregiver_df[~caregiver_df['CaregiverCode'].str.contains('OHZ', case=False, na=False)]

caregiver_df.drop(columns=['CaregiverName_Code', 'Earlier', 'PreviousMonth', 'PreviousYear'], inplace=True)
caregiver_pa.drop(columns=['CaregiverName_Code', 'Earlier', 'PreviousMonth', 'PreviousYear'], inplace=True)

# Patient Churn
# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Remove visit duplicates within each month
visits_df = visits_df.drop_duplicates(subset=['AdmissionID', 'Month', 'Year'])

# Lookup contracts and patient information from relevant sources
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left',
                     suffixes=('', '_lehigh'))
visits_df['Date of Birth'] = visits_df['DOB'].combine_first(visits_df['Date of Birth'])

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.replace(r'\.0$', '', regex=True)
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) and visits_df['MedicaidNo'][i] != 0 and
                                  visits_df['ContractType'][i] not in ['CHHA', 'Private Pay'] else
    visits_df['PatientName'][
        i] + str(
        visits_df['Date of Birth'][i]) for i in range(len(visits_df))]

# Again drop duplicates based on Unique ID, Category and the Month
visits_df = visits_df.drop_duplicates(subset=['UniqueID', 'ContractType', 'Month', 'Year']).reset_index(drop=True)

# Finding Previous Month
# Create a column for the previous month and year
visits_df['PreviousMonth'] = visits_df['Month'] - 1
visits_df['PreviousYear'] = visits_df['Year']
visits_df.loc[visits_df['Month'] == 1, 'PreviousMonth'] = 12
visits_df.loc[visits_df['Month'] == 1, 'PreviousYear'] -= 1

# Create a shifted DataFrame for comparison
shifted_df = visits_df[['UniqueID', 'ContractType', 'Year', 'Month']].copy()
shifted_df['Exists'] = True

# Merge the original DataFrame with the shifted DataFrame
merged_df = visits_df.merge(
    shifted_df,
    left_on=['UniqueID', 'ContractType', 'PreviousYear', 'PreviousMonth'],
    right_on=['UniqueID', 'ContractType', 'Year', 'Month'],
    how='left',
    suffixes=('', '_y')
)

# Add a new column to indicate whether the previous entry exists
visits_df['Previous (Category)'] = merged_df['Exists'].notna()

# Create a column for the Previous (Ever) check
visits_df['Previous (Total)'] = False
# Create a MultiIndex DataFrame to easily check for previous records
index_df = visits_df.set_index(['UniqueID', 'Year', 'Month'])

# Iterate over each row to check for previous month occurrence
for idx, row in visits_df.iterrows():
    uid, year, month = row['UniqueID'], row['Year'], row['Month']

    # Determine the previous month and year
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Check if there's a record with the same Unique ID in the previous month/year
    visits_df.at[idx, 'Previous (Total)'] = (uid, prev_year, prev_month) in index_df.index

# Drop the temporary columns
visits_df.drop(columns=['PreviousMonth', 'PreviousYear'], inplace=True)

# Sort the DataFrame by 'Unique ID', 'Year', and 'Month'
visits_df = visits_df.sort_values(by=['UniqueID', 'Year', 'Month', 'ContractType'])

# Group by 'Unique ID' and 'Contract Type' and calculate cumulative count of earlier records
visits_df['Earlier (Category)'] = visits_df.groupby(['UniqueID', 'ContractType']).cumcount() > 0
visits_df['Earlier (Total)'] = visits_df.groupby(['UniqueID']).cumcount() > 0
visits_df.reset_index(inplace=True, drop=True)

visits_df['Branch_Updated'] = [
    'Baby' if pd.notna(visits_df['Date of Birth'][i]) and
              datetime.strptime(visits_df['Date of Birth'][i].strip(), "%m/%d/%Y %H:%M").date() >= pd.Timestamp(
        visits_df['VisitDate'][i]).date() - relativedelta(years=3)
              and visits_df['Branch'][i] != 'Code 95'
    else visits_df['Branch'][i]
    for i in range(len(visits_df))
]

# Work with only columns I require
patients_df = visits_df[
    ['Month', 'Year', 'Branch_Updated', 'ContractType', 'UniqueID', 'PatientName', 'Previous (Category)',
     'Previous (Total)', 'Earlier (Category)', 'Earlier (Total)']].copy()

# Get Metrics I need
patients_df['Continued (Category)'] = [1 if patients_df['Previous (Category)'][i] == True else 0 for i in
                                       range(len(patients_df))]
patients_df['Continued (Total)'] = [1 if patients_df['Previous (Total)'][i] == True else 0 for i in
                                    range(len(patients_df))]
patients_df['Retained (Category)'] = [
    1 if patients_df['Previous (Category)'][i] != True and patients_df['Earlier (Category)'][i] == True else 0 for i in
    range(len(patients_df))]
patients_df['Retained (Total)'] = [
    1 if patients_df['Previous (Total)'][i] != True and patients_df['Earlier (Total)'][i] == True else 0 for i in
    range(len(patients_df))]
patients_df['New (Category)'] = [1 if patients_df['Earlier (Category)'][i] != True else 0 for i in
                                 range(len(patients_df))]
patients_df['New (Total)'] = [1 if patients_df['Earlier (Total)'][i] != True else 0 for i in range(len(patients_df))]

patients_df = patients_df[patients_df['ContractType'] != 'Unknown']

patients_pa = patients_df[patients_df['ContractType'] == 'PA']
patients_df = patients_df[~(patients_df['ContractType'] == 'PA')]

# Write dataframes to database
conn = sqlite3.connect("C:\\Users\\nochum.paltiel\\Documents\\PycharmProjects\\anchor_scripts\\churn.db")

# Create all tables
patients_df.to_sql("patient_churn", conn, if_exists='replace', index=False)
patients_pa.to_sql("patient_pa", conn, if_exists='replace', index=False)
caregiver_df.to_sql("caregiver_churn", conn, if_exists='replace', index=False)
caregiver_pa.to_sql("caregiver_pa", conn, if_exists='replace', index=False)

conn.close()
