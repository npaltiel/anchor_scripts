import pandas as pd
import sqlite3

df_patients = pd.read_csv("C:\\Users\\nochum.paltiel\\Documents\\Churn Report\\List of Patients.csv")
df_contracts = pd.read_csv("C:\\Users\\nochum.paltiel\\Documents\\Churn Report\\Contract Lookup.csv")
df_2023 = pd.read_csv("C:\\Users\\nochum.paltiel\\Documents\\Churn Report\\Visit_Report_2023.csv")
df_2024 = pd.read_csv("C:\\Users\\nochum.paltiel\\Documents\\Churn Report\\Visit_Report_2024.csv")

visits_df = pd.concat([df_2024, df_2023])

visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df['Year'] = pd.DatetimeIndex(visits_df['VisitDate']).year
visits_df['Month'] = pd.DatetimeIndex(visits_df['VisitDate']).month

# Caregiver Churn
caregiver_df = visits_df[['CaregiverName_Code', 'Month', 'Year']].copy()

# Split Caregiver Name and Code
split_df = visits_df['CaregiverName_Code'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
caregiver_df[['CaregiverName', 'CaregiverCode']] = split_df[[0, 1]]

# Drop Duplicates within each month
caregiver_df= caregiver_df.drop_duplicates(subset=['CaregiverCode', 'Month', 'Year']).reset_index(drop=True)

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
caregiver_df['Retained'] = [1 if caregiver_df['Continued'][i] != 1 and caregiver_df['Earlier'][i] == True else 0 for i in range(len(caregiver_df))]
caregiver_df['New'] = [1 if caregiver_df['Continued'][i] != 1 and caregiver_df['Earlier'][i] != True else 0 for i in range(len(caregiver_df))]

caregiver_df.drop(columns=['CaregiverName_Code', 'Earlier', 'PreviousMonth', 'PreviousYear'], inplace=True)



# Patient Churn
# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Remove visit duplicates within each month
visits_df = visits_df.drop_duplicates(subset=['AdmissionID', 'Month', 'Year'])

# Lookup contracts and patient information from relevant sources
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID', how='left')

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) else visits_df['PatientName'][
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

# Sort the DataFrame by 'Unique ID', 'Contract Type', 'Year', and 'Month'
visits_df = visits_df.sort_values(by=['UniqueID', 'ContractType', 'Year', 'Month'])

# Group by 'Unique ID' and 'Contract Type' and calculate cumulative count of earlier records
visits_df['Earlier (Category)'] = visits_df.groupby(['UniqueID', 'ContractType']).cumcount() > 0
visits_df['Earlier (Total)'] = visits_df.groupby(['UniqueID']).cumcount() > 0

# Generate unique combinations of Contract Type, Year, and Month
unique_combinations = visits_df[['ContractType', 'Year', 'Month']].drop_duplicates()
# Remove rows where Contract Type is NaN
unique_combinations = unique_combinations.dropna(subset=['ContractType'])
# Add a 'Total' contract type to represent total rows for each month
totals_combinations = unique_combinations[['Year', 'Month']].drop_duplicates()
code_95 = totals_combinations.copy()
totals_combinations['ContractType'] = ['Total' for _ in range(len(totals_combinations))]
code_95['ContractType'] = ['Code 95' for _ in range(len(code_95))]
# Combine the original and total combinations
combined_combinations = pd.concat([unique_combinations, code_95, totals_combinations], ignore_index=True)


# Create an empty DataFrame to store the results with a MultiIndex
index = pd.MultiIndex.from_tuples([tuple(x) for x in combined_combinations.values],
                                  names=['ContractType', 'Year', 'Month'])
results_df = pd.DataFrame(index=index, columns=['New', 'Continued', 'Retained', 'Total'])

# Initialize the DataFrame with zeros
results_df = results_df.fillna(0)

# Populate the DataFrame with counts based on the conditions
for (contract_type, year, month), _ in results_df.iterrows():
    if contract_type == 'Total' or contract_type == 'Code 95':
        if contract_type == 'Total':
            monthly_data = visits_df[(visits_df['Year'] == year) & (visits_df['Month'] == month)]
        else:
            monthly_data = visits_df[(visits_df['Year'] == year) & (visits_df['Month'] == month) & (
                    visits_df['Branch'] == contract_type)]

        continued_count = monthly_data[monthly_data['Previous (Total)'] == True].shape[0]
        new_count = monthly_data[(monthly_data['Previous (Total)'] == False) & (monthly_data['Earlier (Total)'] == False)].shape[0]
        retained_count = monthly_data[(monthly_data['Previous (Total)'] == False) & (monthly_data['Earlier (Total)'] == True)].shape[0]
        total_count = monthly_data.shape[0]

    else:
        monthly_data = visits_df[(visits_df['Year'] == year) & (visits_df['Month'] == month) & (
                    visits_df['ContractType'] == contract_type)]

        # Count the number of rows that meet each condition
        continued_count = monthly_data[monthly_data['Previous (Category)'] == True].shape[0]
        new_count = monthly_data[(monthly_data['Previous (Category)'] == False) & (monthly_data['Earlier (Category)'] == False)].shape[0]
        retained_count = monthly_data[(monthly_data['Previous (Category)'] == False) & (monthly_data['Earlier (Category)'] == True)].shape[0]
        total_count = monthly_data.shape[0]

    # Assign the counts to the appropriate cells in the results DataFrame
    results_df.loc[(contract_type, year, month), 'Continued'] = continued_count
    results_df.loc[(contract_type, year, month), 'New'] = new_count
    results_df.loc[(contract_type, year, month), 'Retained'] = retained_count
    results_df.loc[(contract_type, year, month), 'Total'] = total_count

# Sort the MultiIndex by 'Contract Type' first, then by 'Year' and 'Month'
results_df = results_df.sort_index(level=['ContractType', 'Year', 'Month'])
results_df.reset_index(inplace=True)

results_df['PreviousMonth'] = results_df['Month'] - 1
results_df['PreviousYear'] = results_df['Year']
results_df.loc[results_df['Month'] == 1, 'PreviousMonth'] = 12
results_df.loc[results_df['Month'] == 1, 'PreviousYear'] -= 1

# Create a shifted DataFrame for comparison
shifted_df = results_df[['ContractType', 'Year', 'Month', 'Total']].copy()
shifted_df.columns = ['ContractType', 'PreviousYear', 'PreviousMonth', 'PreviousTotal']


# Merge the original DataFrame with the shifted DataFrame
merged_df = results_df.merge(
    shifted_df,
    on=['PreviousYear', 'PreviousMonth', 'ContractType'],
    how='left',
)

results_df['PreviousTotal'] = merged_df['PreviousTotal'].fillna(0).astype(int)
results_df['Continued Percentage'] = merged_df['Continued']/merged_df['PreviousTotal']
results_df['Growth'] = [results_df['Total'][i] - results_df['PreviousTotal'][i] if results_df['PreviousTotal'][i] > 0 else None for i in range(len(results_df))]
results_df.drop(columns=['PreviousMonth', 'PreviousYear', 'PreviousTotal'], inplace=True)


# Write dataframes to database
conn = sqlite3.connect("C:\\Users\\nochum.paltiel\\Documents\\PycharmProjects\\anchor_scripts\\churn.db")

# Create all tables
results_df.to_sql("patient_churn_results", conn, if_exists='replace', index=False)
caregiver_df.to_sql("caregiver_churn", conn, if_exists='replace', index=False)

conn.close()
