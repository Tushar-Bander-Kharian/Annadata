"""Simulation state models."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class WeeklyStress:
    week: int
    stage: str
    temperature_factor: float = 1.0
    water_factor: float = 1.0
    salinity_factor: float = 1.0
    ph_factor: float = 1.0
    nutrient_factor: float = 1.0
    radiation_factor: float = 1.0
    combined: float = 1.0


@dataclass
class SimulationResult:
    crop_name: str
    variety_label: str
    location: str
    sowing_date: str
    harvest_date: str
    potential_yield_t_ha: float
    simulated_yield_t_ha: float
    yield_gap_pct: float
    season_weeks: int
    mean_temp_c: float
    total_rain_mm: float
    weekly_stress: list[WeeklyStress]
    stage_reports: dict[str, str]   # stage name → LLM text
    final_report: str
    dominant_stresses: list[str]    # top 3 limiting factor names
    alerts: list[str]               # critical event flags
    # Soil C/N dynamics — one entry per week from SoilColumn
    weekly_soil: list[dict] = field(default_factory=list)
