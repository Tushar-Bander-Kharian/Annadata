"""Input data models: soil, water quality, crop variety."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SoilState:
    ph: float                       # 0–14, typical crops: 5.0–8.0
    nitrogen_kg_ha: float           # available N in kg/ha
    phosphorus_kg_ha: float         # available P in kg/ha
    potassium_kg_ha: float          # available K in kg/ha
    organic_matter_pct: float       # % OM by weight (typical: 0.5–5.0)
    texture: str                    # sandy, loam, clay, etc.


@dataclass
class WaterQuality:
    ph: float                       # irrigation water pH
    ec_ds_m: float                  # electrical conductivity in dS/m (salinity)
    method: str                     # rainfed, drip, flood, furrow, sprinkler


@dataclass
class CropVariety:
    key: str                        # e.g. "wheat"
    display_name: str
    variety_label: str              # e.g. "HD-2967" or "local"
    base_yield_t_ha: float
    growing_days: int
    optimal_temp_min: float
    optimal_temp_max: float
    critical_temp_high: float
    critical_temp_low: float
    optimal_ph_min: float
    optimal_ph_max: float
    ec_threshold_ds_m: float
    ec_slope_pct_per_ds_m: float
    n_demand_kg_per_t: float
    p_demand_kg_per_t: float
    k_demand_kg_per_t: float
    kc: dict[str, float]            # crop coefficients per stage
