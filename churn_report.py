import pandas as pd
from datetime import datetime

df_patients = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\List of Patients.csv")
df_contracts = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Contract Lookup.csv")
df_2023 = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_2023.csv")
df_jan_april = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_Jan_April.csv")
df_may_june = pd.read_csv("C:\\Users\\nochum.paltiel\\Downloads\\Visit_Report_May_June.csv")

combined_df = pd.concat([df_may_june, df_jan_april, df_2023])
combined_df = combined_df[combined_df['Missed Visit'] == 'No']

split_df = combined_df['Patient (Admission ID)'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
combined_df[['Patient Name', 'Admission ID']] = split_df[[0, 1]]

combined_df['Year'] = pd.DatetimeIndex(combined_df['Visit Date']).year
combined_df['Month'] = pd.DatetimeIndex(combined_df['Visit Date']).month

combined_df = combined_df.drop_duplicates(subset=['Admission ID', 'Month', 'Year'])
combined_df = pd.merge(combined_df, df_contracts, left_on='Contract', right_on='ContractName', how='left')
combined_df = pd.merge(combined_df, df_patients, on='Admission ID', how='left')

combined_df['Unique ID'] = [
    combined_df['Medicaid No.'][i] if pd.notna(combined_df['Medicaid No.'][i]) else combined_df['Patient Name'][
                                                                                        i] + str(
        combined_df['Date of Birth'][i]) for i in range(len(combined_df))]
combined_df = combined_df.drop_duplicates(subset=['Unique ID', 'Contract Type', 'Month', 'Year']).reset_index(drop=True)

# Finding Previous Month
# Create a column for the previous month and year
combined_df['Previous Month'] = combined_df['Month'] - 1
combined_df['Previous Year'] = combined_df['Year']
combined_df.loc[combined_df['Month'] == 1, 'Previous Month'] = 12
combined_df.loc[combined_df['Month'] == 1, 'Previous Year'] -= 1

# Create a shifted DataFrame for comparison
shifted_df = combined_df[['Unique ID', 'Contract Type', 'Year', 'Month']].copy()
shifted_df['Exists'] = True

# Merge the original DataFrame with the shifted DataFrame
merged_df1 = combined_df.merge(
    shifted_df,
    left_on=['Unique ID', 'Contract Type', 'Previous Year', 'Previous Month'],
    right_on=['Unique ID', 'Contract Type', 'Year', 'Month'],
    how='left',
    suffixes=('', '_y')
)

# Add a new column to indicate whether the previous entry exists
combined_df['Previous (Category)'] = merged_df1['Exists'].notna()

# Create a column for the Previous (Ever) check
combined_df['Previous (Ever)'] = False
# Create a MultiIndex DataFrame to easily check for previous records
index_df = combined_df.set_index(['Unique ID', 'Year', 'Month'])

# Iterate over each row to check for previous month occurrence
for idx, row in combined_df.iterrows():
    uid, year, month = row['Unique ID'], row['Year'], row['Month']

    # Determine the previous month and year
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Check if there's a record with the same Unique ID in the previous month/year
    combined_df.at[idx, 'Previous (Ever)'] = (uid, prev_year, prev_month) in index_df.index

# Drop the temporary columns
combined_df.drop(columns=['Previous Month', 'Previous Year'], inplace=True)

# Sort the DataFrame by 'Unique ID', 'Contract Type', 'Year', and 'Month'
combined_df = combined_df.sort_values(by=['Unique ID', 'Contract Type', 'Year', 'Month'])

# Group by 'Unique ID' and 'Contract Type' and calculate cumulative count of earlier records
combined_df['Earlier (Category)'] = combined_df.groupby(['Unique ID', 'Contract Type']).cumcount() > 0
combined_df['Earlier (Ever)'] = combined_df.groupby(['Unique ID']).cumcount() > 0

# Generate unique combinations of Contract Type, Year, and Month
unique_combinations = combined_df[['Contract Type', 'Year', 'Month']].drop_duplicates()
# Remove rows where Contract Type is NaN
unique_combinations = unique_combinations.dropna(subset=['Contract Type'])
# Add a 'Total' contract type to represent total rows for each month
totals_combinations = unique_combinations[['Year', 'Month']].drop_duplicates()
code_95 = totals_combinations.copy()
totals_combinations['Contract Type'] = ['Total' for _ in range(len(totals_combinations))]
code_95['Contract Type'] = ['Code 95' for _ in range(len(code_95))]
# Combine the original and total combinations
combined_combinations = pd.concat([unique_combinations, code_95, totals_combinations], ignore_index=True)


# Create an empty DataFrame to store the results with a MultiIndex
index = pd.MultiIndex.from_tuples([tuple(x) for x in combined_combinations.values],
                                  names=['Contract Type', 'Year', 'Month'])
results_df = pd.DataFrame(index=index, columns=['New', 'Continued', 'Retained', 'Total'])

# Initialize the DataFrame with zeros
results_df = results_df.fillna(0)

# Populate the DataFrame with counts based on the conditions
for (contract_type, year, month), _ in results_df.iterrows():
    if contract_type == 'Total' or contract_type == 'Code 95':
        if contract_type == 'Total':
            monthly_data = combined_df[(combined_df['Year'] == year) & (combined_df['Month'] == month)]
        else:
            monthly_data = combined_df[(combined_df['Year'] == year) & (combined_df['Month'] == month) & (
                    combined_df['Branch'] == contract_type)]

        continued_count = monthly_data[monthly_data['Previous (Ever)'] == True].shape[0]
        new_count = monthly_data[(monthly_data['Previous (Ever)'] == False) & (monthly_data['Earlier (Ever)'] == False)].shape[0]
        retained_count = monthly_data[(monthly_data['Previous (Ever)'] == False) & (monthly_data['Earlier (Ever)'] == True)].shape[0]
        total_count = monthly_data.shape[0]

    else:
        monthly_data = combined_df[(combined_df['Year'] == year) & (combined_df['Month'] == month) & (
                    combined_df['Contract Type'] == contract_type)]

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
results_df = results_df.sort_index(level=['Contract Type', 'Year', 'Month'])

current_month = datetime.today().month
current_year = datetime.today().year
file_name = f'Churn_Report_Stats_{current_month}_{current_year}.csv'
file_path = 'C:\\Users\\nochum.paltiel\\Documents\\Churn Report\\'
results_df.to_csv(file_path + file_name)
