# Weather + Commute Discord Briefing

Python project that fetches current weather and a short forecast from Open-Meteo,
optionally estimates a car route with TomTom, and posts a formatted briefing to
a Discord channel through a webhook.

## Requirements
- Python 3.10+
- Discord webhook URL
- Optional TomTom API key and route coordinates for traffic

Open-Meteo basic forecast access does not require an API key. Threshold notices
are simple configurable indicators, not official weather or flood alerts.

## Local setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env`, set `DISCORD_WEBHOOK_URL`, `LATITUDE`, and `LONGITUDE`.
For a quick test keep `FORCE_RUN=true`, then run:

```powershell
python main.py
```

After successful testing, set `FORCE_RUN=false` for scheduled execution.

## Environment variables
See `.env.example`. Never commit `.env` or paste webhook/API secrets into source
code or public repositories.

## GitHub Actions
Store `DISCORD_WEBHOOK_URL` and optional `TOMTOM_API_KEY` in repository Actions
Secrets. Store non-secret location/route settings as Actions Variables. The
workflow schedule can be delayed by GitHub; it is not an exact-time guarantee.

## Notes
- TomTom route estimates use car routing. The `TRANSPORT_MODE` setting is
  currently displayed as context only; it does not change TomTom's routing mode.
- No continuous phone GPS is available in a GitHub Actions runner. Configure
  fixed coordinates or update them manually.
