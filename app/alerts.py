def build_weather_alerts(weather: dict, settings) -> list[str]:
    """Simple threshold-based notices; these are not official warnings."""
    alerts = []
    temp = weather.get("temperature_c")
    rain = weather.get("next_6h_rain_mm")
    wind = weather.get("wind_kmh")

    if temp is not None and temp >= settings.heat_alert_c:
        alerts.append(
            f"High-temperature threshold: {temp}°C (configured threshold "
            f"{settings.heat_alert_c}°C)."
        )
    if temp is not None and temp <= settings.cold_alert_c:
        alerts.append(
            f"Low-temperature threshold: {temp}°C (configured threshold "
            f"{settings.cold_alert_c}°C)."
        )
    if rain is not None and rain >= settings.rain_alert_mm:
        alerts.append(
            f"Rainfall threshold: {rain:.1f} mm forecast over the next 6 hours."
        )
    if wind is not None and wind >= settings.wind_alert_kmh:
        alerts.append(
            f"High-wind threshold: {wind} km/h (configured threshold "
            f"{settings.wind_alert_kmh} km/h)."
        )
    return alerts
