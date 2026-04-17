import os
import csv
import base64
import time
import random
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()
# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

INTERVIEW_DATE = "Monday, 21 April 2026"
INTERVIEW_TIME = "10:00 AM IST"
INTERVIEW_MODE = "Google Meet"
MEET_LINK      = "LINK_TO_BE_PROVIDED"


BANNER_URL = "BANNER_LINK(HOSTED)"
LOGO_URL   = "LOGO_LINK(HOSTED)"

SENDER_EMAIL = "elavarasanjaswanth001@gmail.com"
SENDER_NAME  = "OWASP Student Chapter, Sathyabama"


# --- MODEL ---
@dataclass
class Recipient:
    name: str
    email: str
    position: str


# --- LOAD CSV ---
def load_recipients(file_path: str) -> List[Recipient]:
    recipients = []
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            recipients.append(Recipient(
                name=row["name"].strip(),
                email=row["email"].strip(),
                position=row["position"].strip()
            ))
    return recipients


# --- AUTH ---
def authenticate():
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return build('gmail', 'v1', credentials=creds)

# --- HTML BODY ---
def create_message(recipient: Recipient):

    subject = f"Interview Invitation | {recipient.position} | OWASP Student Chapter"

    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0; padding:0; background:#f3f4f6; font-family:Arial;">

        <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px;">
            <tr>
                <td align="center">

                    <table width="600" style="background:#ffffff; border-radius:10px; overflow:hidden;">

                        <!-- LOGO -->
                        <tr>
                            <td style="text-align:center; padding:15px;">
                                <img src="{LOGO_URL}" width="120" style="display:block; margin:auto;">
                            </td>
                        </tr>

                        <!-- BANNER -->
                        <tr>
                            <td>
                                <img src="{BANNER_URL}" width="600"
                                     style="display:block; width:100%;">
                            </td>
                        </tr>

                        <!-- HEADER -->
                        <tr>
                            <td style="background:#1e3a5f; padding:20px; text-align:center;">
                                <h2 style="color:white; margin:0;">OWASP Student Chapter</h2>
                                <p style="color:#cbd5f5; margin:5px 0;">Sathyabama</p>
                            </td>
                        </tr>

                        <!-- BODY -->
                        <tr>
                            <td style="padding:30px;">

                                <p>Dear {recipient.name},</p>

                                <p>
                                    Greetings from <b>OWASP Student Chapter, Sathyabama</b>!
                                </p>

                                <p>
                                    You have been shortlisted for the interview round for the 
                                    <b>{recipient.position}</b>.
                                </p>

                                <table width="100%" cellpadding="10"
                                       style="background:#eff6ff; border-left:4px solid #2563eb; margin:20px 0;">
                                    <tr>
                                        <td>
                                            <b>Mode:</b> {INTERVIEW_MODE}<br>
                                            <b>Date:</b> {INTERVIEW_DATE}<br>
                                            <b>Time:</b> {INTERVIEW_TIME}<br><br>

                                            <a href="{MEET_LINK}"
                                               style="background:#2563eb; color:white;
                                                      padding:10px 15px; text-decoration:none;
                                                      border-radius:5px;">
                                                Join Interview
                                            </a>
                                        </td>
                                    </tr>
                                </table>

                                <p>Please confirm your availability by replying.</p>

                                <p>We look forward to speaking with you.</p>

                                <p>
                                    Regards,<br>
                                    <b>OWASP Student Chapter</b>
                                </p>

                            </td>
                        </tr>

                        <!-- FOOTER -->
                        <tr>
                            <td style="background:#f9fafb; padding:15px; text-align:center;
                                       font-size:12px; color:#888;">
                                OWASP Student Chapter · Sathyabama
                            </td>
                        </tr>

                    </table>

                </td>
            </tr>
        </table>

    </body>
    </html>
    """

    message = MIMEMultipart("alternative")
    message['to'] = f"{recipient.name} <{recipient.email}>"
    message['from'] = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message['subject'] = subject

    message.attach(MIMEText(html, 'html'))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


# --- SEND ---
def send_email(service, recipient: Recipient):
    try:
        msg = create_message(recipient)

        service.users().messages().send(
            userId='me',
            body=msg
        ).execute()

        print(f" [+] Sent --> {recipient.name} ({recipient.email})")

        # Anti-spam delay
        time.sleep(random.uniform(1.5, 3))

    except Exception as e:
        print(f" [+] Failed --> {recipient.email} | {e}")


# --- SEND BULK ---
def send_bulk(csv_file: str):
    service = authenticate()
    recipients = load_recipients(csv_file)

    print(f" [+] ... Sending to {len(recipients)} recipients ...\n")

    for r in recipients:
        send_email(service, r)

    print("\n [+] All emails processed.")


if __name__ == "__main__":
    send_bulk("recipients.csv")