
# 🌤️ Weather & Commute Briefing Bot

A Python-based automation that delivers a concise daily weather and commute briefing to Discord.

The bot fetches weather forecasts for configured cities, checks travel time between selected locations using TomTom, and uses Groq AI to generate a short, easy-to-understand weather summary and alert.

Designed to help you quickly understand the weather at home, the weather at your destination, and the expected commute time — without reading a lengthy report.

---

## ✨ Features

- **Multi-city weather monitoring** using the Open-Meteo API.
- **Commute time estimation** using TomTom Routing API.
- **AI-generated weather summaries** using Groq.
- **Concise Discord notifications** with a simple, readable format.
- **Weather alerts** based on configurable thresholds.
- **Configurable locations and routes** through environment variables.
- **Graceful fallback** when Groq AI is unavailable.
- **Environment-based configuration** to keep API keys out of source code.

---

## 📍 Current Configuration

The current setup monitors:

| Location | Purpose |
|---|---|
| Erode | Home |
| Bangalore | Office |

Configured commute route:

**Home to Office — Erode → Bangalore**

City coordinates:

| City | Latitude | Longitude |
|---|---:|---:|
| Erode | 11.3410 | 77.7172 |
| Bangalore | 12.9716 | 77.5946 |

You can change the cities and route through the `.env` file.

---

## 🛠️ Tech Stack

- **Python** — Application logic
- **Open-Meteo API** — Weather forecasts
- **TomTom Routing API** — Route travel-time estimates
- **Groq API** — AI-generated weather insights
- **Discord Webhook** — Notification delivery
- **python-dotenv** — Environment variable management
- **GitHub Actions** — Optional scheduled execution

---

## 📂 Project Structure

```text
weather-commute-bot/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── weather.py
│   ├── traffic.py
│   ├── ai_insights.py
│   ├── formatter.py
│   ├── discord_client.py
│   └── main.py
│
├── .github/
│   └── workflows/
│       └── daily-briefing.yml
│
├── main.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Prerequisites

Before running the project, make sure you have:

- Python 3.10 or later
- A Discord webhook URL
- A Groq API key
- A TomTom API key for commute information
- Git (optional, for version control)

Weather data is retrieved from Open-Meteo.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/weather-commute-bot.git
cd weather-commute-bot
```

Replace `YOUR_USERNAME` with your GitHub username and use your repository name.

### 2. Create a virtual environment

**Windows PowerShell**

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root.

```dotenv
# --------------------------------------------------
# Discord
# --------------------------------------------------

DISCORD_WEBHOOK_URL=your_discord_webhook_url


# --------------------------------------------------
# Groq AI
# --------------------------------------------------

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
ENABLE_GROQ_INSIGHTS=true


# --------------------------------------------------
# TomTom
# --------------------------------------------------

TOMTOM_API_KEY=your_tomtom_api_key


# --------------------------------------------------
# Cities
# --------------------------------------------------

CITIES=Erode,Bangalore

CITY_ERODE_LAT=11.3410
CITY_ERODE_LON=77.7172

CITY_BANGALORE_LAT=12.9716
CITY_BANGALORE_LON=77.5946


# --------------------------------------------------
# Commute Route
# --------------------------------------------------

TEST_ALL_DIRECTED_ROUTES=false
ROUTES=Erode>Bangalore
ROUTE_DISPLAY_NAME=Home to Office


# --------------------------------------------------
# Schedule
# --------------------------------------------------

TIMEZONE=Asia/Kolkata
RUN_HOUR=7
FORCE_RUN=true


# --------------------------------------------------
# Alert Thresholds
# --------------------------------------------------

RAIN_ALERT_MM=20
RAIN_PROBABILITY_ALERT_PERCENT=60
HEAT_ALERT_C=38
FEELS_LIKE_ALERT_C=40
COLD_ALERT_C=10
WIND_ALERT_KMH=50
```

**Important:** Use the exact environment variable names expected by your `app/config.py`. If your configuration uses different names, update the `.env` entries to match it.

Do not commit your actual `.env` file or expose API keys publicly.

---

## ▶️ Run the Bot

From the project root directory:

```bash
python main.py
```

To test immediately, set:

```dotenv
FORCE_RUN=true
```

When `FORCE_RUN=false`, the application runs only during the configured `RUN_HOUR`, according to the configured timezone.

---

## 💬 Sample Discord Notification

