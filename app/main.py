import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config import load_settings, generate_routes
from app.weather import WeatherClient, weather_description
from app.traffic import TrafficClient
from app.ai_insights import GroqInsights
from app.formatter import format_briefing
from app.discord_client import DiscordClient


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def main() -> None:
    settings = load_settings()
    now = datetime.now(ZoneInfo(settings.timezone))

    if not settings.force_run and now.hour != settings.run_hour:
        logger.info(
            "Skipping run: local hour=%s, configured hour=%s",
            now.hour,
            settings.run_hour,
        )
        return

    logger.info("Starting weather and commute briefing")

    # -------------------------
    # Fetch weather
    # -------------------------
    weather_client = WeatherClient(settings)
    weather_results = []

    for city in settings.cities:
        logger.info("Fetching weather for %s", city.name)

        try:
            result = weather_client.fetch(city)

            result["condition"] = weather_description(
                result.get("weather_code")
            )
            result["status"] = "success"

            weather_results.append(result)

        except Exception as exc:
            logger.exception(
                "Weather request failed for %s",
                city.name,
            )

            weather_results.append({
                "city": city.name,
                "status": "failed",
                "error": str(exc)[:250],
            })

    # -------------------------
    # Fetch traffic
    # -------------------------
    traffic_results = []
    routes = generate_routes(settings)

    if not settings.tomtom_api_key:
        logger.warning(
            "TomTom skipped: TOMTOM_API_KEY is not configured"
        )

        traffic_results = [
            {
                "route": route.name,
                "origin": route.origin.name,
                "destination": route.destination.name,
                "status": "failed",
                "error": "TomTom API key is not configured",
            }
            for route in routes
        ]

    else:
        traffic_client = TrafficClient(settings)

        for route in routes:
            logger.info("Fetching traffic for %s", route.name)

            try:
                result = traffic_client.fetch(route)

                # Ensure route endpoints are available to the formatter.
                result.setdefault("route", route.name)
                result.setdefault("origin", route.origin.name)
                result.setdefault("destination", route.destination.name)

                traffic_results.append(result)

            except Exception as exc:
                logger.exception(
                    "Traffic request failed for %s",
                    route.name,
                )

                traffic_results.append({
                    "route": route.name,
                    "origin": route.origin.name,
                    "destination": route.destination.name,
                    "status": "failed",
                    "error": str(exc)[:250],
                })

    # -------------------------
    # Generate short AI insights
    # -------------------------
    if settings.enable_groq_insights:
        logger.info("Generating concise Groq insights")

        ai_insights = GroqInsights(settings).generate(
            weather_results,
            traffic_results,
        )
    else:
        ai_insights = (
            "Weather: Weather summary unavailable.\n"
            "Alert: No major alerts."
        )

    # -------------------------
    # Format short Discord message
    # -------------------------
    message = format_briefing(
        settings=settings,
        now=now,
        weather_results=weather_results,
        traffic_results=traffic_results,
        ai_insights=ai_insights,
    )

    successful_weather = sum(
        item.get("status") == "success"
        for item in weather_results
    )

    successful_traffic = sum(
        item.get("status") == "success"
        for item in traffic_results
    )

    logger.info(
        "Collected weather for %d/%d cities and traffic for %d/%d routes",
        successful_weather,
        len(weather_results),
        successful_traffic,
        len(traffic_results),
    )

    DiscordClient(
        settings.discord_webhook_url,
        timeout=settings.request_timeout,
    ).send(message)

    logger.info("Briefing delivered to Discord")


if __name__ == "__main__":
    main()