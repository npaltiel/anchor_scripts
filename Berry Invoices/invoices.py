import pandas as pd
from pathlib import Path
from emails_mailgun import send_mailgun_email
from find_files import find_care_notes, find_invoices
import time
from datetime import datetime, timedelta, date

# =============== SETTINGS ================
MAX_RETRIES = 2  # How many times to retry failed sends
PAUSE_BETWEEN_RETRIES = 10  # Seconds to wait between retry rounds

# =============== LOAD DATA ================
now = datetime.today()
last_friday = now - timedelta(days=(now.weekday() - 4) % 7 + 7)
# invoice_date = f"{last_friday.month}.{last_friday.day}.{last_friday.year % 100}"
invoice_date = '04.10.26'

start_date = (last_friday - timedelta(days=6)).strftime("%m/%d/%Y")
end_date = last_friday.strftime("%m/%d/%Y")

emails_df = pd.read_excel(
    "C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Berry Invoices\\Invoice Wording Lookup.xlsx")

invoice_folder_path = Path(
    f"C:\\Users\\nochu\\OneDrive - Anchor Home Health care\\Documents\\Berry Invoices\\{invoice_date}")

sent_already = {}

# =============== PROCESS INVOICES ================
success_log = []
retry_list = []
error_log = []

duplicates, missing = [], []

for file in invoice_folder_path.iterdir():
    if file.is_file() and not file.name.endswith('2.pdf'):  # Ensure it's a file
        separated = file.name.split(' - ')
        if separated[0] == 'Invoice' and separated[1] == invoice_date:
            patient_name = separated[2].split('.')[0]
            filtered_df = emails_df[
                emails_df['Patient Name'].str.strip().str.lower().str.contains(patient_name.strip().lower(), na=False)
            ].reset_index(drop=True)

            if len(filtered_df) > 1:
                # Duplicate Names
                duplicates.append(patient_name)
                continue
            elif len(filtered_df) == 0:
                # Missing Name
                missing.append(patient_name)
                continue

            attachments = [file]
            # Check if Care Note
            care_note = find_care_notes(invoice_folder_path, invoice_date, patient_name)
            care_note2 = find_care_notes(invoice_folder_path, invoice_date, patient_name, True)
            invoice2 = find_invoices(invoice_folder_path, invoice_date, patient_name)
            if care_note:
                attachments.append(care_note)
            if care_note2:
                attachments.append(care_note2)
            if invoice2:
                attachments.append(invoice2)

            # Send Email
            try:
                addresses = filtered_df['Email Addresses'][0].split(",")
            except:
                missing.append(patient_name)
                continue
            addresses = [addr.strip() for addr in addresses]
            addresses += [
                'berry@anchorhc.org',
                'keyla.perez@anchorhc.org',
                'ingrid.p@anchorhc.org'
            ]

            subject = f"{filtered_df['Email Subject'][0]}"
            body = f"Hi {patient_name.split(' ')[-1]},\n\n{filtered_df['Email Body'][0]}"
            body = body.replace("XXX", start_date, 1).replace("XXX", end_date, 1)

            if patient_name in sent_already:
                print(f"Skipping {patient_name} (already sent)")
                continue

            try:
                response = send_mailgun_email(addresses, subject, body, attachments)
                if response.status_code == 200:
                    success_log.append({'patient': patient_name, 'subject': subject, 'status': 'Success'})
                else:
                    retry_list.append((patient_name, addresses, subject, body, attachments, response.text))
            except Exception as e:
                retry_list.append((patient_name, addresses, subject, body, attachments, str(e)))

# =============== RETRY LOGIC ================
for attempt in range(MAX_RETRIES):

    if not retry_list:
        break

    time.sleep(PAUSE_BETWEEN_RETRIES)

    print(f"🔄 Retry round {attempt + 1} starting for {len(retry_list)} emails...")
    new_retry_list = []

    for patient_name, addresses, subject, body, attachments, previous_error in retry_list:
        try:
            response = send_mailgun_email(addresses, subject, body, attachments)
            if response.status_code == 200:
                success_log.append(
                    {'patient': patient_name, 'subject': subject, 'status': f'Retry Success {attempt + 1}'})
            else:
                new_retry_list.append((patient_name, addresses, subject, body, attachments, response.text))
        except Exception as e:
            new_retry_list.append((patient_name, addresses, subject, body, attachments, str(e)))

    retry_list = new_retry_list
    print(f"🔄 Retry round {attempt + 1} complete. Remaining: {len(retry_list)}")

# Anything still left after retries goes to error log
for patient_name, addresses, subject, body, attachments, final_error in retry_list:
    error_log.append(
        {'patient': patient_name, 'subject': subject, 'status': 'Failed after retries', 'error': final_error})

# =============== REPORTING ================
print(f"\n✅ Successfully sent {len(success_log)} emails.")
print(f"❌ Failed to send {len(error_log)} emails.")

if error_log:
    for err in error_log:
        print(f"Error sending to {err['patient']}: {err['error']}")

if len(duplicates) + len(missing) > 0:
    missing_text = f"\n\nMissing names:\n{', '.join(missing)}" if missing else ''
    duplicates_text = f"\n\nDuplicate names:\n{', '.join(duplicates)}" if duplicates else ''

    body_start = 'Hi Ingrid,'
    body_end = '\n\nThanks,\nNochum'

    body = body_start + missing_text + duplicates_text + body_end
    send_mailgun_email(['ingrid.p@anchorhc.org'], 'Missing/Duplicated Invoice Names', body)
