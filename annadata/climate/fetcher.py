"""Fetch historical climate data from Open-Meteo archive API and aggregate to weekly."""
from __future__ import annotations

from datetime import date, timedelta

import httpx

from annadata.config import ARCHIVE_URL
from annadata.models.climate import SeasonClimate, WeeklyClimate


async def fetch_season_climate(
    lat: float,
    lon: float,
    location_name: str,
    sowing_date: date,
    growing_days: int,
) -> SeasonClimate:
    """Fetch real historical weather for the growing season and return SeasonClimate."""
    harvest_date = sowing_date + timedelta(days=growing_days)

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            ARCHIVE_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "start_date": sowing_date.isoformat(),
                "end_date": harvest_date.isoformat(),
                "daily": ",".join([
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "shortwave_radiation_sum",
                    "windspeed_10m_max",
                    "et0_fao_evapotranspiration",
                ]),
                "timezone": "auto",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    daily = data["daily"]
    n_days = len(daily["time"])

    season = SeasonClimate(
        location=location_name,
        latitude=lat,
        longitude=lon,
        sowing_date=sowing_date,
        harvest_date=harvest_date,
    )

    # Aggregate daily → weekly
    week_num = 1
    i = 0
    while i < n_days:
        chunk_end = min(i + 7, n_days)
        chunk = range(i, chunk_end)

        def safe(key: str, idx: int) -> float:
            v = daily[key][idx]
            return v if v is not None else 0.0

        temp_maxes = [safe("temperature_2m_max", j) for j in chunk]
        temp_mins  = [safe("temperature_2m_min", j)  for j in chunk]
        means      = [(mx + mn) / 2 for mx, mn in zip(temp_maxes, temp_mins)]

        week = WeeklyClimate(
            week_number=week_num,
            start_date=date.fromisoformat(daily["time"][i]),
            end_date=date.fromisoformat(daily["time"][chunk_end - 1]),
            temp_max_avg=sum(temp_maxes) / len(temp_maxes),
            temp_min_avg=sum(temp_mins) / len(temp_mins),
            temp_mean=sum(means) / len(means),
            precipitation_mm=sum(safe("precipitation_sum", j) for j in chunk),
            solar_radiation_mj_m2=sum(safe("shortwave_radiation_sum", j) for j in chunk),
            wind_speed_avg_ms=sum(safe("windspeed_10m_max", j) for j in chunk) / len(chunk),
            et0_mm=sum(safe("et0_fao_evapotranspiration", j) for j in chunk),
        )
        season.weeks.append(week)
        week_num += 1
        i += 7

    return season
