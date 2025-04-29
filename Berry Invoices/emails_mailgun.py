import requests
import base64
import os

from requests import Response

from api_key import APIKEY_MAILGUN, MAILGUN_DOMAIN
from pathlib import Path


def send_mailgun_email(emails: list, subject: str, body: str, file_paths: list = None) -> Response:
    FROM_EMAIL = "berry@reports.anchorhc.org"

    url = f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages"

    # Base payload
    data = {
        "from": FROM_EMAIL,
        "to": emails,
        "subject": subject,
        "text": body,
    }

    files = []

    if file_paths:
        for file_path in file_paths:
            if file_path:  # Ensure file_path is not None
                files.append(
                    ("attachment", (Path(file_path).name, open(file_path, "rb")))
                )

    response = requests.post(
        url,
        auth=("api", APIKEY_MAILGUN),
        data=data,
        files=files if files else None,
    )

    return response
