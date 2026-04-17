import os
import base64
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

SCOPES           = ['https://www.googleapis.com/auth/gmail.send']
CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE       = os.getenv("TOKEN_FILE", "token.json")
TEST_RECIPIENT   = os.getenv("TEST_RECIPIENT", "")


def authenticate():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)


def send_test_email(service):
    message = MIMEText("This is a test email from Gmail API.")
    message['to'] = TEST_RECIPIENT
    message['subject'] = "Gmail API Test"

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={'raw': raw}
    ).execute()

    print(" [+] Test email sent!")


if __name__ == "__main__":
    service = authenticate()
    send_test_email(service)
