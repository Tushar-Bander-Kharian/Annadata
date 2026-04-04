"""Geocode a city name to lat/lon using Open-Meteo (free, no API key)."""
from __future__ import annotations

import httpx

from annadata.config import GEOCODING_URL


async def geocode(city: str) -> tuple[float, float, str]:
    """Return (latitude, longitude, resolved_name) for a city name."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            GEOCODING_URL,
            params={"name": city, "count": 1, "language": "en", "format": "json"},
        )
        resp.raise_for_status()
        data = resp.json()

    results = data.get("results")
    if not results:
        raise ValueError(f"Location '{city}' not found. Try a larger nearby city.")

    r = results[0]
    name = f"{r['name']}, {r.get('country', '')}"
    return float(r["latitude"]), float(r["longitude"]), name
