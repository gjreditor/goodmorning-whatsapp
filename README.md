# Good Morning WhatsApp Bot

This project generates a funny **Good Morning meme** every day using Google Gemini and sends it to WhatsApp via GreenAPI.

## Setup

1. Fork this repo.
2. Go to **Settings → Secrets → Actions** and add:
   - `GEMINI_API_KEY` → Your Google Gemini API Key
   - `GREENAPI_ID` → Your GreenAPI instance ID
   - `GREENAPI_TOKEN` → Your GreenAPI API token
   - `WHATSAPP_NUMBER` → Your WhatsApp number (with country code, e.g. `919876543210`)
3. GitHub Actions will run **daily at 8:30 AM IST** and send the message.

## Manual Run
You can trigger it manually:
- Go to **Actions tab → Daily Good Morning WhatsApp → Run workflow**

## Notes
- Edit `PROMPTS` in `goodmorning.py` to add more funny ideas.
- Timezone can be changed by editing the cron in `.github/workflows/daily_goodmorning.yml`.
