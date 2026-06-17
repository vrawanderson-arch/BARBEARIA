import os.path
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Escopos necessários para Calendar e Gmail
SCOPES = [
    'https://www.googleapis.com/auth/calendar',
    'https://www.googleapis.com/auth/gmail.send'
]

class GoogleService:
    def __init__(self):
        self.creds = self._authenticate()
        self.calendar_service = build('calendar', 'v3', credentials=self.creds)
        self.gmail_service = build('gmail', 'v1', credentials=self.creds)

    def _authenticate(self):
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists('credentials.json'):
                    raise FileNotFoundError("Arquivo 'credentials.json' não encontrado. Siga o guia no README.")
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        return creds

    def add_event(self, summary, start_time, end_time, description=""):
        """Adiciona evento ao Google Calendar"""
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'America/Sao_Paulo'},
            'end': {'dateTime': end_time, 'timeZone': 'America/Sao_Paulo'},
        }
        try:
            event = self.calendar_service.events().insert(calendarId='primary', body=event).execute()
            return event.get('htmlLink')
        except HttpError as error:
            print(f'Erro ao criar evento: {error}')
            return None

    def send_email(self, to, subject, body):
        """Envia e-mail automático via Gmail"""
        try:
            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['From'] = 'me'
            message['Subject'] = subject

            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
            create_message = {'raw': encoded_message}
            
            send_message = (self.gmail_service.users().messages().send(userId="me", body=create_message).execute())
            return send_message
        except HttpError as error:
            print(f'Erro ao enviar e-mail: {error}')
            return None
