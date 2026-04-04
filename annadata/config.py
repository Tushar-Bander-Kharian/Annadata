"""Annadata — configuration, crop database, and simulation constants."""
from __future__ import annotations
import os

# ---------------------------------------------------------------------------
# LLM Backend
# ---------------------------------------------------------------------------
LLM_BACKEND: str = os.environ.get("ANNADATA_BACKEND", "grok")
GROK_API_KEY: str = os.environ.get("GROK_API_KEY", "")
ANTHROPIC_API_KEY: str = os.environ.get("ANTHROPIC_API_KEY", "")
OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_URL", "http://localhost:11434")

if LLM_BACKEND == "ollama":
    STAGE_MODEL: str = os.environ.get("ANNADATA_MODEL", "qwen2.5:7b")
elif LLM_BACKEND == "grok":
    STAGE_MODEL: str = os.environ.get("ANNADATA_MODEL", "grok-3-mini")
else:  # claude
    STAGE_MODEL: str = "claude-haiku-4-5-20251001"

REPORT_MODEL: str = STAGE_MODEL

# ---------------------------------------------------------------------------
# Open-Meteo API (free, no key required)
# ---------------------------------------------------------------------------
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# ---------------------------------------------------------------------------
# Crop database
# ---------------------------------------------------------------------------
CROP_DB: dict[str, dict] = {
    "wheat": {
        "display_name": "Wheat (Triticum aestivum)",
        "base_yield_t_ha": 6.0,
        "growing_days": 120,
        "optimal_temp_min": 12.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 32.0, "critical_temp_low": 3.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 6.0, "ec_slope_pct_per_ds_m": 7.1,
        "n_demand_kg_per_t": 25.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 18.0,
        "kc": {"germination": 0.40, "vegetative": 0.85, "reproductive": 1.10, "maturity": 0.65},
    },
    "rice": {
        "display_name": "Rice (Oryza sativa)",
        "base_yield_t_ha": 8.0,
        "growing_days": 130,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 36.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 3.0, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 20.0, "p_demand_kg_per_t": 4.0, "k_demand_kg_per_t": 15.0,
        "kc": {"germination": 0.50, "vegetative": 1.00, "reproductive": 1.20, "maturity": 0.70},
    },
    "maize": {
        "display_name": "Maize/Corn (Zea mays)",
        "base_yield_t_ha": 9.0,
        "growing_days": 100,
        "optimal_temp_min": 18.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 35.0, "critical_temp_low": 8.0,
        "optimal_ph_min": 5.8, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.7, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 22.0, "p_demand_kg_per_t": 6.0, "k_demand_kg_per_t": 20.0,
        "kc": {"germination": 0.40, "vegetative": 0.90, "reproductive": 1.20, "maturity": 0.60},
    },
    "cotton": {
        "display_name": "Cotton (Gossypium hirsutum)",
        "base_yield_t_ha": 2.5,
        "growing_days": 160,
        "optimal_temp_min": 22.0, "optimal_temp_max": 34.0,
        "critical_temp_high": 40.0, "critical_temp_low": 14.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 7.7, "ec_slope_pct_per_ds_m": 5.2,
        "n_demand_kg_per_t": 50.0, "p_demand_kg_per_t": 12.0, "k_demand_kg_per_t": 35.0,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.15, "maturity": 0.65},
    },
    "soybean": {
        "display_name": "Soybean (Glycine max)",
        "base_yield_t_ha": 3.5,
        "growing_days": 110,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 36.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 5.0, "ec_slope_pct_per_ds_m": 20.0,
        "n_demand_kg_per_t": 10.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 18.0,
        "kc": {"germination": 0.40, "vegetative": 0.80, "reproductive": 1.15, "maturity": 0.50},
    },
    "tomato": {
        "display_name": "Tomato (Solanum lycopersicum)",
        "base_yield_t_ha": 40.0,
        "growing_days": 100,
        "optimal_temp_min": 18.0, "optimal_temp_max": 27.0,
        "critical_temp_high": 35.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 6.8,
        "ec_threshold_ds_m": 2.5, "ec_slope_pct_per_ds_m": 9.9,
        "n_demand_kg_per_t": 3.0, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 4.5,
        "kc": {"germination": 0.45, "vegetative": 0.75, "reproductive": 1.15, "maturity": 0.80},
    },
    "potato": {
        "display_name": "Potato (Solanum tuberosum)",
        "base_yield_t_ha": 30.0,
        "growing_days": 110,
        "optimal_temp_min": 14.0, "optimal_temp_max": 22.0,
        "critical_temp_high": 30.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 5.0, "optimal_ph_max": 6.5,
        "ec_threshold_ds_m": 1.7, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 4.0, "p_demand_kg_per_t": 0.9, "k_demand_kg_per_t": 6.0,
        "kc": {"germination": 0.50, "vegetative": 0.85, "reproductive": 1.15, "maturity": 0.75},
    },
}

