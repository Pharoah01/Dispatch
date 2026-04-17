# Dispatch

A lightweight Python tool that sends bulk HTML emails via the Gmail API. Load your recipients from a CSV, configure your message and branding, and send personalized emails at scale — no SMTP setup required.

---

## Features

- Sends personalized HTML emails to multiple recipients
- Reads recipient list from a CSV file
- Gmail API OAuth2 authentication (no SMTP)
- Configurable branding (logo, banner)
- Anti-spam delay between sends
- Environment-based configuration via `.env`
- Duplicate email detection — skips repeated entries in CSV with a warning
- Retry with exponential backoff — configurable max retries per recipient
- Send log — results saved to `send_log.csv` after every run
- Plain-text fallback — included alongside HTML for better email client compatibility
- Configurable email subject with `{name}`, `{position}`, `{sender}` placeholders

---

## Project Structure

```
dispatch/
├── script.py           # Main script — builds and sends bulk emails
├── test_run.py         # Quick test to verify Gmail API auth and sending
├── recipients.csv      # Recipient list (name, email, position)
├── send_log.csv        # Auto-generated send report (not committed)
├── credentials.json    # Google OAuth client secret (not committed)
├── token.json          # Cached OAuth token (auto-generated, not committed)
├── .env                # Local environment config (not committed)
├── .env.example        # Example env config
├── requirements.txt    # Python dependencies
└── .gitignore
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/Pharoah01/Dispatch.git
cd Dispatch
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Fill in your values in `.env`:

```env
GOOGLE_CREDENTIALS_FILE=credentials.json
TOKEN_FILE=token.json

SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=Your Organization

INTERVIEW_DATE=Monday, 21 April 2026
INTERVIEW_TIME=10:00 AM IST
INTERVIEW_MODE=Google Meet
MEET_LINK=https://meet.google.com/your-link

BANNER_URL=https://your-domain.com/banner.png
LOGO_URL=https://your-domain.com/logo.png

RECIPIENTS_CSV=recipients.csv
EMAIL_SUBJECT=Message from {sender} | {position}

MAX_RETRIES=3
LOG_FILE=send_log.csv

TEST_RECIPIENT=your_test_email@gmail.com
```

### 4. Add Google OAuth credentials

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Create a project and enable the **Gmail API**
- Create OAuth 2.0 credentials (Desktop app)
- Download the JSON file and set its path in `GOOGLE_CREDENTIALS_FILE`

### 5. Add recipients

Edit `recipients.csv`:

```csv
name,email,position
Jane Doe,jane@example.com,Technical Team
John Smith,john@example.com,Management Team
```

Duplicate emails are automatically skipped with a warning.

---

## Usage

### Send bulk emails

```bash
python script.py
```

On first run, a browser window will open for Gmail OAuth authorization. A `token.json` will be saved for subsequent runs. A `send_log.csv` is generated after each run with the status of every recipient.

### Test the setup

```bash
python test_run.py
```

Sends a plain test email to `TEST_RECIPIENT` to verify your auth and API connection.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GOOGLE_CREDENTIALS_FILE` | Path to OAuth client secret JSON | `credentials.json` |
| `TOKEN_FILE` | Path to cached OAuth token | `token.json` |
| `SENDER_EMAIL` | Gmail address to send from | — |
| `SENDER_NAME` | Display name for sender | — |
| `INTERVIEW_DATE` | Date shown in email body | — |
| `INTERVIEW_TIME` | Time shown in email body | — |
| `INTERVIEW_MODE` | Mode shown in email body | — |
| `MEET_LINK` | Link for the Join button | — |
| `BANNER_URL` | Hosted URL for banner image | — |
| `LOGO_URL` | Hosted URL for logo image | — |
| `RECIPIENTS_CSV` | Path to recipients CSV file | `recipients.csv` |
| `EMAIL_SUBJECT` | Subject template (`{sender}`, `{position}`, `{name}`) | — |
| `MAX_RETRIES` | Max send attempts per recipient | `3` |
| `LOG_FILE` | Path for send report CSV | `send_log.csv` |
| `TEST_RECIPIENT` | Email address for test run | — |

---

## Dependencies

| Package | Version |
|---|---|
| google-api-python-client | 2.127.0 |
| google-auth | 2.29.0 |
| google-auth-httplib2 | 0.2.0 |
| google-auth-oauthlib | 1.2.0 |
| python-dotenv | latest |

---

## Notes

- `credentials.json`, `token.json`, and `send_log.csv` are excluded from version control — never commit them.
- The script adds a random 1.5–3s delay between emails to avoid Gmail rate limits.
- Failed sends are retried with exponential backoff before being marked as failed in the log.
- HTML email template is defined in `script.py` and can be customized freely.

---

## License

MIT — see [LICENSE](LICENSE)
