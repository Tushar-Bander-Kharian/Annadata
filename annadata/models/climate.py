"""Climate data models."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date


@dataclass
class WeeklyClimate:
    week_number: int
    start_date: date
    end_date: date
    temp_max_avg: float         # °C — weekly mean of daily maximums
    temp_min_avg: float         # °C — weekly mean of daily minimums
    temp_mean: float            # °C — (max+min)/2 averaged over week
    precipitation_mm: float     # mm — total weekly rainfall
    solar_radiation_mj_m2: float  # MJ/m² — total weekly shortwave radiation
    wind_speed_avg_ms: float    # m/s — weekly average
    et0_mm: float               # mm — reference evapotranspiration (FAO-56)


@dataclass
class SeasonClimate:
    location: str
    latitude: float
    longitude: float
    sowing_date: date
    harvest_date: date
    weeks: list[WeeklyClimate] = field(default_factory=list)

    @property
    def total_precipitation_mm(self) -> float:
        return sum(w.precipitation_mm for w in self.weeks)

    @property
    def mean_temp(self) -> float:
        if not self.weeks:
            return 0.0
        return sum(w.temp_mean for w in self.weeks) / len(self.weeks)

    @property
    def total_et0_mm(self) -> float:
        return sum(w.et0_mm for w in self.weeks)
