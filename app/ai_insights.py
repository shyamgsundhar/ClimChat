import json
import logging

from groq import Groq

logger = logging.getLogger(__name__)


class GroqInsights:
    def __init__(self, settings):
        self.settings = settings
        self.client = Groq(api_key=settings.groq_api_key)

    def generate(
        self,
        weather_results: list[dict],
        traffic_results: list[dict],
    ) -> str:
        weather_summary = []

        for item in weather_results:
            if item.get("status") != "success":
                weather_summary.append({
                    "city": item.get("city", "Unknown"),
                    "status": "failed",
                    "error": item.get("error", "Weather unavailable"),
                })
                continue

            weather_summary.append({
                "city": item.get("city"),
                "condition": item.get("condition"),
                "temperature_c": item.get("temperature_c"),
                "feels_like_c": item.get("feels_like_c"),
                "rain_next_6h_mm": item.get("next_6h_rain_mm"),
                "rain_probability_max_percent": (
                    item.get("next_6h_rain_probability_max")
                ),
                "wind_kmh": item.get("wind_kmh"),
            })

        traffic_summary = []

        for item in traffic_results:
            traffic_summary.append({
                "route": item.get("route"),
                "status": item.get("status"),
                "travel_minutes": item.get("travel_minutes"),
                "traffic_delay_minutes": item.get("delay_minutes"),
                "baseline_difference_minutes": (
                    item.get("baseline_difference_minutes")
                ),
                "error": item.get("error"),
            })

        data = {
            "weather": weather_summary,
            "traffic": (
                traffic_summary
                if self.settings.ai_include_route_insights
                else []
            ),
            "thresholds": {
                "rain_mm": self.settings.rain_alert_mm,
                "rain_probability_percent": (
                    self.settings.rain_probability_alert_percent
                ),
                "heat_c": self.settings.heat_alert_c,
                "feels_like_c": self.settings.feels_like_alert_c,
                "cold_c": self.settings.cold_alert_c,
                "wind_kmh": self.settings.wind_alert_kmh,
            },
        }

        system_prompt = """
You are a concise daily weather and commute assistant.

Analyze only the supplied data. Never invent weather, traffic conditions,
road closures, causes, or travel advice.

Return EXACTLY these two lines:

Weather: One short sentence describing the important weather difference
between the locations. Mention rain only when supported by the data.

Alert: One short actionable alert based on the supplied thresholds and data.
If no notable alert exists, write: No major alerts.

Rules:
- Keep the entire response under 55 words.
- Do not add headings other than Weather: and Alert:.
- Do not use numbered lists or bullet points.
- Do not repeat every temperature or weather measurement.
- Do not call informational thresholds official warnings.
- Do not claim a location is safe or unsafe.
- If data is missing, do not guess.
- For commute-related alerts, use only supplied traffic data.
"""

        try:
            completion = self.client.chat.completions.create(
                model=self.settings.groq_model,
                temperature=self.settings.groq_temperature,
                max_tokens=120,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": (
                            "Create the short weather summary and alert "
                            "from this data:\n"
                            + json.dumps(data, ensure_ascii=False)
                        ),
                    },
                ],
            )

            content = completion.choices[0].message.content

            if content and content.strip():
                return content.strip()

            return self._fallback(weather_results, traffic_results)

        except Exception:
            logger.exception("Groq insight generation failed")
            return self._fallback(weather_results, traffic_results)

    @staticmethod
    def _fallback(
        weather_results: list[dict],
        traffic_results: list[dict],
    ) -> str:
        """
        Produce a short non-AI fallback so the Discord briefing
        remains useful even if Groq is unavailable.
        """

        successful_weather = [
            item for item in weather_results
            if item.get("status") == "success"
        ]

        successful_traffic = [
            item for item in traffic_results
            if item.get("status") == "success"
        ]

        rain_cities = [
            item.get("city", "Unknown")
            for item in successful_weather
            if (
                (item.get("next_6h_rain_probability_max") or 0) >= 60
                or (item.get("next_6h_rain_mm") or 0) >= 1
            )
        ]

        if rain_cities:
            weather_line = (
                "Weather: Rain is possible in "
                + ", ".join(rain_cities)
                + "."
            )
            alert_line = (
                "Alert: Carry rain protection where needed."
            )
        else:
            weather_line = (
                "Weather: No significant rainfall signal in the available forecast."
            )
            alert_line = "Alert: No major alerts."

        if successful_traffic:
            route = successful_traffic[0]
            baseline_diff = route.get("baseline_difference_minutes")

            if baseline_diff is not None and baseline_diff > 0:
                alert_line = (
                    f"Alert: Allow about {round(baseline_diff)} extra "
                    "minutes for the commute."
                )

        return f"{weather_line}\n{alert_line}"