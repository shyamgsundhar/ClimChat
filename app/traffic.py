
import requests


class TrafficClient:
    BASE_URL = "https://api.tomtom.com/routing/1/calculateRoute"

    def __init__(self, settings):
        self.settings = settings
        self.session = requests.Session()

    def fetch(self, route) -> dict:
        locations = (
            f"{route.origin.latitude},{route.origin.longitude}:"
            f"{route.destination.latitude},{route.destination.longitude}"
        )

        url = f"{self.BASE_URL}/{locations}/json"

        params = {
            "key": self.settings.tomtom_api_key,
            "traffic": "true",
            "travelMode": "car",
            "routeType": "fastest",
        }

        response = self.session.get(
            url,
            params=params,
            timeout=self.settings.request_timeout,
        )
        response.raise_for_status()

        payload = response.json()
        routes = payload.get("routes", [])

        if not routes:
            raise ValueError("TomTom returned no route results")

        summary = routes[0].get("summary", {})
        actual_seconds = summary.get("travelTimeInSeconds")
        freeflow_seconds = summary.get("noTrafficTravelTimeInSeconds")

        actual_minutes = (
            round(actual_seconds / 60)
            if actual_seconds is not None else None
        )
        freeflow_minutes = (
            round(freeflow_seconds / 60)
            if freeflow_seconds is not None else None
        )

        delay_minutes = None
        if actual_minutes is not None and freeflow_minutes is not None:
            delay_minutes = max(0, actual_minutes - freeflow_minutes)

        baseline_difference = None
        if (
            actual_minutes is not None
            and self.settings.usual_commute_minutes > 0
        ):
            baseline_difference = (
                actual_minutes - self.settings.usual_commute_minutes
            )

        return {
            "route": route.name,
            "origin": route.origin.name,
            "destination": route.destination.name,
            "travel_minutes": actual_minutes,
            "freeflow_minutes": freeflow_minutes,
            "delay_minutes": delay_minutes,
            "baseline_minutes": self.settings.usual_commute_minutes or None,
            "baseline_difference_minutes": baseline_difference,
            "status": "success",
        }