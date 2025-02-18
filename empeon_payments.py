import pandas as pd
import numpy as np

payments_1 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Empeon Payments Report\\Empeon Payments 1.csv")
payments_2 = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Empeon Payments Report\\Empeon Payments 2.csv")

payments = pd.concat([payments_1, payments_2])

# Count occurrences of each (Id, Pay Detail Begin Date) combination
duplicate_counts = payments.groupby(['Id', 'Pay Detail Begin Date']).size().reset_index(name='Count')

# Filter only duplicates (count > 1)
duplicate_payments = duplicate_counts[duplicate_counts['Count'] > 1]

# Merge with the original dataframe to get detailed duplicate records
filtered_payments = payments.merge(duplicate_payments[['Id', 'Pay Detail Begin Date']],
                                   on=['Id', 'Pay Detail Begin Date'],
                                   how='inner')

filtered_payments['Pay Detail Begin Date'] = pd.to_datetime(filtered_payments['Pay Detail Begin Date'], errors='coerce')
filtered_payments['Pay Detail End Date'] = pd.to_datetime(filtered_payments['Pay Detail End Date'], errors='coerce')

filtered_payments = filtered_payments.sort_values(by=['Id', 'Pay Detail Begin Date'])
filtered_payments['Comment'] = filtered_payments['Comment'].str.lower()

# Group by 'Id' and 'Pay Detail Begin Date' and count unique (case-insensitive) comments

comment_groups = filtered_payments.groupby(['Id', 'Pay Detail Begin Date'])['Comment'].nunique().reset_index()

# Identify records where all comments are the same for the given Id and Pay Detail Begin Date
same_comment_records = comment_groups[comment_groups['Comment'] == 1][['Id', 'Pay Detail Begin Date']]

# Create a flag column to mark whether a group belongs to 'same_comment'
filtered_payments['Same_Comment_Flag'] = filtered_payments.duplicated(subset=['Id', 'Pay Detail Begin Date', 'Comment'],
                                                                      keep=False)

# Separate payments into two buckets
same_comment = filtered_payments[filtered_payments['Same_Comment_Flag'] &
                                 filtered_payments.set_index(['Id', 'Pay Detail Begin Date']).index.isin(
                                     same_comment_records.set_index(['Id', 'Pay Detail Begin Date']).index)].copy()

different_comment = filtered_payments[~filtered_payments.index.isin(same_comment.index)].copy()

# Step 1: Calculate visit duration in hours
same_comment.loc[:, 'Visit Duration'] = np.where(
    same_comment['Pay Detail End Date'].isna(),
    np.nan,  # Flag as NaN if no end time
    (same_comment['Pay Detail End Date'] - same_comment['Pay Detail Begin Date']).dt.total_seconds() / 3600
)

# Step 2: Get the max visit duration for each start time (Id + Pay Detail Begin Date)
max_durations = same_comment.groupby(['Id', 'Pay Detail Begin Date'])['Visit Duration'].max().reset_index()
max_durations.rename(columns={'Visit Duration': 'Max Visit Duration'}, inplace=True)

# Step 3: Merge the max duration back into the main dataframe
same_comment = same_comment.merge(max_durations, on=['Id', 'Pay Detail Begin Date'], how='left')

# Step 4: Assign the max duration to all entries sharing the same start time
same_comment['Visit Duration'] = same_comment['Max Visit Duration']

# Drop the helper column
same_comment.drop(columns=['Max Visit Duration'], inplace=True)

# Step 5: Sum total hours for each visit (grouped only by Id + Begin Date)
total_hours_per_visit = same_comment.groupby(['Id', 'Pay Detail Begin Date'])['Pay Detail Hours'].sum().reset_index()
total_hours_per_visit.rename(columns={'Pay Detail Hours': 'Total Pay Detail Hours'}, inplace=True)

# Step 6: Merge summed hours back into the `same_comment` dataframe
same_comment = same_comment.merge(total_hours_per_visit, on=['Id', 'Pay Detail Begin Date'], how='left')

# Round Visit Duration and Total Pay Detail Hours to the nearest half hour
same_comment.loc[:, 'Visit Duration'] = np.ceil(same_comment['Visit Duration'] * 2) / 2
same_comment.loc[:, 'Total Pay Detail Hours'] = np.round(same_comment['Total Pay Detail Hours'] * 2) / 2

# Step 7: Flag visits where total paid hours exceed visit duration
same_comment['Overpaid Flag'] = np.where(
    (same_comment['Visit Duration'].isna()) | (
            same_comment['Total Pay Detail Hours'] > same_comment['Visit Duration']),
    True,
    False
)

# Step 1: Calculate visit duration in hours
different_comment.loc[:, 'Visit Duration'] = np.where(
    different_comment['Pay Detail End Date'].isna(),
    np.nan,  # Flag as NaN if no end time
    (different_comment['Pay Detail End Date'] - different_comment['Pay Detail Begin Date']).dt.total_seconds() / 3600
)

# Step 2: Get the max visit duration for each start time (Id + Pay Detail Begin Date)
max_durations = different_comment.groupby(['Id', 'Pay Detail Begin Date'])['Visit Duration'].max().reset_index()
max_durations.rename(columns={'Visit Duration': 'Max Visit Duration'}, inplace=True)

# Step 3: Merge the max duration back into the main dataframe
different_comment = different_comment.merge(max_durations, on=['Id', 'Pay Detail Begin Date'], how='left')

# Step 4: Assign the max duration to all entries sharing the same start time
different_comment['Visit Duration'] = different_comment['Max Visit Duration']

# Drop the helper column
different_comment.drop(columns=['Max Visit Duration'], inplace=True)

# Step 5: Sum total hours for each visit (grouped only by Id + Begin Date)
total_hours_per_visit = different_comment.groupby(['Id', 'Pay Detail Begin Date'])[
    'Pay Detail Hours'].sum().reset_index()
total_hours_per_visit.rename(columns={'Pay Detail Hours': 'Total Pay Detail Hours'}, inplace=True)

# Step 6: Merge summed hours back into the `same_comment` dataframe
different_comment = different_comment.merge(total_hours_per_visit, on=['Id', 'Pay Detail Begin Date'], how='left')

# Round Visit Duration and Total Pay Detail Hours to the nearest half hour
different_comment.loc[:, 'Visit Duration'] = np.ceil(different_comment['Visit Duration'] * 2) / 2
different_comment.loc[:, 'Total Pay Detail Hours'] = np.round(different_comment['Total Pay Detail Hours'] * 2) / 2

# Step 7: Flag visits where total paid hours exceed visit duration
different_comment['Overpaid Flag'] = np.where(
    (different_comment['Visit Duration'].isna()) | (
            different_comment['Total Pay Detail Hours'] > different_comment['Visit Duration']),
    True,
    False
)

regular = same_comment[same_comment['Overpaid Flag'] == True].copy()
mutual = different_comment[different_comment['Overpaid Flag'] == True].copy()

excel_file = f'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Empeon Payments Report\\Regular.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
regular.to_excel(excel_file, index=False, sheet_name='Sheet1')
# Output Excel file path
excel_file = f'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Empeon Payments Report\\Mutual.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
mutual.to_excel(excel_file, index=False, sheet_name='Sheet1')
