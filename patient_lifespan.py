import pandas as pd
import sqlite3

conn = sqlite3.connect(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visits.db")

visits_df = pd.read_sql_query('SELECT MedicaidNo, PatientName, AdmissionID, VisitDate, Billed, MissedVisit FROM visits',
                              conn)

conn.close()

visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[visits_df['Billed'] == 'Yes']

# Lookup contracts and patient information from relevant sources
df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_patients_lehigh = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\List of Patients Lehigh.csv")
df_patients_lehigh['Medicaid Number'] = df_patients_lehigh['Medicaid Number'].astype(str)

visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
visits_df = pd.merge(visits_df, df_patients_lehigh, left_on='MedicaidNo', right_on='Medicaid Number', how='left',
                     suffixes=('', '_lehigh'))
visits_df['Date of Birth'] = visits_df['DOB'].combine_first(visits_df['Date of Birth'])

# Create unique ID
visits_df['UniqueID'] = [visits_df['PatientName'][i] + str(visits_df['Date of Birth'][i]) for i in
                         range(len(visits_df))]

# Ensure VisitDate is in datetime format
visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'])

# Group by UniqueID to calculate first and last visit dates
lifespan_df = visits_df.groupby('UniqueID').agg(
    FirstVisit=('VisitDate', 'min'),
    LastVisit=('VisitDate', 'max')
).reset_index()

# Calculate the lifespan (in days) for each UniqueID
lifespan_df['LifespanDays'] = (lifespan_df['LastVisit'] - lifespan_df['FirstVisit']).dt.days

# Add lifespan back to the original DataFrame (optional)
visits_df = pd.merge(visits_df, lifespan_df[['UniqueID', 'LifespanDays']], on='UniqueID', how='left')

# Calculate the average lifespan across all UniqueIDs
average_lifespan = lifespan_df['LifespanDays'].mean()

print(f"Average lifespan of patients: {average_lifespan:.2f} days")
