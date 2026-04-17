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

---

## Project Structure

```
dispatch/
├── script.py           # Main script — builds and sends bulk emails
├── test_run.py         # Quick test to verify Gmail API auth and sending
├── recipients.csv      # Recipient list (name, email, position)
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
git clone https://github.com/your-username/dispatch.git
cd dispatch
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
```

- `GOOGLE_CREDENTIALS_FILE` — path to your downloaded Google OAuth client secret JSON
- `TOKEN_FILE` — path where the OAuth token will be cached after first login (default: `token.json`)

> All other config (sender info, branding URLs, email content) is set directly in `script.py` under the `# --- CONFIG ---` section.

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

---

## Usage

### Send bulk emails

```bash
python script.py
```

On first run, a browser window will open for Gmail OAuth authorization. A `token.json` will be saved for subsequent runs.

### Test the setup

```bash
python test_run.py
```

Sends a plain test email to verify your auth and API connection.

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

- `credentials.json` and `token.json` are excluded from version control — never commit them.
- The script adds a random 1.5–3s delay between emails to avoid Gmail rate limits.
- HTML email template is defined in `script.py` and can be customized freely.

---

## License

MIT — see [LICENSE](LICENSE)