```text
🌤️ Daily Weather & Commute Brief
Tuesday, 29 September 2026 · 07:00 AM IST

🏠 Home — Erode: 29.9°C · Feels like 33.5°C · Light rain
🏢 Office — Bangalore: 24.8°C · Feels like 25.2°C · Cloudy

🌦️ Weather: Rain is possible in Erode, while Bangalore is expected to remain mostly cloudy.

🚗 Home to Office: Erode → Bangalore · Approx. 6 hr 20 min · 15 min above usual

⚠️ Alert: Carry rain protection if travelling from Erode.
```

*Sample values are illustrative. Actual weather and travel times depend on API responses.*

---

## 🧠 How It Works

```text
                 ┌──────────────────────┐
                 │    Scheduled Run     │
                 │   or Manual Run      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Load .env Settings   │
                 └──────────┬───────────┘
                            │
              ┌─────────────┴─────────────┐
              ▼                           ▼
   ┌────────────────────┐     ┌────────────────────┐
   │ Open-Meteo API     │     │ TomTom Routing API │
   │ Fetch City Weather │     │ Fetch Commute Time │
   └──────────┬─────────┘     └──────────┬─────────┘
              │                           │
              └─────────────┬─────────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Groq AI Summary      │
                 │ Weather + Alert      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Format Briefing      │
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Discord Webhook      │
                 │ Deliver Notification │
                 └──────────────────────┘
```

---

## 🔔 Weather Alerts

The bot uses configurable thresholds to identify noteworthy conditions, such as:

- High forecast rainfall
- High probability of rain
- High temperature
- High feels-like temperature
- Low temperature
- Strong winds

These are informational notifications, not official weather warnings.

---

## 🚗 Commute Information

The commute section reports the estimated travel time for the configured route.

When baseline information is configured, the briefing can also show whether the current estimate is above or below the usual travel time.

A difference from the baseline is not necessarily the same as a live traffic delay. The message distinguishes these values when available.

---

## 🧪 Testing Multiple Routes

To test all directed routes between configured cities:

```dotenv
TEST_ALL_DIRECTED_ROUTES=true
```

For only the Erode-to-Bangalore route:

```dotenv
TEST_ALL_DIRECTED_ROUTES=false
ROUTES=Erode>Bangalore
ROUTE_DISPLAY_NAME=Home to Office
```

For a single-route daily briefing, keep `TEST_ALL_DIRECTED_ROUTES=false`.

---

## 🕒 Scheduled Execution

The application supports scheduled execution through its configured timezone and run hour.

For automated daily execution, the project can also be configured with GitHub Actions.

Before enabling a GitHub Actions workflow:

1. Add the required API keys and webhook URL as repository secrets.
2. Configure the workflow schedule.
3. Ensure the workflow installs dependencies before running the application.
4. Check the Actions run logs after the first execution.

Never hardcode API keys in the workflow file.

---

## 🛡️ Security

- Keep `.env` out of Git.
- Store secrets in GitHub Actions Secrets when running in GitHub Actions.
- Do not share Discord webhook URLs publicly.
- Avoid printing API keys in logs.
- Rotate credentials if they are accidentally exposed.

---

## 🐛 Troubleshooting

### Groq model not found

If Groq returns a model-not-found error:

1. Check the configured `GROQ_MODEL`.
2. Confirm the model is available to your Groq account.
3. Update the model name in `.env`.
4. Restart the application.

### Discord notification not received

Check:

- `DISCORD_WEBHOOK_URL` is correct.
- The webhook has not been deleted or regenerated.
- The application logs show a successful Discord response.

### Weather request failed

Check your internet connection and review the API response in the application logs.

### TomTom traffic unavailable

Check that `TOMTOM_API_KEY` is configured and valid. Weather reporting can still work even if traffic retrieval fails.

### Timezone error on Windows

Install the timezone database package:

```bash
pip install tzdata
```

---

## 📌 Future Improvements

- Discord embeds for a richer notification layout
- Configurable multiple home-office routes
- Better commute baseline tracking
- More detailed weather alert customization
- Retry and backoff for temporary API failures
- Historical weather and commute summaries

---

## 👨‍💻 Author

**Shyam Sundhar G**

Computer Science Engineering | AI & Machine Learning

- GitHub: [@shyamgsundhar](https://github.com/shyamgsundhar)
- LinkedIn: [@shyamgsundhar](https://www.linkedin.com/in/shyamgsundhar/)

---

## 📄 License

This project is intended for personal learning and automation.
```