# ---------------------------------------------------------------------------
# Soil textures
# ---------------------------------------------------------------------------
SOIL_TEXTURES: dict[str, dict] = {
    "sandy":      {"water_holding": 0.40, "drainage_rate": 1.00, "nutrient_retention": 0.30},
    "sandy_loam": {"water_holding": 0.60, "drainage_rate": 0.70, "nutrient_retention": 0.55},
    "loam":       {"water_holding": 0.80, "drainage_rate": 0.50, "nutrient_retention": 0.80},
    "clay_loam":  {"water_holding": 0.90, "drainage_rate": 0.30, "nutrient_retention": 0.85},
    "clay":       {"water_holding": 1.00, "drainage_rate": 0.20, "nutrient_retention": 0.90},
    "silty":      {"water_holding": 0.70, "drainage_rate": 0.40, "nutrient_retention": 0.70},
}

# ---------------------------------------------------------------------------
# Simulation constants
# ---------------------------------------------------------------------------
STAGE_WEIGHTS: dict[str, float] = {
    "germination":  0.05,
    "vegetative":   0.25,
    "reproductive": 0.50,
    "maturity":     0.20,
}

STAGE_BOUNDARIES: dict[str, tuple[float, float]] = {
    "germination":  (0.00, 0.10),
    "vegetative":   (0.10, 0.50),
    "reproductive": (0.50, 0.80),
    "maturity":     (0.80, 1.00),
}

# Irrigation water added per week (mm)
IRRIGATION_MM_PER_WEEK: dict[str, float] = {
    "rainfed":   0.0,
    "flood":    40.0,
    "furrow":   25.0,
    "sprinkler": 30.0,
    "drip":     26.0,   # 20mm but 1.3x efficiency → effective 26mm
}

OPTIMAL_RADIATION_MJ_PER_WEEK: float = 140.0

# ---------------------------------------------------------------------------
# Regional soil presets — measured field data from peer-reviewed theses
# ---------------------------------------------------------------------------
# Punjab presets derived from:
#   Sravanthi (2022), M.Sc. Thesis, PAU Ludhiana — 340 samples across 3 districts
#   Mondal (2017), Ph.D. Thesis, PAU Ludhiana — Ladian village rice-wheat system
#
# Parameter notes:
#   ph              — 1:2.5 water suspension method
#   ec_ds_m         — electrical conductivity of saturation extract (dS/m)
#   nitrogen_kg_ha  — mineral N (0-30 cm), estimated from KCl-N (mg/kg) × 4.2
#   phosphorus_kg_ha— Olsen-P (0.5 M NaHCO₃ extract), kg/ha
#   potassium_kg_ha — NH₄OAc extractable K, kg/ha
#   organic_matter  — SOC% × 1.724 Van Bemmelen factor
# ---------------------------------------------------------------------------

PUNJAB_SOIL_PRESETS: dict[str, dict] = {
    "punjab_mansa": {
        "display_name": "Punjab - Mansa district (loamy sand, Malwa agro-zone)",
        "texture": "sandy_loam",      # loamy sand → nearest model class
        "ph": 8.46,                   # alkaline, CaCO₃-bearing alluvium
        "ec_ds_m": 0.37,
        "nitrogen_kg_ha": 55.0,       # low; sparse OM, rapid N leaching
        "phosphorus_kg_ha": 32.5,     # Olsen-P, low-medium
        "potassium_kg_ha": 443.9,     # adequate
        "organic_matter_pct": 0.52,   # SOC 0.30 % × 1.724
    },
    "punjab_ludhiana": {
        "display_name": "Punjab - Ludhiana district (sandy loam, rice-wheat zone)",
        "texture": "sandy_loam",
        "ph": 7.69,                   # near-neutral, long-term rice-wheat
        "ec_ds_m": 0.26,
        "nitrogen_kg_ha": 90.0,       # Mondal (2017): KCl-N 87 mg/kg → ~87×1.02≈89
        "phosphorus_kg_ha": 48.9,     # Olsen-P, medium
        "potassium_kg_ha": 374.5,     # adequate
        "organic_matter_pct": 1.00,   # SOC 0.58 % × 1.724
    },
    "punjab_patiala": {
        "display_name": "Punjab - Patiala district (loam, Majha-Doaba transition)",
        "texture": "loam",
        "ph": 7.71,
        "ec_ds_m": 0.54,              # slightly higher EC, older alluvium
        "nitrogen_kg_ha": 75.0,       # medium; good OM but heavier texture
        "phosphorus_kg_ha": 115.4,    # Olsen-P, high (long-term P build-up)
        "potassium_kg_ha": 493.0,     # high
        "organic_matter_pct": 0.93,   # SOC 0.54 % × 1.724
    },
}

# Master index — extend with other states as data is collected
REGION_SOIL_PRESETS: dict[str, dict[str, dict]] = {
    "Punjab": PUNJAB_SOIL_PRESETS,
}
