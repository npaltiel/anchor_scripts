import pandas as pd
import sqlite3
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

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


df_1 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_2023.csv")
df_2 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_Jan_June.csv")
df_lehigh = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_Lehigh.csv",dtype={'MedicaidNo': 'S10'})
df_lehigh['MedicaidNo'] = df_lehigh['MedicaidNo'].astype(str)

df_lehigh['ContractName'] = ['PA' for _ in range(len(df_lehigh))]

df_3 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_2022.csv")
df_4 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_2021.csv")
df_5 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_2020.csv")
df_6 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_2019.csv")
df_7 = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_July_Oct28.csv")

#visits_df = pd.read_csv("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visit_Report_July_Oct28.csv")
visits_df = pd.concat([df_1, df_2, df_3, df_4, df_5, df_6, df_7, df_lehigh])

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.replace(r'\.0$', '', regex=True)
visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

conn = sqlite3.connect("C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Visits\\Visits.db")

visits_df.to_sql("visits", conn, if_exists='replace', index=False)
# insert_or_replace("visits", visits_df, conn)

conn.close()

