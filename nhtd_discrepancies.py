import pandas as pd

anchor_active = pd.read_excel(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Anchor).xlsx",
    dtype=str, keep_default_na=False)
abode_active = pd.read_excel(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Abode).xlsx",
    dtype=str, keep_default_na=False)
attentive_active = pd.read_excel(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Billing Report\\Active (Attentive).xlsx",
    dtype=str, keep_default_na=False)

anchor_active = anchor_active.rename(columns={'Total Hours Utilization': 'Total Hours Utilized'})
anchor_active = anchor_active.drop(['Date Added to Sensative', 'Sensitive', 'Sensitive Notes'], axis=1)
abode_active = abode_active.rename(columns={'Hours Utilized %': 'Hours Utilization %'})
abode_active = abode_active.drop('Location', axis=1)
attentive_active = attentive_active.rename(columns={'Addendum type': 'Addendum Type'})
attentive_active = attentive_active.drop('Location', axis=1)

anchor_active['CIN'] = anchor_active['CIN'].str.strip().str.lower()
abode_active['CIN'] = abode_active['CIN'].str.strip().str.lower()
attentive_active['CIN'] = attentive_active['CIN'].str.strip().str.lower()

anchor_abode = anchor_active[anchor_active['SC Agency'].str.strip().str.lower().str.contains('abode')].reset_index(
    drop=True)
anchor_attentive = anchor_active[
    anchor_active['SC Agency'].str.strip().str.lower().str.contains('attentive')].reset_index(drop=True)

abode_active = abode_active[abode_active['HCSS Agency'].str.strip().str.lower().str.contains('anchor')].reset_index(
    drop=True)

attentive_active = attentive_active[
    attentive_active['HCSS Agency'].str.strip().str.lower().str.contains('anchor')].reset_index(drop=True)

headers = anchor_active.columns.tolist()

discrepancies_abode = {}
found = []
for i in range(len(anchor_abode['CIN'])):
    cin = anchor_abode['CIN'][i]
    if abode_active['CIN'].str.contains(cin).any():
        found.append(cin)
        cin_discrepancies = {}
        index = abode_active[abode_active['CIN'] == cin].index[0]
        for header in headers:
            if header == 'ISP':
                anchor_val = 'Present' if anchor_abode[header][i] != '' else 'Missing'
                abode_val = 'Present' if abode_active[header][index] != '' else 'Missing'
            else:
                anchor_val = anchor_abode[header][i]
                abode_val = abode_active[header][index]
            if anchor_val != abode_val:
                if anchor_val.strip().lower() == abode_val.strip().lower():
                    cin_discrepancies[header] = 'formatting'
                else:
                    cin_discrepancies[header] = (f'Anchor: {anchor_val}, Abode: {abode_val}')
    else:
        cin_discrepancies = 'Missing from Abode'

    discrepancies_abode[cin] = cin_discrepancies

for cin in abode_active['CIN']:
    if cin not in found:
        discrepancies_abode[cin] = 'Missing from Anchor'

discrepancies_attentive = {}
found = []
for i in range(len(anchor_attentive['CIN'])):
    cin = anchor_attentive['CIN'][i]
    if attentive_active['CIN'].str.contains(cin).any():
        found.append(cin)
        cin_discrepancies = {}
        index = attentive_active[attentive_active['CIN'] == cin].index[0]
        for header in headers:
            if header == 'ISP':
                anchor_val = 'Present' if anchor_attentive[header][i] != '' else 'Missing'
                attentive_val = 'Present' if attentive_active[header][index] != '' else 'Missing'
            else:
                anchor_val = anchor_attentive[header][i]
                attentive_val = attentive_active[header][index]
            if anchor_val != attentive_val:
                if anchor_val.strip().lower() == attentive_val.strip().lower():
                    cin_discrepancies[header] = 'formatting'
                else:
                    cin_discrepancies[header] = (f'Anchor: {anchor_val}, Attentive: {attentive_val}')
    else:
        cin_discrepancies = 'Missing from Attentive'

    discrepancies_attentive[cin] = cin_discrepancies

for cin in attentive_active['CIN']:
    if cin not in found:
        discrepancies_attentive[cin] = 'Missing from Anchor'

# Separate CINs with nested dicts and CINs with string values
structured_rows_abode = []

# Collect all headers from nested dicts
all_headers = set()
for value in discrepancies_abode.values():
    if isinstance(value, dict):
        all_headers.update(value.keys())

# Sort headers for consistent column order
all_headers = sorted(all_headers)

# Build rows
for cin, value in discrepancies_abode.items():
    row = {'CIN': cin}
    row['Missing'] = value if isinstance(value, str) else ''
    if isinstance(value, dict):
        for header in all_headers:
            row[header] = value.get(header, '')
    else:
        for header in all_headers:
            row[header] = ''
    structured_rows_abode.append(row)

# Create DataFrame
abode_discrepancies = pd.DataFrame(structured_rows_abode)

# Separate CINs with nested dicts and CINs with string values
structured_rows_attentive = []

# Collect all headers from nested dicts
all_headers = set()
for value in discrepancies_attentive.values():
    if isinstance(value, dict):
        all_headers.update(value.keys())

# Sort headers for consistent column order
all_headers = sorted(all_headers)

# Build rows
for cin, value in discrepancies_attentive.items():
    row = {'CIN': cin}
    row['Missing'] = value if isinstance(value, str) else ''
    if isinstance(value, dict):
        for header in all_headers:
            row[header] = value.get(header, '')
    else:
        for header in all_headers:
            row[header] = ''
    structured_rows_attentive.append(row)

# Create DataFrame
attentive_discrepancies = pd.DataFrame(structured_rows_attentive)

abode_path = "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Discrepancies\\abode.xlsx"
abode_discrepancies.to_excel(abode_path, index=False, sheet_name='Sheet1')
attentive_path = "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\NHTD\\Discrepancies\\attentive.xlsx"
attentive_discrepancies.to_excel(attentive_path, index=False, sheet_name='Sheet1')
