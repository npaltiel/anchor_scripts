import sendgrid
import base64
import os
from sendgrid.helpers.mail import Mail, Email, To, Content, Attachment, FileContent, FileName, FileType, Disposition
from api_key import API_KEY
from pathlib import Path


def send_email(emails: list, subject: str, body: str, file_paths: list = None) -> None:
    sg = sendgrid.SendGridAPIClient(api_key=API_KEY)
    from_email = Email("berry@reports.anchorhc.org")
    to_emails = [To(e.strip()) for e in emails]
    content = Content("text/plain", body)
    mail = Mail(from_email, to_emails, subject, content)

    attachments = []
    if file_paths:
        for file_path in file_paths:
            if file_path:  # Ensure file_path is not None
                with open(file_path, "rb") as file:
                    file_data = file.read()
                    encoded_file = base64.b64encode(file_data).decode()

                # Create SendGrid attachment
                attachment = Attachment(
                    FileContent(encoded_file),
                    FileName(Path(file_path).name),
                    FileType("application/pdf"),  # Change based on file type
                    Disposition("attachment"),
                )
                attachments.append(attachment)

    # Attach file to email
    mail.attachment = attachments

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(f'{emails}: {response.status_code}')
