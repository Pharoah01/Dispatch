import os
import csv
import base64
import time
import random
import logging
from dataclasses import dataclass, field
from typing import List, Set
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

load_dotenv()

# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

CREDENTIALS_FILE = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
TOKEN_FILE       = os.getenv("TOKEN_FILE", "token.json")
SENDER_EMAIL     = os.getenv("SENDER_EMAIL", "")
SENDER_NAME      = os.getenv("SENDER_NAME", "")

INTERVIEW_DATE = os.getenv("INTERVIEW_DATE", "")
INTERVIEW_TIME = os.getenv("INTERVIEW_TIME", "")
INTERVIEW_MODE = os.getenv("INTERVIEW_MODE", "")
MEET_LINK      = os.getenv("MEET_LINK", "")

BANNER_URL     = os.getenv("BANNER_URL", "")
LOGO_URL       = os.getenv("LOGO_URL", "")

RECIPIENTS_CSV = os.getenv("RECIPIENTS_CSV", "recipients.csv")
EMAIL_SUBJECT  = os.getenv("EMAIL_SUBJECT", "Message from {sender} | {position}")

MAX_RETRIES    = int(os.getenv("MAX_RETRIES", "3"))
LOG_FILE       = os.getenv("LOG_FILE", "send_log.csv")

# --- LOGGING ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)


# --- MODEL ---
@dataclass
class Recipient:
    name: str
    email: str
    position: str


@dataclass
class SendResult:
    name: str
    email: str
    position: str
    status: str
    error: str = ""


# --- LOAD CSV ---
def load_recipients(file_path: str) -> List[Recipient]:
    recipients = []
    seen: Set[str] = set()

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["email"].strip().lower()
            if email in seen:
                log.warning(f"Duplicate skipped: {email}")
                continue
            seen.add(email)
            recipients.append(Recipient(
                name=row["name"].strip(),
                email=email,
                position=row["position"].strip()
            ))
    return recipients


# --- AUTH ---
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


# --- BUILD MESSAGE ---
def create_message(recipient: Recipient):
    subject = EMAIL_SUBJECT.format(
        sender=SENDER_NAME,
        position=recipient.position,
        name=recipient.name
    )

    plain = (
        f"Dear {recipient.name},\n\n"
        f"Greetings from {SENDER_NAME}!\n\n"
        f"Position: {recipient.position}\n"
        f"Mode: {INTERVIEW_MODE}\n"
        f"Date: {INTERVIEW_DATE}\n"
        f"Time: {INTERVIEW_TIME}\n"
        f"Link: {MEET_LINK}\n\n"
        f"Please confirm your availability by replying.\n\n"
        f"Regards,\n{SENDER_NAME}"
    )

    html = f"""<!DOCTYPE html>
<html>
<body style="margin:0; padding:0; background:#f3f4f6; font-family:Arial;">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:30px;">
    <tr><td align="center">
      <table width="600" style="background:#ffffff; border-radius:10px; overflow:hidden;">

        <!-- LOGO -->
        <tr><td style="text-align:center; padding:15px;">
          <img src="{LOGO_URL}" width="120" style="display:block; margin:auto;">
        </td></tr>

        <!-- BANNER -->
        <tr><td>
          <img src="{BANNER_URL}" width="600" style="display:block; width:100%;">
        </td></tr>

        <!-- HEADER -->
        <tr><td style="background:#1e3a5f; padding:20px; text-align:center;">
          <h2 style="color:white; margin:0;">{SENDER_NAME}</h2>
        </td></tr>

        <!-- BODY -->
        <tr><td style="padding:30px;">
          <p>Dear {recipient.name},</p>
          <p>Greetings from <b>{SENDER_NAME}</b>!</p>
          <p>You have been shortlisted for the <b>{recipient.position}</b>.</p>

          <table width="100%" cellpadding="10"
                 style="background:#eff6ff; border-left:4px solid #2563eb; margin:20px 0;">
            <tr><td>
              <b>Mode:</b> {INTERVIEW_MODE}<br>
              <b>Date:</b> {INTERVIEW_DATE}<br>
              <b>Time:</b> {INTERVIEW_TIME}<br><br>
              <a href="{MEET_LINK}"
                 style="background:#2563eb; color:white; padding:10px 15px;
                        text-decoration:none; border-radius:5px;">
                Join Interview
              </a>
            </td></tr>
          </table>

          <p>Please confirm your availability by replying.</p>
          <p>Regards,<br><b>{SENDER_NAME}</b></p>
        </td></tr>

        <!-- FOOTER -->
        <tr><td style="background:#f9fafb; padding:15px; text-align:center;
                       font-size:12px; color:#888;">
          {SENDER_NAME}
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""

    message = MIMEMultipart("alternative")
    message['to']      = f"{recipient.name} <{recipient.email}>"
    message['from']    = f"{SENDER_NAME} <{SENDER_EMAIL}>"
    message['subject'] = subject

    message.attach(MIMEText(plain, 'plain'))
    message.attach(MIMEText(html, 'html'))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}


# --- SEND WITH RETRY ---
def send_email(service, recipient: Recipient) -> SendResult:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            msg = create_message(recipient)
            service.users().messages().send(userId='me', body=msg).execute()
            log.info(f"Sent [{attempt}/{MAX_RETRIES}] --> {recipient.name} ({recipient.email})")
            time.sleep(random.uniform(1.5, 3))
            return SendResult(recipient.name, recipient.email, recipient.position, "success")

        except Exception as e:
            log.warning(f"Attempt {attempt} failed for {recipient.email}: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(2 ** attempt)  # exponential backoff

    log.error(f"All retries failed --> {recipient.email}")
    return SendResult(recipient.name, recipient.email, recipient.position, "failed", str(e))


# --- WRITE LOG ---
def write_log(results: List[SendResult]):
    with open(LOG_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "position", "status", "error"])
        for r in results:
            writer.writerow([r.name, r.email, r.position, r.status, r.error])
    log.info(f"Send log saved to {LOG_FILE}")


# --- SEND BULK ---
def send_bulk(csv_file: str):
    service    = authenticate()
    recipients = load_recipients(csv_file)
    results    = []

    log.info(f"Sending to {len(recipients)} recipients...")

    for r in recipients:
        results.append(send_email(service, r))

    sent   = sum(1 for r in results if r.status == "success")
    failed = sum(1 for r in results if r.status == "failed")

    log.info(f"Done. {sent} sent, {failed} failed.")
    write_log(results)


if __name__ == "__main__":
    send_bulk(RECIPIENTS_CSV)
