
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


# Load .env from project root, regardless of current terminal directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def env_float(name: str, default: float) -> float:
    value = os.getenv(name, "").strip()
    return float(value) if value else default


def env_int(name: str, default: int) -> int:
    value = os.getenv(name, "").strip()
    return int(value) if value else default


@dataclass(frozen=True)
class City:
    name: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class Route:
    origin: City
    destination: City

    @property
    def name(self) -> str:
        return f"{self.origin.name} → {self.destination.name}"


@dataclass(frozen=True)
class Settings:
    discord_webhook_url: str
    groq_api_key: str
    groq_model: str
    groq_max_tokens: int
    groq_temperature: float

    timezone: str
    run_hour: int
    force_run: bool
    request_timeout: int

    cities: tuple[City, ...]
    tomtom_api_key: str
    transport_mode: str
    test_all_directed_routes: bool
    configured_routes: tuple[str, ...]
    usual_commute_minutes: int

    rain_alert_mm: float
    rain_probability_alert_percent: int
    heat_alert_c: float
    feels_like_alert_c: float
    cold_alert_c: float
    wind_alert_kmh: float

    enable_groq_insights: bool
    ai_include_route_insights: bool


def load_cities() -> tuple[City, ...]:
    city_names = [
        name.strip()
        for name in os.getenv("CITIES", "").split(",")
        if name.strip()
    ]

    if not city_names:
        raise ValueError("CITIES is empty. Add at least one city in .env")

    cities = []
    seen = set()

    for name in city_names:
        normalized = name.upper()

        if normalized in seen:
            raise ValueError(f"Duplicate city in CITIES: {name}")

        seen.add(normalized)
        prefix = name.upper().replace(" ", "_")

        lat_key = f"CITY_{prefix}_LAT"
        lon_key = f"CITY_{prefix}_LON"

        lat_value = os.getenv(lat_key, "").strip()
        lon_value = os.getenv(lon_key, "").strip()

        if not lat_value or not lon_value:
            raise ValueError(
                f"Missing coordinates for {name}. "
                f"Expected {lat_key} and {lon_key} in .env"
            )

        latitude = float(lat_value)
        longitude = float(lon_value)

        if not -90 <= latitude <= 90:
            raise ValueError(f"Invalid latitude for {name}: {latitude}")

        if not -180 <= longitude <= 180:
            raise ValueError(f"Invalid longitude for {name}: {longitude}")

        cities.append(City(name, latitude, longitude))

    return tuple(cities)


def load_settings() -> Settings:
    required = [
        "DISCORD_WEBHOOK_URL",
        "GROQ_API_KEY",
    ]

    missing = [
        key for key in required
        if not os.getenv(key, "").strip()
        or os.getenv(key, "").startswith("PASTE_")
    ]

    if missing:
        raise ValueError(
            "Missing required .env values: " + ", ".join(missing)
        )

    run_hour = env_int("RUN_HOUR", 7)
    if not 0 <= run_hour <= 23:
        raise ValueError("RUN_HOUR must be between 0 and 23")

    timeout = env_int("REQUEST_TIMEOUT", 25)
    if timeout < 1:
        raise ValueError("REQUEST_TIMEOUT must be greater than zero")

    route_text = os.getenv("ROUTES", "")
    configured_routes = tuple(
        item.strip()
        for item in route_text.split(";")
        if item.strip()
    )

    return Settings(
        discord_webhook_url=os.environ["DISCORD_WEBHOOK_URL"].strip(),
        groq_api_key=os.environ["GROQ_API_KEY"].strip(),
        groq_model=os.getenv(
            "GROQ_MODEL", "llama-3.3-70b-versatile"
        ).strip(),
        groq_max_tokens=env_int("GROQ_MAX_TOKENS", 1200),
        groq_temperature=env_float("GROQ_TEMPERATURE", 0.3),

        timezone=os.getenv("TIMEZONE", "Asia/Kolkata").strip(),
        run_hour=run_hour,
        force_run=env_bool("FORCE_RUN", False),
        request_timeout=timeout,

        cities=load_cities(),
        tomtom_api_key=os.getenv("TOMTOM_API_KEY", "").strip(),
        transport_mode=os.getenv("TRANSPORT_MODE", "car").strip(),
        test_all_directed_routes=env_bool(
            "TEST_ALL_DIRECTED_ROUTES", True
        ),
        configured_routes=configured_routes,
        usual_commute_minutes=env_int(
            "USUAL_COMMUTE_MINUTES", 0
        ),

        rain_alert_mm=env_float("RAIN_ALERT_MM", 20),
        rain_probability_alert_percent=env_int(
            "RAIN_PROBABILITY_ALERT_PERCENT", 60
        ),
        heat_alert_c=env_float("HEAT_ALERT_C", 38),
        feels_like_alert_c=env_float("FEELS_LIKE_ALERT_C", 40),
        cold_alert_c=env_float("COLD_ALERT_C", 8),
        wind_alert_kmh=env_float("WIND_ALERT_KMH", 50),

        enable_groq_insights=env_bool("ENABLE_GROQ_INSIGHTS", True),
        ai_include_route_insights=env_bool(
            "AI_INCLUDE_ROUTE_INSIGHTS", True
        ),
    )


def generate_routes(settings: Settings) -> list[Route]:
    city_map = {city.name.lower(): city for city in settings.cities}

    if settings.test_all_directed_routes:
        return [
            Route(origin, destination)
            for origin in settings.cities
            for destination in settings.cities
            if origin.name != destination.name
        ]

    routes = []

    for route_text in settings.configured_routes:
        if ">" not in route_text:
            raise ValueError(
                f"Invalid route '{route_text}'. Expected Origin>Destination"
            )

        origin_name, destination_name = [
            part.strip().lower()
            for part in route_text.split(">", 1)
        ]

        if origin_name not in city_map:
            raise ValueError(f"Unknown route origin: {origin_name}")

        if destination_name not in city_map:
            raise ValueError(f"Unknown route destination: {destination_name}")

        if origin_name == destination_name:
            raise ValueError("Same-city routes are not supported")

        routes.append(
            Route(city_map[origin_name], city_map[destination_name])
        )

    return routes