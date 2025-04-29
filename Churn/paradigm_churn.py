import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


def get_paradigm_churn():
    df_1 = pd.read_excel(
        "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Paradigm\\SuperbillReport_Jan_June.xlsx")
    df_2 = pd.read_excel(
        "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Paradigm\\SuperbillReport_July_December.xlsx")
    df_3 = pd.read_excel(
        "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\Paradigm\\SuperbillReport_Jan25_Mar25.xlsx")

    visits_df = pd.concat([df_1, df_2, df_3])
    visits_df = visits_df.drop_duplicates(subset=['Note Id']).reset_index(drop=True)

    # Create unique ID
    visits_df['UniqueID'] = [visits_df['First Name'][i] + visits_df['Last Name'][i] + str(visits_df['DOB'][i]) for i in
                             range(len(visits_df))]

    visits_df['DOB'] = pd.to_datetime(visits_df['DOB'])
    visits_df['Note Id'] = pd.to_datetime(visits_df['Note Id'])

    threshold = pd.Timedelta(days=21 * 366)
    visits_df['Age Category'] = [
        'Geriatric' if visits_df['Note Id'][i] - visits_df['DOB'][i] > threshold else 'Pediatric' for i in
        range(len(visits_df))]

    visits_df['Category'] = [
        visits_df['Age Category'][i] + ' ' + 'PT' if visits_df['Case'][i].strip()[:2] == 'AP' else
        visits_df['Age Category'][i] + ' ' + visits_df['Case'][i].strip()[:2]
        for i in range(len(visits_df))]

    visits_df['Year'] = pd.DatetimeIndex(visits_df['Note Date']).year
    visits_df['Month'] = pd.DatetimeIndex(visits_df['Note Date']).month
    visits_df = visits_df.drop_duplicates(subset=['UniqueID', 'Category', 'Month', 'Year']).reset_index(drop=True)

    # Create a column for the previous month and year
    visits_df['PreviousMonth'] = visits_df['Month'] - 1
    visits_df['PreviousYear'] = visits_df['Year']
    visits_df.loc[visits_df['Month'] == 1, 'PreviousMonth'] = 12
    visits_df.loc[visits_df['Month'] == 1, 'PreviousYear'] -= 1

    # Create a shifted DataFrame for comparison
    shifted_df = visits_df[['UniqueID', 'Category', 'Year', 'Month']].copy()
    shifted_df['Exists'] = True

    # Merge the original DataFrame with the shifted DataFrame
    merged_df = visits_df.merge(
        shifted_df,
        left_on=['UniqueID', 'Category', 'PreviousYear', 'PreviousMonth'],
        right_on=['UniqueID', 'Category', 'Year', 'Month'],
        how='left',
        suffixes=('', '_y')
    )

    # Add a new column to indicate whether the previous entry exists
    visits_df['Previous (Category)'] = merged_df['Exists'].notna()

    # Create a column for the Previous (Ever) check
    visits_df['Previous (Total)'] = False

    existing_records = set(zip(visits_df['UniqueID'], visits_df['Year'], visits_df['Month']))

    visits_df['Previous (Total)'] = [
        (row['UniqueID'], row['PreviousYear'], row['PreviousMonth']) in existing_records
        for _, row in visits_df.iterrows()
    ]

    # Drop the temporary columns
    visits_df.drop(columns=['PreviousMonth', 'PreviousYear'], inplace=True)

    # Sort the DataFrame by 'Unique ID', 'Year', and 'Month'
    visits_df = visits_df.sort_values(by=['UniqueID', 'Year', 'Month', 'Category'])

    # Group by 'Unique ID' and 'Contract Type' and calculate cumulative count of earlier records
    visits_df['Earlier (Category)'] = visits_df.groupby(['UniqueID', 'Category']).cumcount() > 0
    visits_df['Earlier (Total)'] = visits_df.groupby(['UniqueID']).cumcount() > 0
    visits_df.reset_index(inplace=True, drop=True)

    # Work with only columns I require
    paradigm_df = visits_df[
        ['Month', 'Year', 'Category', 'UniqueID', 'First Name', 'Last Name',
         'Previous (Category)',
         'Previous (Total)', 'Earlier (Category)', 'Earlier (Total)']].copy()

    # Get Metrics I need
    paradigm_df['Continued (Category)'] = [1 if paradigm_df['Previous (Category)'][i] == True else 0 for i in
                                           range(len(paradigm_df))]
    paradigm_df['Continued (Total)'] = [1 if paradigm_df['Previous (Total)'][i] == True else 0 for i in
                                        range(len(paradigm_df))]
    paradigm_df['Retained (Category)'] = [
        1 if paradigm_df['Previous (Category)'][i] != True and paradigm_df['Earlier (Category)'][i] == True else 0 for i
        in
        range(len(paradigm_df))]
    paradigm_df['Retained (Total)'] = [
        1 if paradigm_df['Previous (Total)'][i] != True and paradigm_df['Earlier (Total)'][i] == True else 0 for i in
        range(len(paradigm_df))]
    paradigm_df['New (Category)'] = [1 if paradigm_df['Earlier (Category)'][i] != True else 0 for i in
                                     range(len(paradigm_df))]
    paradigm_df['New (Total)'] = [1 if paradigm_df['Earlier (Total)'][i] != True else 0 for i in
                                  range(len(paradigm_df))]

    return paradigm_df
