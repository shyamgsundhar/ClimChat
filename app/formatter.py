from datetime import datetime

from app.weather import weather_description


def value_or_na(value, suffix=""):
    if value is None:
        return "N/A"

    return f"{value}{suffix}"


def format_briefing(
    settings,
    now: datetime,
    weather_results: list[dict],
    traffic_results: list[dict],
    ai_insights: str,
) -> str:

    # Use the first two configured cities as Home and Office.
    home_city = settings.cities[0].name if settings.cities else "Home"
    office_city = (
        settings.cities[1].name
        if len(settings.cities) > 1
        else "Office"
    )

    weather_by_city = {
        item.get("city"): item
        for item in weather_results
    }

    home_weather = weather_by_city.get(home_city)
    office_weather = weather_by_city.get(office_city)

    lines = [
        "# 🌤️ Daily Weather & Commute Brief",
        f"**{now.strftime('%A, %d %B %Y · %I:%M %p %Z')}**",
        "",
    ]

    def add_location_weather(label: str, city_name: str, item: dict | None):
        if not item or item.get("status") != "success":
            lines.append(
                f"**📍 {label} — {city_name}:** Weather unavailable"
            )
            return

        condition = item.get("condition") or weather_description(
            item.get("weather_code")
        )

        lines.append(
            f"**📍 {label} — {city_name}:** "
            f"{value_or_na(item.get('temperature_c'), '°C')} · "
            f"Feels like {value_or_na(item.get('feels_like_c'), '°C')} · "
            f"{condition}"
        )

    add_location_weather("Home", home_city, home_weather)
    add_location_weather("Office", office_city, office_weather)

    # Read the two short AI lines.
    ai_lines = [
        line.strip()
        for line in (ai_insights or "").splitlines()
        if line.strip()
    ]

    weather_insight = next(
        (
            line.split(":", 1)[1].strip()
            for line in ai_lines
            if line.lower().startswith("weather:")
        ),
        "Weather summary unavailable.",
    )

    alert_insight = next(
        (
            line.split(":", 1)[1].strip()
            for line in ai_lines
            if line.lower().startswith("alert:")
        ),
        "No major alerts.",
    )

    lines.extend([
        "",
        f"**🌦️ Weather:** {weather_insight}",
        "",
    ])

    # Display commute information.
    successful_routes = [
        item for item in traffic_results
        if item.get("status") == "success"
    ]

    failed_routes = [
        item for item in traffic_results
        if item.get("status") != "success"
    ]

    if successful_routes:
        route = successful_routes[0]

        route_name = getattr(
            settings,
            "route_display_name",
            "Home to Office",
        )

        origin = route.get("origin", home_city)
        destination = route.get("destination", office_city)

        travel_minutes = route.get("travel_minutes")
        baseline_diff = route.get("baseline_difference_minutes")

        if travel_minutes is None:
            travel_text = "Travel time unavailable"
        else:
            hours, minutes = divmod(round(travel_minutes), 60)

            if hours:
                travel_text = f"{hours} hr {minutes} min"
            else:
                travel_text = f"{minutes} min"

        if baseline_diff is None:
            comparison_text = "usual-time comparison unavailable"
        elif baseline_diff > 0:
            comparison_text = (
                f"{round(baseline_diff)} min above usual"
            )
        elif baseline_diff < 0:
            comparison_text = (
                f"{abs(round(baseline_diff))} min below usual"
            )
        else:
            comparison_text = "usual travel time"

        lines.append(
            f"**🚗 Commute — {route_name}:** "
            f"{origin} → {destination} · "
            f"{travel_text} · {comparison_text}"
        )

    elif failed_routes:
        lines.append(
            "**🚗 Commute:** Traffic information unavailable."
        )
    else:
        lines.append(
            "**🚗 Commute:** No route configured."
        )

    lines.extend([
        "",
        f"**⚠️ Alert:** {alert_insight}",
    ])

    return "\n".join(lines)