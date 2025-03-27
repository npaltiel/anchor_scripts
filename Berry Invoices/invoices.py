import pandas as pd
from datetime import datetime, timedelta, date
from pathlib import Path
from emails_sendgrid import send_email
from find_files import find_care_notes, find_invoices

now = datetime.today()
last_friday = now - timedelta(days=(now.weekday() - 4) % 7)
invoice_date = f"{last_friday.month}.{last_friday.day}.{last_friday.year % 100}"

start_date = last_friday - timedelta(days=6)
# Format dates
start_date = start_date.strftime("%m/%d/%Y")
end_date = last_friday.strftime("%m/%d/%Y")

emails_df = pd.read_excel(
    "C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Berry Invoices\\Invoice Wording Lookup.xlsx")

invoice_folder_path = Path(
    f"C:\\Users\\nochum.paltiel\\OneDrive - Anchor Home Health care\\Documents\\Berry Invoices\\{invoice_date}")

duplicates, missing = [], []
for file in invoice_folder_path.iterdir():
    if file.is_file():  # Ensure it's a file
        name = file.name
        if name[-5:] != '2.pdf':
            separated = name.split(' - ')
            if separated[0] == 'Invoice' and separated[1] == invoice_date:
                patient_name = separated[2].split('.')[0]
                filtered_df = emails_df[
                    emails_df['Patient Name'].str.strip().str.lower().str.contains(patient_name.strip().lower(),
                                                                                   na=False)].reset_index(drop=True)
                if len(filtered_df) > 1:
                    # Duplicate Names
                    duplicates.append(patient_name)
                elif len(filtered_df) == 0:
                    # Missing Name
                    missing.append(patient_name)
                else:
                    attachments = [file]
                    # Check if Care Note
                    care_note = find_care_notes(invoice_folder_path, invoice_date, patient_name)
                    if care_note:
                        attachments.append(care_note)
                    invoice2 = find_invoices(invoice_folder_path, invoice_date, patient_name)
                    if invoice2:
                        attachments.append(invoice2)

                    # Send Email
                    addresses = filtered_df['Email Addresses'][0].split(",")
                    addresses.append('berry@anchorhc.org')
                    addresses.append('mushka.krinsky@anchorhc.org')
                    subject = f"{filtered_df['Email Subject'][0]}"
                    body = f"Hi {patient_name.split(" ")[-1]},\n\n{filtered_df['Email Body'][0]}"

                    body = body.replace("XXX", start_date, 1).replace("XXX", end_date, 1)

                    send_email(addresses, subject, body, attachments)

if len(duplicates) + len(missing) > 0:
    missing_text, duplicates_text = '', ''
    if len(missing) > 0:
        missing_text = f'\n\nThe following patient names are missing from the Lookup sheet:\n{", ".join(missing)}'
    if len(duplicates) > 0:
        duplicates_text = f'\n\nThe following patient names appear twice in the Lookup sheet:\n{", ".join(duplicates)}'

    body_start = 'Hi Berry,'
    body_end = '\n\nThanks,\nNochum'

    body = body_start + missing_text + duplicates_text + body_end
    send_email(['berry@anchorhc.org'], 'Missing/Duplicated Invoice Names', body)
