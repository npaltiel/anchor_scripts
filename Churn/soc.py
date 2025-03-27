import pandas as pd
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from spire.xls import *
from spire.xls.common import *

df_patients = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\List of Patients.csv")
df_contracts = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\General Information\\Contract Lookup.csv")
visits_df = pd.read_csv(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\Visit_Report_7Month.csv",
    low_memory=False)

visits_df = visits_df[visits_df['MissedVisit'] == 'No']
visits_df = visits_df[pd.notna(visits_df['VisitTime'])]

# Patient Churn
# Split patient name and admission id
split_df = visits_df['PatientName'].str.split('(', expand=True)
split_df[1] = split_df[1].str.replace(')', '')
visits_df[['PatientName', 'AdmissionID']] = split_df[[0, 1]]

# Lookup contracts and patient information from relevant sources
visits_df = pd.merge(visits_df, df_contracts, on='ContractName', how='left')
visits_df['ContractType'] = visits_df['ContractType'].fillna('Unknown')

visits_df = pd.merge(visits_df, df_patients, left_on='AdmissionID', right_on='Admission ID - Office', how='left')

visits_df['MedicaidNo'] = visits_df['MedicaidNo'].str.lstrip('0')

# Create unique ID
visits_df['UniqueID'] = [
    visits_df['MedicaidNo'][i] if pd.notna(visits_df['MedicaidNo'][i]) else visits_df['PatientName'][
                                                                                i] + str(
        visits_df['DOB'][i]) for i in range(len(visits_df))]

# Create Baby Branch
visits_df['Branch_Updated'] = [
    'Baby' if pd.notna(visits_df['DOB'][i]) and
              datetime.strptime(visits_df['DOB'][i].strip(),
                                "%m/%d/%Y %H:%M:%S %p").date() >= date.today() - relativedelta(years=2)
    else visits_df['Branch'][i]
    for i in range(len(visits_df))
]

today = datetime.now()
sixteenth_of_previous_month = (today.replace(day=1) - pd.DateOffset(months=1)).replace(day=16).date()

visits_df['VisitDate'] = pd.to_datetime(visits_df['VisitDate'], errors='coerce')
prev_df = visits_df[visits_df['VisitDate'] < pd.Timestamp(sixteenth_of_previous_month)]
cur_df = visits_df[visits_df['VisitDate'] >= pd.Timestamp(sixteenth_of_previous_month)]

# Drop duplicates based on Unique ID
prev_df = prev_df.sort_values(by=['VisitDate'])
prev_df = prev_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)
cur_df = cur_df.drop_duplicates(subset=['UniqueID']).reset_index(drop=True)

prev_ids = []
for i in range(len(prev_df)):
    prev_ids.append(prev_df['UniqueID'][i])

soc_df = cur_df[~cur_df['UniqueID'].isin(prev_ids)][
    ['AdmissionID', 'First Name', 'Last Name', 'VisitDate', 'Branch_Updated', 'ContractName', 'ContractType', 'Team',
     'DOB', 'Status']].copy()

soc_df.rename(columns={'VisitDate': 'FirstVisitDate'}, inplace=True)

# Output Excel file path
month = datetime.today().strftime('%b')
year = datetime.today().strftime('%Y')
excel_file = f'C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Churn Report\\SOC\\soc_{month}_{year}.xlsx'
# Name, Branch, Contract Type, Contract, Team, DOB, Admission ID, Status
soc_df.to_excel(excel_file, index=False, sheet_name='Sheet1')

workbook = Workbook()
workbook.LoadFromFile(excel_file)
data_sheet = workbook.Worksheets[0]
rnge = 'A1:J' + str(len(soc_df) + 1)
cellRange = data_sheet.Range[rnge]

pivotCache = workbook.PivotCaches.Add(cellRange)
pivot_sheet = workbook.Worksheets.Add("Pivot")
pivotTable = pivot_sheet.PivotTables.Add("Pivot Table", pivot_sheet.Range["B3"], pivotCache)
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
workbook.SaveToFile(excel_file, ExcelVersion.Version2016)
workbook.Dispose()
