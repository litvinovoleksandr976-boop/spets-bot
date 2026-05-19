# Spets Security CCTV Bot

Telegram bot for automated CCTV quote generation.
Built for Spets Security LTD (UK).

## What it does

1. Customer messages bot on Telegram
2. Bot asks 8 questions (name, phone, email, address, object type, cameras, tier, archive)
3. Auto-calculates components (NVR, HDD, Deep Base, installation)
4. Generates branded PDF quote
5. Emails PDF to customer (via SendGrid)
6. Sends quote in Telegram chat too (backup)
7. Notifies admin in Telegram

## Stack

- Python 3.10
- python-telegram-bot 20.7
- ReportLab 4.1 (PDF)
- Resend HTTP API (email — Railway blocks SMTP). Free 100/day, 3000/month.

## Files

| File | Purpose |
|---|---|
| `bot.py` | Telegram conversation flow |
| `pricing.py` | All CCTV prices + auto-selection logic |
| `quote_generator.py` | PDF generation (styled like invoice #183) |
| `email_sender.py` | Resend email + Telegram admin notify |
| `requirements.txt` | Dependencies |
| `runtime.txt` | Python 3.10.13 (Railway) |
| `Procfile` | Railway start command |
| `.env.example` | Env variable template |

## Deploy on Railway

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Spets bot v2 — CCTV calculator"
git remote add origin https://github.com/litvinovoleksandr976-boop/spets-bot.git
git branch -M main
git push -u origin main --force
```

### 2. Railway project

1. Railway → Open existing `spets-bot` project (or New from GitHub)
2. Connect this repo
3. **Variables** tab — add:
   - `TELEGRAM_TOKEN` — new token from @BotFather
   - `ADMIN_CHAT_ID` — your Telegram chat ID (get from @userinfobot)
   - `RESEND_API_KEY` — from resend.com → API Keys (starts with `re_`)
   - `SENDER_EMAIL` — `onboarding@resend.dev` (test domain, no DNS needed)
   - `SENDER_NAME` — `Spets Security LTD`
   - `REPLY_TO_EMAIL` — `r.brain@spetstech.co.uk` (where customer replies go)
4. Deploy

### 3. Get admin chat ID

1. Open Telegram → search for `@userinfobot`
2. Send `/start`
3. It replies with your numeric ID
4. Use as `ADMIN_CHAT_ID`

### 4. Resend setup (test domain — works immediately)

We start with Resend's free test domain `onboarding@resend.dev`. No DNS
configuration needed — emails are sent immediately after you set the API key.

Customers receive emails from:
```
From: Spets Security LTD <onboarding@resend.dev>
Reply-To: r.brain@spetstech.co.uk
```

When customers click "Reply", their reply goes to your real email
(`r.brain@spetstech.co.uk` by default — change `REPLY_TO_EMAIL` env var
to set a different reply address, e.g. `spets.services@gmail.com`).

**Later (production):** Move domain DNS to Cloudflare → verify
`spetstech.co.uk` in Resend → change `SENDER_EMAIL` env var to
`r.brain@spetstech.co.uk`. No code changes needed.

## Local testing

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with real values
export $(cat .env | xargs)
python bot.py
```

## Future (Phase 2 — n8n)

Bot will POST quote data to n8n webhook → n8n creates client in KeyCRM,
sends follow-up emails, manages pipeline status.

## Troubleshooting

**"Conflict: terminated by other getUpdates request"** — bot is running on
two Railway instances. Open in browser:
```
https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true
```
Then restart the service.

**Email not delivered** — check Resend dashboard → Logs. Most likely
sender domain not verified, or API key has insufficient permissions.

## Contact

Spets Security LTD
- 📞 +44 7706 906079
- 📧 r.brain@spetstech.co.uk
- 📍 1 Oakcroft Road, Chessington, Surrey, KT9 1BD
