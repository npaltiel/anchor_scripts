import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from spire.xls import *
from spire.xls.common import *

df_patients = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_contracts = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
prev_df= pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\Visit_Report_6Month.csv")
cur_df = pd.read_csv("C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\Visit_Report_LastMonth.csv")

prev_df = prev_df[prev_df['MissedVisit'] == 'No']
cur_df = cur_df[cur_df['MissedVisit'] == 'No']

# Patient Churn
# Split patient name and admission id
split_df = prev_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
prev_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

split_df = cur_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
cur_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Lookup contracts and patient information from relevant sources
prev_df = pd.merge(prev_df, df_contracts, on='ContractName', how='left')
prev_df['ContractType'] = prev_df['ContractType'].fillna('Unknown')
# Lookup contracts and patient information from relevant sources
cur_df = pd.merge(cur_df, df_contracts, on='ContractName', how='left')
cur_df['ContractType'] = cur_df['ContractType'].fillna('Unknown')

prev_df = pd.merge(prev_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')
cur_df = pd.merge(cur_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

prev_df['MedicaidNo'] = prev_df['MedicaidNo'].str.lstrip('0')
cur_df['MedicaidNo'] = cur_df['MedicaidNo'].str.lstrip('0')

# Create unique ID
prev_df['UniqueID'] = [
    prev_df['MedicaidNo'][i] if pd.notna(prev_df['MedicaidNo'][i]) else prev_df['PatientName'][
                                                                                        i] + str(
        prev_df['DOB'][i]) for i in range(len(prev_df))]

# Create unique ID
cur_df['UniqueID'] = [
    cur_df['MedicaidNo'][i] if pd.notna(cur_df['MedicaidNo'][i]) else cur_df['PatientName'][
                                                                                        i] + str(
        cur_df['DOB'][i]) for i in range(len(cur_df))]

# Create Baby Branch
cur_df['Branch_Updated'] = [
    'Baby' if pd.notna(cur_df['DOB'][i]) and
    datetime.strptime(cur_df['DOB'][i].strip(), "%m/%d/%Y").date() >= date.today() - relativedelta(years=2)
    else cur_df['Branch'][i]
    for i in range(len(cur_df))
]
# Create Baby Branch
prev_df['Branch_Updated'] = [
    'Baby' if pd.notna(prev_df['DOB'][i]) and
    datetime.strptime(prev_df['DOB'][i].strip(), "%m/%d/%Y").date() >= date.today() - relativedelta(years=2)
    else prev_df['Branch'][i]
    for i in range(len(prev_df))
]

# Again drop duplicates based on Unique ID, Category and the Month
prev_df = prev_df.sort_values(by=['VisitDate'])
prev_df = prev_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
cur_df = cur_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

prev_ids = []
for i in range(len(prev_df)):
    prev_ids.append(prev_df['UniqueID'][i])

soc_df = cur_df[~cur_df['UniqueID'].isin(prev_ids)][['AdmissionID','First Name', 'Last Name', 'VisitDate', 'Branch_Updated','ContractName','ContractType','Team','DOB','Status']].copy()
#Output Excel file path
excel_file = 'C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\soc_oct2.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
soc_df.to_excel(excel_file, index=False, sheet_name='Sheet1')


workbook = Workbook()
workbook.LoadFromFile('C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\soc_oct2.xlsx')
data_sheet = workbook.Worksheets[0]
rnge = 'A1:I'+str(len(soc_df)+1)
cellRange = data_sheet.Range[rnge]

pivotCache = workbook.PivotCaches.Add(cellRange)
pivot_sheet = workbook.Worksheets.Add("Pivot")
pivotTable = pivot_sheet.PivotTables.Add("Pivot Table", pivot_sheet.Range["C6"], pivotCache)
pivotTable.Options.RowHeaderCaption = "Row Labels"
regionField = pivotTable.PivotFields["Team"]
regionField.Axis = AxisTypes.Row
productField = pivotTable.PivotFields["Status"]
productField.Axis = AxisTypes.Column
pivotTable.DataFields.Add(pivotTable.PivotFields["AdmissionID"], "SOC Count", SubtotalTypes.Count)
pivotTable.CalculateData()
teamField = pivotTable.PivotFields["Team"]
teamField.SortType = PivotFieldSortType.Ascending

pivotTable.BuiltInStyle = PivotBuiltInStyles.PivotStyleMedium11
workbook.SaveToFile('C:\\Users\\Nochum\\OneDrive\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\soc_oct2.xlsx', ExcelVersion.Version2016)
workbook.Dispose()