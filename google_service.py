import json
import base64
from email.message import EmailMessage

import streamlit as st

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = [
"https://www.googleapis.com/auth/calendar",
"https://www.googleapis.com/auth/gmail.send",
"https://www.googleapis.com/auth/spreadsheets"
]

CALENDAR_ID = "primary"

class GoogleService:

```
def __init__(self):
    self.creds = self._authenticate()

    self.calendar_service = build(
        "calendar",
        "v3",
        credentials=self.creds
    )

    self.gmail_service = build(
        "gmail",
        "v1",
        credentials=self.creds
    )

    self.sheets_service = build(
        "sheets",
        "v4",
        credentials=self.creds
    )

def _authenticate(self):

    service_account_info = json.loads(
        st.secrets["GOOGLE_SERVICE_ACCOUNT"]
    )

    creds = service_account.Credentials.from_service_account_info(
        service_account_info,
        scopes=SCOPES
    )

    return creds

def add_event(self, summary, start_time, end_time, description=""):

    event = {
        "summary": summary,
        "description": description,
        "start": {
            "dateTime": start_time,
            "timeZone": "America/Sao_Paulo"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "America/Sao_Paulo"
        }
    }

    try:

        event = (
            self.calendar_service.events()
            .insert(
                calendarId=CALENDAR_ID,
                body=event
            )
            .execute()
        )

        return event.get("htmlLink")

    except HttpError as error:
        print(error)
        return None

def send_email(self, to, subject, body):

    try:

        message = EmailMessage()

        message.set_content(body)
        message["To"] = to
        message["From"] = "me"
        message["Subject"] = subject

        encoded_message = base64.urlsafe_b64encode(
            message.as_bytes()
        ).decode()

        send_message = (
            self.gmail_service.users()
            .messages()
            .send(
                userId="me",
                body={"raw": encoded_message}
            )
            .execute()
        )

        return send_message

    except HttpError as error:
        print(error)
        return None

def salvar_agendamento_planilha(
    self,
    spreadsheet_id,
    cliente,
    servico,
    data,
    email
):

    values = [
        [
            cliente,
            servico,
            data,
            email
        ]
    ]

    body = {
        "values": values
    }

    self.sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="A:D",
        valueInputOption="RAW",
        body=body
    ).execute()
```
