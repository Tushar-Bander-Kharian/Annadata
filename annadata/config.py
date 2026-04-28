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
        "optimal_ph_min": 6.0, "optimal_ph_max": 8.0,  # wheat tolerates calcareous IGP soils to pH 8.0
        "ec_threshold_ds_m": 6.0, "ec_slope_pct_per_ds_m": 7.1,
        "n_demand_kg_per_t": 25.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 18.0,
        "kc": {"germination": 0.40, "vegetative": 0.85, "reproductive": 1.10, "maturity": 0.65},
        # GDD accumulation uses agronomic T_base (0°C for wheat — Mcmaster & Wilhelm 1997).
        # Thresholds are cumulative GDD above gdd_t_base to reach each stage.
        # At IGP T_mean ≈16°C: 16 GDD/d → germination ends wk1, veg ends wk9, rep ends wk14
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 900, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 5.5, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.2, "reproductive": 5.5, "maturity": 2.0},
        "category": "field_crop",
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
        # Rice T_base=10°C (IRRI standard). At kharif T_mean≈28°C: 18 GDD/d
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 80, "reproductive": 700, "maturity": 1400},
        "waterlogging_sensitive": False,
        "lai_max": 6.0, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.4, "vegetative": 3.5, "reproductive": 6.0, "maturity": 3.0},
        "category": "field_crop",
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
        # Maize T_base=10°C (CIMMYT). At T_mean≈28°C: 18 GDD/d
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 120, "reproductive": 900, "maturity": 1450},
        "waterlogging_sensitive": True,
        "lai_max": 5.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.0, "reproductive": 5.0, "maturity": 1.8},
        "category": "field_crop",
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
        # Cotton T_base=14°C. At T_mean≈30°C: 16 GDD/d
        "gdd_t_base": 14.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 700, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.2, "vegetative": 2.5, "reproductive": 4.5, "maturity": 2.0},
        "category": "field_crop",
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
        # Soybean T_base=10°C. At T_mean≈28°C: 18 GDD/d
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 90, "reproductive": 600, "maturity": 1100},
        "waterlogging_sensitive": True,
        "lai_max": 5.0, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.0, "reproductive": 5.0, "maturity": 1.5},
        "category": "field_crop",
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
        # Tomato T_base=10°C. At T_mean≈22°C: 12 GDD/d
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 80, "reproductive": 500, "maturity": 950},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.5, "reproductive": 4.0, "maturity": 1.5},
        "category": "vegetable",
    },
    "potato": {
        "display_name": "Potato (Solanum tuberosum)",
        "base_yield_t_ha": 30.0,
        "growing_days": 110,
        "optimal_temp_min": 14.0, "optimal_temp_max": 22.0,
        "critical_temp_high": 30.0, "critical_temp_low": 4.0,
        "optimal_ph_min": 5.0, "optimal_ph_max": 6.5,
        "ec_threshold_ds_m": 1.7, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 4.0, "p_demand_kg_per_t": 0.9, "k_demand_kg_per_t": 6.0,
        "kc": {"germination": 0.50, "vegetative": 0.85, "reproductive": 1.15, "maturity": 0.75},
        # Potato T_base=4°C. At T_mean≈16°C: 12 GDD/d
        "gdd_t_base": 4.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 600, "maturity": 1100},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.60,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.8, "reproductive": 4.5, "maturity": 1.8},
        "category": "vegetable",
    },
    "chickpea": {
        "display_name": "Chickpea (Cicer arietinum)",
        "base_yield_t_ha": 1.8,
        "growing_days": 100,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 35.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 8.0,
        "ec_threshold_ds_m": 3.9, "ec_slope_pct_per_ds_m": 7.4,
        "n_demand_kg_per_t": 12.0, "p_demand_kg_per_t": 4.0, "k_demand_kg_per_t": 10.0,
        "kc": {"germination": 0.40, "vegetative": 0.70, "reproductive": 1.00, "maturity": 0.50},
        # Chickpea T_base=0°C. Cool-season legume, at T_mean≈18°C: 18 GDD/d
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 80, "reproductive": 600, "maturity": 1100},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.2, "vegetative": 2.0, "reproductive": 3.5, "maturity": 1.0},
        "category": "field_crop",
    },
    "mustard": {
        "display_name": "Mustard (Brassica juncea)",
        "base_yield_t_ha": 2.0,
        "growing_days": 110,
        "optimal_temp_min": 10.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 32.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 8.0,  # mustard tolerates alkaline IGP soils
        "ec_threshold_ds_m": 2.9, "ec_slope_pct_per_ds_m": 9.7,
        "n_demand_kg_per_t": 30.0, "p_demand_kg_per_t": 7.0, "k_demand_kg_per_t": 15.0,
        "kc": {"germination": 0.35, "vegetative": 0.80, "reproductive": 1.05, "maturity": 0.55},
        # Mustard T_base=0°C. At IGP T_mean≈16°C: 16 GDD/d
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 80, "reproductive": 550, "maturity": 1050},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.2, "vegetative": 2.3, "reproductive": 4.0, "maturity": 1.2},
        "category": "field_crop",
    },

    # ── Vegetables ────────────────────────────────────────────────────────────
    "onion": {
        "display_name": "Onion (Allium cepa)",
        "category": "vegetable",
        "base_yield_t_ha": 25.0,
        "growing_days": 150,
        "optimal_temp_min": 13.0, "optimal_temp_max": 24.0,
        "critical_temp_high": 30.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.2, "ec_slope_pct_per_ds_m": 16.0,
        "n_demand_kg_per_t": 3.5, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 3.5,
        "kc": {"germination": 0.50, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.75},
        "gdd_t_base": 7.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1100, "maturity": 1650},
        "waterlogging_sensitive": True,
        "lai_max": 2.5, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.3, "vegetative": 1.8, "reproductive": 2.5, "maturity": 1.0},
    },
    "okra": {
        "display_name": "Okra / Bhindi (Abelmoschus esculentus)",
        "category": "vegetable",
        "base_yield_t_ha": 12.0,
        "growing_days": 120,
        "optimal_temp_min": 22.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 42.0, "critical_temp_low": 16.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 8.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 5.5,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.75},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 900, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.2, "reproductive": 3.5, "maturity": 1.5},
    },
    "brinjal": {
        "display_name": "Brinjal / Eggplant (Solanum melongena)",
        "category": "vegetable",
        "base_yield_t_ha": 25.0,
        "growing_days": 120,
        "optimal_temp_min": 22.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 40.0, "critical_temp_low": 12.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.1, "ec_slope_pct_per_ds_m": 6.9,
        "n_demand_kg_per_t": 3.0, "p_demand_kg_per_t": 0.7, "k_demand_kg_per_t": 4.5,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.15, "maturity": 0.80},
        "gdd_t_base": 12.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 1000, "maturity": 1600},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.3, "reproductive": 3.5, "maturity": 1.8},
    },
    "cauliflower": {
        "display_name": "Cauliflower (Brassica oleracea var. botrytis)",
        "category": "vegetable",
        "base_yield_t_ha": 22.0,
        "growing_days": 120,
        "optimal_temp_min": 14.0, "optimal_temp_max": 20.0,
        "critical_temp_high": 28.0, "critical_temp_low": 2.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.8, "ec_slope_pct_per_ds_m": 6.2,
        "n_demand_kg_per_t": 4.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 4.5,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.05, "maturity": 0.80},
        "gdd_t_base": 5.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 900, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.5, "reproductive": 4.0, "maturity": 2.0},
    },
    "cabbage": {
        "display_name": "Cabbage (Brassica oleracea var. capitata)",
        "category": "vegetable",
        "base_yield_t_ha": 40.0,
        "growing_days": 120,
        "optimal_temp_min": 15.0, "optimal_temp_max": 20.0,
        "critical_temp_high": 30.0, "critical_temp_low": -3.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.8, "ec_slope_pct_per_ds_m": 9.7,
        "n_demand_kg_per_t": 2.5, "p_demand_kg_per_t": 0.5, "k_demand_kg_per_t": 3.5,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.05, "maturity": 0.80},
        "gdd_t_base": 5.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 900, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.8, "reproductive": 4.5, "maturity": 2.5},
    },
    "pea": {
        "display_name": "Pea (Pisum sativum)",
        "category": "vegetable",
        "base_yield_t_ha": 10.0,
        "growing_days": 90,
        "optimal_temp_min": 13.0, "optimal_temp_max": 18.0,
        "critical_temp_high": 30.0, "critical_temp_low": -3.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 3.4, "ec_slope_pct_per_ds_m": 10.6,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.2, "k_demand_kg_per_t": 4.0,
        "kc": {"germination": 0.40, "vegetative": 0.70, "reproductive": 1.10, "maturity": 0.55},
        "gdd_t_base": 4.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 600, "maturity": 950},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.2, "reproductive": 3.5, "maturity": 1.2},
    },
    "carrot": {
        "display_name": "Carrot (Daucus carota)",
        "category": "vegetable",
        "base_yield_t_ha": 30.0,
        "growing_days": 120,
        "optimal_temp_min": 15.0, "optimal_temp_max": 20.0,
        "critical_temp_high": 30.0, "critical_temp_low": -3.0,
        "optimal_ph_min": 5.8, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.0, "ec_slope_pct_per_ds_m": 14.0,
        "n_demand_kg_per_t": 2.5, "p_demand_kg_per_t": 0.6, "k_demand_kg_per_t": 3.5,
        "kc": {"germination": 0.40, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.80},
        "gdd_t_base": 5.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 900, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 3.0, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.0, "reproductive": 3.0, "maturity": 1.5},
    },
    "garlic": {
        "display_name": "Garlic (Allium sativum)",
        "category": "vegetable",
        "base_yield_t_ha": 10.0,
        "growing_days": 180,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 32.0, "critical_temp_low": -3.0,
        "optimal_ph_min": 5.8, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 3.9, "ec_slope_pct_per_ds_m": 6.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 5.5,
        "kc": {"germination": 0.50, "vegetative": 0.80, "reproductive": 1.00, "maturity": 0.70},
        "gdd_t_base": 5.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1100, "maturity": 1700},
        "waterlogging_sensitive": True,
        "lai_max": 2.5, "k_extinction": 0.40,
        "lai_by_stage": {"germination": 0.3, "vegetative": 1.8, "reproductive": 2.5, "maturity": 1.0},
    },
    "spinach": {
        "display_name": "Spinach (Spinacia oleracea)",
        "category": "vegetable",
        "base_yield_t_ha": 15.0,
        "growing_days": 60,
        "optimal_temp_min": 10.0, "optimal_temp_max": 20.0,
        "critical_temp_high": 25.0, "critical_temp_low": -5.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 7.6,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 5.0,
        "kc": {"germination": 0.50, "vegetative": 0.90, "reproductive": 1.05, "maturity": 0.75},
        "gdd_t_base": 4.0,
        "gdd_stages": {"vegetative": 80, "reproductive": 400, "maturity": 620},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.4, "vegetative": 2.5, "reproductive": 3.5, "maturity": 2.0},
    },

    # ── Spices ────────────────────────────────────────────────────────────────
    "cumin": {
        "display_name": "Cumin / Jeera (Cuminum cyminum)",
        "category": "spice",
        "base_yield_t_ha": 1.2,
        "growing_days": 110,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 30.0, "critical_temp_low": 3.0,
        "optimal_ph_min": 6.5, "optimal_ph_max": 8.0,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 30.0, "p_demand_kg_per_t": 7.0, "k_demand_kg_per_t": 20.0,
        "kc": {"germination": 0.35, "vegetative": 0.70, "reproductive": 1.00, "maturity": 0.55},
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1200, "maturity": 1800},
        "waterlogging_sensitive": True,
        "lai_max": 2.0, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.2, "vegetative": 1.3, "reproductive": 2.0, "maturity": 0.8},
    },
    "coriander": {
        "display_name": "Coriander / Dhania (Coriandrum sativum)",
        "category": "spice",
        "base_yield_t_ha": 1.3,
        "growing_days": 100,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 32.0, "critical_temp_low": 3.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 2.5, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 25.0, "p_demand_kg_per_t": 6.0, "k_demand_kg_per_t": 15.0,
        "kc": {"germination": 0.35, "vegetative": 0.75, "reproductive": 1.00, "maturity": 0.55},
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 1000, "maturity": 1600},
        "waterlogging_sensitive": True,
        "lai_max": 2.5, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.2, "vegetative": 1.5, "reproductive": 2.5, "maturity": 0.8},
    },
    "fenugreek": {
        "display_name": "Fenugreek / Methi (Trigonella foenum-graecum)",
        "category": "spice",
        "base_yield_t_ha": 1.5,
        "growing_days": 100,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 35.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 5.8, "optimal_ph_max": 8.2,
        "ec_threshold_ds_m": 2.5, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 20.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 12.0,
        "kc": {"germination": 0.40, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.55},
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 1000, "maturity": 1600},
        "waterlogging_sensitive": True,
        "lai_max": 2.5, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.3, "vegetative": 1.6, "reproductive": 2.5, "maturity": 1.0},
    },
    "chilli": {
        "display_name": "Chilli / Mirch (Capsicum annuum)",
        "category": "spice",
        "base_yield_t_ha": 12.0,
        "growing_days": 150,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 12.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.5, "ec_slope_pct_per_ds_m": 14.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.2, "k_demand_kg_per_t": 5.5,
        "kc": {"germination": 0.45, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.80},
        "gdd_t_base": 12.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1400, "maturity": 2200},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.2, "reproductive": 3.5, "maturity": 2.0},
    },
    "turmeric": {
        "display_name": "Turmeric (Curcuma longa)",
        "category": "spice",
        "base_yield_t_ha": 25.0,
        "growing_days": 280,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 15.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 6.0,
        "kc": {"germination": 0.50, "vegetative": 0.90, "reproductive": 1.15, "maturity": 0.80},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 350, "reproductive": 2200, "maturity": 3400},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.60,
        "lai_by_stage": {"germination": 0.4, "vegetative": 3.0, "reproductive": 4.5, "maturity": 2.5},
    },
    "ginger": {
        "display_name": "Ginger (Zingiber officinale)",
        "category": "spice",
        "base_yield_t_ha": 20.0,
        "growing_days": 260,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 15.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 6.5,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.2, "k_demand_kg_per_t": 6.5,
        "kc": {"germination": 0.50, "vegetative": 0.90, "reproductive": 1.15, "maturity": 0.80},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 350, "reproductive": 2000, "maturity": 3200},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.60,
        "lai_by_stage": {"germination": 0.4, "vegetative": 2.8, "reproductive": 4.0, "maturity": 2.0},
    },

    # ── Flowers ───────────────────────────────────────────────────────────────
    "marigold": {
        "display_name": "Marigold (Tagetes erecta)",
        "category": "flower",
        "base_yield_t_ha": 22.0,
        "growing_days": 100,
        "optimal_temp_min": 18.0, "optimal_temp_max": 26.0,
        "critical_temp_high": 35.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 3.0, "p_demand_kg_per_t": 0.7, "k_demand_kg_per_t": 4.0,
        "kc": {"germination": 0.40, "vegetative": 0.80, "reproductive": 1.05, "maturity": 0.80},
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 800, "maturity": 1200},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.5, "reproductive": 3.5, "maturity": 2.5},
    },
    "chrysanthemum": {
        "display_name": "Chrysanthemum (Chrysanthemum morifolium)",
        "category": "flower",
        "base_yield_t_ha": 18.0,
        "growing_days": 120,
        "optimal_temp_min": 15.0, "optimal_temp_max": 20.0,
        "critical_temp_high": 30.0, "critical_temp_low": 2.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 6.5,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 3.5, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 4.5,
        "kc": {"germination": 0.40, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.85},
        "gdd_t_base": 5.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 800, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.2, "reproductive": 3.5, "maturity": 2.5},
    },

    # ── Fruits ────────────────────────────────────────────────────────────────
    # Modelled as a single productive season (flowering → harvest)
    "mango": {
        "display_name": "Mango (Mangifera indica)",
        "category": "fruit",
        "base_yield_t_ha": 12.0,
        "growing_days": 180,
        "optimal_temp_min": 24.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 42.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.5, "ec_slope_pct_per_ds_m": 14.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 1.0, "k_demand_kg_per_t": 6.0,
        "kc": {"germination": 0.55, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.90},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 250, "reproductive": 1500, "maturity": 2500},
        "waterlogging_sensitive": True,
        "lai_max": 5.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 1.0, "vegetative": 3.0, "reproductive": 5.0, "maturity": 4.0},
    },
    "banana": {
        "display_name": "Banana (Musa spp.)",
        "category": "fruit",
        "base_yield_t_ha": 45.0,
        "growing_days": 300,
        "optimal_temp_min": 24.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 3.0, "p_demand_kg_per_t": 0.5, "k_demand_kg_per_t": 8.0,
        "kc": {"germination": 0.50, "vegetative": 0.90, "reproductive": 1.20, "maturity": 0.90},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 400, "reproductive": 2500, "maturity": 3700},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.8, "vegetative": 3.0, "reproductive": 4.5, "maturity": 3.5},
    },
    "citrus": {
        "display_name": "Citrus (Citrus sinensis / limon)",
        "category": "fruit",
        "base_yield_t_ha": 25.0,
        "growing_days": 200,
        "optimal_temp_min": 20.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 2.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 6.5,
        "ec_threshold_ds_m": 1.7, "ec_slope_pct_per_ds_m": 16.0,
        "n_demand_kg_per_t": 4.0, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 5.0,
        "kc": {"germination": 0.55, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.90},
        "gdd_t_base": 12.0,
        "gdd_stages": {"vegetative": 300, "reproductive": 1700, "maturity": 2600},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 1.0, "vegetative": 2.8, "reproductive": 4.0, "maturity": 3.5},
    },
    "grapes": {
        "display_name": "Grapes (Vitis vinifera)",
        "category": "fruit",
        "base_yield_t_ha": 18.0,
        "growing_days": 150,
        "optimal_temp_min": 22.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 40.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.5, "ec_slope_pct_per_ds_m": 9.5,
        "n_demand_kg_per_t": 4.5, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 7.0,
        "kc": {"germination": 0.45, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.85},
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 250, "reproductive": 1500, "maturity": 2300},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.5, "vegetative": 2.5, "reproductive": 3.5, "maturity": 2.5},
    },
    "guava": {
        "display_name": "Guava (Psidium guajava)",
        "category": "fruit",
        "base_yield_t_ha": 22.0,
        "growing_days": 180,
        "optimal_temp_min": 22.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 42.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 4.5, "optimal_ph_max": 8.2,
        "ec_threshold_ds_m": 2.0, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 4.0, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 5.0,
        "kc": {"germination": 0.50, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.90},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 250, "reproductive": 1400, "maturity": 2200},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.8, "vegetative": 2.8, "reproductive": 4.0, "maturity": 3.0},
    },
    "pomegranate": {
        "display_name": "Pomegranate (Punica granatum)",
        "category": "fruit",
        "base_yield_t_ha": 18.0,
        "growing_days": 180,
        "optimal_temp_min": 25.0, "optimal_temp_max": 35.0,
        "critical_temp_high": 42.0, "critical_temp_low": 5.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 4.0, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 5.0, "p_demand_kg_per_t": 0.8, "k_demand_kg_per_t": 5.5,
        "kc": {"germination": 0.45, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.85},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 250, "reproductive": 1500, "maturity": 2500},
        "waterlogging_sensitive": True,
        "lai_max": 3.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.5, "vegetative": 2.5, "reproductive": 3.5, "maturity": 2.8},
    },
    "papaya": {
        "display_name": "Papaya (Carica papaya)",
        "category": "fruit",
        "base_yield_t_ha": 50.0,
        "growing_days": 240,
        "optimal_temp_min": 22.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.0, "ec_slope_pct_per_ds_m": 12.0,
        "n_demand_kg_per_t": 3.0, "p_demand_kg_per_t": 0.5, "k_demand_kg_per_t": 5.0,
        "kc": {"germination": 0.55, "vegetative": 0.85, "reproductive": 1.15, "maturity": 0.90},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 300, "reproductive": 1900, "maturity": 3000},
        "waterlogging_sensitive": True,
        "lai_max": 5.0, "k_extinction": 0.60,
        "lai_by_stage": {"germination": 1.0, "vegetative": 3.5, "reproductive": 5.0, "maturity": 4.0},
    },
    "watermelon": {
        "display_name": "Watermelon (Citrullus lanatus)",
        "category": "fruit",
        "base_yield_t_ha": 40.0,
        "growing_days": 90,
        "optimal_temp_min": 24.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 40.0, "critical_temp_low": 12.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 1.0, "ec_slope_pct_per_ds_m": 8.0,
        "n_demand_kg_per_t": 2.5, "p_demand_kg_per_t": 0.5, "k_demand_kg_per_t": 4.0,
        "kc": {"germination": 0.40, "vegetative": 0.80, "reproductive": 1.00, "maturity": 0.75},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 800, "maturity": 1300},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.8, "reproductive": 4.0, "maturity": 2.5},
    },

    # ── Additional field crops ─────────────────────────────────────────────────
    "sugarcane": {
        "display_name": "Sugarcane (Saccharum officinarum)",
        "category": "field_crop",
        "base_yield_t_ha": 80.0,
        "growing_days": 350,
        "optimal_temp_min": 26.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 38.0, "critical_temp_low": 15.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.7, "ec_slope_pct_per_ds_m": 5.9,
        "n_demand_kg_per_t": 1.5, "p_demand_kg_per_t": 0.3, "k_demand_kg_per_t": 2.0,
        "kc": {"germination": 0.55, "vegetative": 1.00, "reproductive": 1.25, "maturity": 0.75},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 450, "reproductive": 3000, "maturity": 4400},
        "waterlogging_sensitive": False,
        "lai_max": 6.0, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.5, "vegetative": 4.0, "reproductive": 6.0, "maturity": 3.5},
    },
    "bajra": {
        "display_name": "Pearl Millet / Bajra (Pennisetum glaucum)",
        "category": "field_crop",
        "base_yield_t_ha": 3.5,
        "growing_days": 80,
        "optimal_temp_min": 26.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 40.0, "critical_temp_low": 12.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 1.8, "ec_slope_pct_per_ds_m": 8.0,
        "n_demand_kg_per_t": 20.0, "p_demand_kg_per_t": 4.5, "k_demand_kg_per_t": 12.0,
        "kc": {"germination": 0.35, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.55},
        "gdd_t_base": 12.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 850, "maturity": 1350},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.0, "reproductive": 4.5, "maturity": 1.8},
    },
    "jowar": {
        "display_name": "Sorghum / Jowar (Sorghum bicolor)",
        "category": "field_crop",
        "base_yield_t_ha": 4.5,
        "growing_days": 110,
        "optimal_temp_min": 26.0, "optimal_temp_max": 32.0,
        "critical_temp_high": 38.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.5,
        "ec_threshold_ds_m": 6.8, "ec_slope_pct_per_ds_m": 16.0,
        "n_demand_kg_per_t": 22.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 15.0,
        "kc": {"germination": 0.35, "vegetative": 0.85, "reproductive": 1.15, "maturity": 0.60},
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1200, "maturity": 1900},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.55,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.8, "reproductive": 4.5, "maturity": 1.8},
    },
    "groundnut": {
        "display_name": "Groundnut / Peanut (Arachis hypogaea)",
        "category": "field_crop",
        "base_yield_t_ha": 3.2,
        "growing_days": 125,
        "optimal_temp_min": 24.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 15.0,
        "optimal_ph_min": 5.5, "optimal_ph_max": 7.0,
        "ec_threshold_ds_m": 3.2, "ec_slope_pct_per_ds_m": 29.0,
        "n_demand_kg_per_t": 10.0, "p_demand_kg_per_t": 4.0, "k_demand_kg_per_t": 12.0,
        "kc": {"germination": 0.40, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.60},
        "gdd_t_base": 15.0,
        "gdd_stages": {"vegetative": 150, "reproductive": 900, "maturity": 1500},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.0, "reproductive": 4.5, "maturity": 2.0},
    },
    "lentil": {
        "display_name": "Lentil (Lens culinaris)",
        "category": "field_crop",
        "base_yield_t_ha": 1.8,
        "growing_days": 100,
        "optimal_temp_min": 15.0, "optimal_temp_max": 25.0,
        "critical_temp_high": 30.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 8.0,
        "ec_threshold_ds_m": 4.0, "ec_slope_pct_per_ds_m": 8.0,
        "n_demand_kg_per_t": 12.0, "p_demand_kg_per_t": 4.0, "k_demand_kg_per_t": 10.0,
        "kc": {"germination": 0.40, "vegetative": 0.70, "reproductive": 1.00, "maturity": 0.50},
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 700, "maturity": 1300},
        "waterlogging_sensitive": True,
        "lai_max": 3.0, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.2, "vegetative": 2.0, "reproductive": 3.0, "maturity": 1.0},
    },
    "pigeonpea": {
        "display_name": "Pigeonpea / Arhar (Cajanus cajan)",
        "category": "field_crop",
        "base_yield_t_ha": 2.2,
        "growing_days": 160,
        "optimal_temp_min": 22.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 38.0, "critical_temp_low": 10.0,
        "optimal_ph_min": 5.0, "optimal_ph_max": 8.5,
        "ec_threshold_ds_m": 1.8, "ec_slope_pct_per_ds_m": 10.0,
        "n_demand_kg_per_t": 10.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 12.0,
        "kc": {"germination": 0.40, "vegetative": 0.75, "reproductive": 1.05, "maturity": 0.55},
        "gdd_t_base": 10.0,
        "gdd_stages": {"vegetative": 250, "reproductive": 1700, "maturity": 2700},
        "waterlogging_sensitive": True,
        "lai_max": 4.0, "k_extinction": 0.50,
        "lai_by_stage": {"germination": 0.3, "vegetative": 2.5, "reproductive": 4.0, "maturity": 1.8},
    },
    "barley": {
        "display_name": "Barley (Hordeum vulgare)",
        "category": "field_crop",
        "base_yield_t_ha": 4.5,
        "growing_days": 105,
        "optimal_temp_min": 10.0, "optimal_temp_max": 22.0,
        "critical_temp_high": 32.0, "critical_temp_low": 0.0,
        "optimal_ph_min": 6.0, "optimal_ph_max": 8.5,
        "ec_threshold_ds_m": 8.0, "ec_slope_pct_per_ds_m": 5.0,
        "n_demand_kg_per_t": 22.0, "p_demand_kg_per_t": 5.0, "k_demand_kg_per_t": 15.0,
        "kc": {"germination": 0.35, "vegetative": 0.80, "reproductive": 1.10, "maturity": 0.60},
        "gdd_t_base": 0.0,
        "gdd_stages": {"vegetative": 100, "reproductive": 800, "maturity": 1400},
        "waterlogging_sensitive": True,
        "lai_max": 5.0, "k_extinction": 0.45,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.2, "reproductive": 5.0, "maturity": 2.0},
    },
    "sunflower": {
        "display_name": "Sunflower (Helianthus annuus)",
        "category": "field_crop",
        "base_yield_t_ha": 2.8,
        "growing_days": 110,
        "optimal_temp_min": 22.0, "optimal_temp_max": 30.0,
        "critical_temp_high": 36.0, "critical_temp_low": 7.0,
        "optimal_ph_min": 5.7, "optimal_ph_max": 8.0,
        "ec_threshold_ds_m": 4.8, "ec_slope_pct_per_ds_m": 5.0,
        "n_demand_kg_per_t": 25.0, "p_demand_kg_per_t": 6.0, "k_demand_kg_per_t": 20.0,
        "kc": {"germination": 0.35, "vegetative": 0.80, "reproductive": 1.15, "maturity": 0.60},
        "gdd_t_base": 7.0,
        "gdd_stages": {"vegetative": 200, "reproductive": 1200, "maturity": 1900},
        "waterlogging_sensitive": True,
        "lai_max": 4.5, "k_extinction": 0.60,
        "lai_by_stage": {"germination": 0.3, "vegetative": 3.0, "reproductive": 4.5, "maturity": 1.8},
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
    "tube-well": 30.0,  # tube-well source, furrow/flood delivery — typical IGP application
}

OPTIMAL_RADIATION_MJ_PER_WEEK: float = 100.0  # C3 crop canopy saturates ~14 MJ/m²/day; 140 over-penalised winter rabi crops

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

# ---------------------------------------------------------------------------
# Indian state soil presets (beyond Punjab)
# Values from NBSS&LUP state soil surveys, ICAR zonal reports, and
# Soil Health Card district averages (2020-22 tranche)
# ---------------------------------------------------------------------------
INDIA_UP_BIHAR_PRESETS: dict[str, dict] = {
    "up_western": {
        "display_name": "UP - Western (Muzaffarnagar/Meerut, loam IGP)",
        "texture": "loam",
        "ph": 7.90, "ec_ds_m": 0.42,
        "nitrogen_kg_ha": 80.0, "phosphorus_kg_ha": 22.0,
        "potassium_kg_ha": 285.0, "organic_matter_pct": 0.72,
    },
    "up_eastern": {
        "display_name": "UP - Eastern (Varanasi/Gorakhpur, clay loam alluvium)",
        "texture": "clay_loam",
        "ph": 8.10, "ec_ds_m": 0.52,
        "nitrogen_kg_ha": 70.0, "phosphorus_kg_ha": 18.0,
        "potassium_kg_ha": 240.0, "organic_matter_pct": 0.65,
    },
    "bihar_plains": {
        "display_name": "Bihar - Gangetic Plains (loam, rice-wheat belt)",
        "texture": "loam",
        "ph": 7.80, "ec_ds_m": 0.38,
        "nitrogen_kg_ha": 72.0, "phosphorus_kg_ha": 20.0,
        "potassium_kg_ha": 220.0, "organic_matter_pct": 0.80,
    },
}

INDIA_CENTRAL_PRESETS: dict[str, dict] = {
    "maharashtra_vidarbha": {
        "display_name": "Maharashtra - Vidarbha (Vertisol, cotton-soybean zone)",
        "texture": "clay",
        "ph": 7.50, "ec_ds_m": 0.35,
        "nitrogen_kg_ha": 95.0, "phosphorus_kg_ha": 16.0,
        "potassium_kg_ha": 320.0, "organic_matter_pct": 0.95,
    },
    "mp_malwa": {
        "display_name": "Madhya Pradesh - Malwa Plateau (clay loam, black cotton soil)",
        "texture": "clay_loam",
        "ph": 7.80, "ec_ds_m": 0.44,
        "nitrogen_kg_ha": 85.0, "phosphorus_kg_ha": 20.0,
        "potassium_kg_ha": 340.0, "organic_matter_pct": 0.88,
    },
    "rajasthan_semi_arid": {
        "display_name": "Rajasthan - Semi-arid zone (sandy loam, aridisol)",
        "texture": "sandy_loam",
        "ph": 8.30, "ec_ds_m": 0.72,
        "nitrogen_kg_ha": 42.0, "phosphorus_kg_ha": 10.0,
        "potassium_kg_ha": 350.0, "organic_matter_pct": 0.38,
    },
}

INDIA_SOUTH_PRESETS: dict[str, dict] = {
    "tamil_nadu_cauvery": {
        "display_name": "Tamil Nadu - Cauvery Delta (clay loam, rice zone)",
        "texture": "clay_loam",
        "ph": 6.80, "ec_ds_m": 0.55,
        "nitrogen_kg_ha": 110.0, "phosphorus_kg_ha": 35.0,
        "potassium_kg_ha": 280.0, "organic_matter_pct": 1.10,
    },
    "karnataka_deccan": {
        "display_name": "Karnataka - Deccan Plateau (red lateritic, ragi-groundnut)",
        "texture": "sandy_loam",
        "ph": 6.30, "ec_ds_m": 0.28,
        "nitrogen_kg_ha": 75.0, "phosphorus_kg_ha": 25.0,
        "potassium_kg_ha": 190.0, "organic_matter_pct": 0.80,
    },
    "gujarat_semi_arid": {
        "display_name": "Gujarat - Semi-arid (loam, cotton-groundnut zone)",
        "texture": "loam",
        "ph": 7.60, "ec_ds_m": 0.65,
        "nitrogen_kg_ha": 68.0, "phosphorus_kg_ha": 18.0,
        "potassium_kg_ha": 260.0, "organic_matter_pct": 0.70,
    },
}

# ---------------------------------------------------------------------------
# Germany — detailed regional soil presets
# Sources: BGR BUEK-200 soil map, Thünen Atlas 2023, UBA soil monitoring,
# Kühn et al. (2012) Soil Tillage Res., Sieling et al. (2003) Eur J Agron
# pH method: CaCl2 (standard German lab protocol; +0.5 unit cf. H2O method)
# N = mineral N (EUF or KCl extraction); P = CAL-P; K = CAL-K (German DIN)
# ---------------------------------------------------------------------------
GERMANY_SOIL_PRESETS: dict[str, dict] = {
    "germany_saxony_anhalt": {
        "display_name": "Germany — Saxony-Anhalt, Magdeburger Börde (Chernozem, premium arable)",
        "texture": "clay_loam",
        "ph": 7.20,         # CaCl2 7.1-7.4; H2O equiv ~7.6-7.9
        "ec_ds_m": 0.28,
        "nitrogen_kg_ha": 115.0,   # high N mineralisation from Chernozem OM
        "phosphorus_kg_ha": 68.0,  # CAL-P medium-high
        "potassium_kg_ha": 390.0,  # CAL-K adequate
        "organic_matter_pct": 3.20, # Schwarzerde SOC 1.8-2.3 % → OM 3.1-4.0 %
    },
    "germany_bavaria": {
        "display_name": "Germany — Bavaria, Central Plateau (Luvisol/Parabraunerde)",
        "texture": "loam",
        "ph": 6.70,         # CaCl2 6.5-7.0; typical Luvisol
        "ec_ds_m": 0.25,
        "nitrogen_kg_ha": 88.0,
        "phosphorus_kg_ha": 55.0,
        "potassium_kg_ha": 278.0,
        "organic_matter_pct": 2.80,
    },
    "germany_lower_saxony": {
        "display_name": "Germany — Lower Saxony, Hanover-Braunschweig Börde (Luvisol, loess)",
        "texture": "loam",
        "ph": 6.40,         # CaCl2 6.2-6.7
        "ec_ds_m": 0.28,
        "nitrogen_kg_ha": 82.0,
        "phosphorus_kg_ha": 50.0,
        "potassium_kg_ha": 252.0,
        "organic_matter_pct": 2.90,
    },
    "germany_nrw": {
        "display_name": "Germany — North Rhine-Westphalia, Cologne Bay (Luvisol, loess, Atlantic)",
        "texture": "loam",
        "ph": 6.60,         # CaCl2 6.4-6.9
        "ec_ds_m": 0.32,
        "nitrogen_kg_ha": 92.0,
        "phosphorus_kg_ha": 60.0,
        "potassium_kg_ha": 298.0,
        "organic_matter_pct": 2.50,
    },
    "germany_mecklenburg": {
        "display_name": "Germany — Mecklenburg-Vorpommern (Luvisol/Cambisol, Baltic glacial till)",
        "texture": "loam",
        "ph": 6.50,         # CaCl2 6.3-6.8
        "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 72.0,
        "phosphorus_kg_ha": 44.0,
        "potassium_kg_ha": 228.0,
        "organic_matter_pct": 2.60,
    },
    "germany_brandenburg": {
        "display_name": "Germany — Brandenburg (Arenosol/Podzol, diluvial sandy soils, lowest fertility)",
        "texture": "sandy_loam",
        "ph": 5.90,         # CaCl2 5.6-6.3; acid sandy soil
        "ec_ds_m": 0.18,
        "nitrogen_kg_ha": 45.0,    # low N; high leaching
        "phosphorus_kg_ha": 32.0,
        "potassium_kg_ha": 168.0,  # low K; sandy
        "organic_matter_pct": 1.80, # low OM; SOC ~1.0 %
    },
}

# ---------------------------------------------------------------------------
# Global soil presets
# Sources: FAO HWSD v2.0, SoilGrids 250m, ISRIC World Soil DB,
# CIMMYT/IRRI country-specific field trial reports
# ---------------------------------------------------------------------------
EAST_ASIA_PRESETS: dict[str, dict] = {
    "china_north_plain": {
        "display_name": "China - North China Plain (loam, wheat-maize belt)",
        "texture": "loam",
        "ph": 7.90, "ec_ds_m": 0.45,
        "nitrogen_kg_ha": 85.0, "phosphorus_kg_ha": 40.0,
        "potassium_kg_ha": 320.0, "organic_matter_pct": 1.20,
    },
    "china_yangtze": {
        "display_name": "China - Yangtze Delta (clay loam, rice-wheat zone)",
        "texture": "clay_loam",
        "ph": 6.50, "ec_ds_m": 0.40,
        "nitrogen_kg_ha": 110.0, "phosphorus_kg_ha": 55.0,
        "potassium_kg_ha": 200.0, "organic_matter_pct": 2.00,
    },
    "vietnam_mekong": {
        "display_name": "Vietnam - Mekong Delta (clay, intensive rice)",
        "texture": "clay",
        "ph": 5.50, "ec_ds_m": 0.60,
        "nitrogen_kg_ha": 120.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 150.0, "organic_matter_pct": 2.80,
    },
    "thailand_central": {
        "display_name": "Thailand - Central Plain (clay loam, rice)",
        "texture": "clay_loam",
        "ph": 6.00, "ec_ds_m": 0.40,
        "nitrogen_kg_ha": 95.0, "phosphorus_kg_ha": 25.0,
        "potassium_kg_ha": 180.0, "organic_matter_pct": 1.80,
    },
}

SOUTHEAST_ASIA_PRESETS: dict[str, dict] = {
    "indonesia_java": {
        "display_name": "Indonesia - Java (clay loam, volcanic Andisols, rice-maize)",
        "texture": "clay_loam",
        "ph": 6.20, "ec_ds_m": 0.30,
        "nitrogen_kg_ha": 130.0, "phosphorus_kg_ha": 45.0,
        "potassium_kg_ha": 280.0, "organic_matter_pct": 3.50,
    },
    "philippines_luzon": {
        "display_name": "Philippines - Luzon lowlands (clay, irrigated rice)",
        "texture": "clay",
        "ph": 6.00, "ec_ds_m": 0.35,
        "nitrogen_kg_ha": 100.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 160.0, "organic_matter_pct": 2.20,
    },
}

AFRICA_PRESETS: dict[str, dict] = {
    "sahel_zone": {
        "display_name": "West Africa - Sahel (sandy, millet-sorghum, low OM)",
        "texture": "sandy",
        "ph": 6.20, "ec_ds_m": 0.20,
        "nitrogen_kg_ha": 28.0, "phosphorus_kg_ha": 6.0,
        "potassium_kg_ha": 80.0, "organic_matter_pct": 0.28,
    },
    "ethiopia_highlands": {
        "display_name": "Ethiopia - Highlands (clay loam Nitosol, teff-wheat-maize)",
        "texture": "clay_loam",
        "ph": 5.80, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 65.0, "phosphorus_kg_ha": 12.0,
        "potassium_kg_ha": 200.0, "organic_matter_pct": 2.50,
    },
    "east_africa_highlands": {
        "display_name": "East Africa - Highlands Kenya/Rwanda (red loam, tea-maize)",
        "texture": "sandy_loam",
        "ph": 5.50, "ec_ds_m": 0.18,
        "nitrogen_kg_ha": 70.0, "phosphorus_kg_ha": 18.0,
        "potassium_kg_ha": 220.0, "organic_matter_pct": 3.00,
    },
    "south_africa_highveld": {
        "display_name": "South Africa - Highveld (sandy loam, maize-soybean)",
        "texture": "sandy_loam",
        "ph": 5.90, "ec_ds_m": 0.16,
        "nitrogen_kg_ha": 55.0, "phosphorus_kg_ha": 20.0,
        "potassium_kg_ha": 190.0, "organic_matter_pct": 1.60,
    },
    "nile_delta": {
        "display_name": "Egypt - Nile Delta (clay loam, irrigated, wheat-rice)",
        "texture": "clay_loam",
        "ph": 8.00, "ec_ds_m": 1.20,
        "nitrogen_kg_ha": 90.0, "phosphorus_kg_ha": 28.0,
        "potassium_kg_ha": 320.0, "organic_matter_pct": 1.40,
    },
}

LATIN_AMERICA_PRESETS: dict[str, dict] = {
    "argentina_pampas": {
        "display_name": "Argentina - Pampas (loam Mollisol, soybean-wheat-maize)",
        "texture": "loam",
        "ph": 6.20, "ec_ds_m": 0.25,
        "nitrogen_kg_ha": 100.0, "phosphorus_kg_ha": 35.0,
        "potassium_kg_ha": 380.0, "organic_matter_pct": 3.80,
    },
    "brazil_cerrado": {
        "display_name": "Brazil - Cerrado (sandy loam Oxisol, soybean-maize, acidic)",
        "texture": "sandy_loam",
        "ph": 5.20, "ec_ds_m": 0.18,
        "nitrogen_kg_ha": 50.0, "phosphorus_kg_ha": 12.0,
        "potassium_kg_ha": 120.0, "organic_matter_pct": 2.00,
    },
    "mexico_central": {
        "display_name": "Mexico - Central Plateau (clay loam, maize-wheat)",
        "texture": "clay_loam",
        "ph": 7.20, "ec_ds_m": 0.38,
        "nitrogen_kg_ha": 75.0, "phosphorus_kg_ha": 22.0,
        "potassium_kg_ha": 260.0, "organic_matter_pct": 1.80,
    },
}

EUROPE_PRESETS: dict[str, dict] = {
    "nw_europe": {
        "display_name": "NW Europe - UK/France/Low Countries (loam, winter wheat-rapeseed)",
        "texture": "loam",
        "ph": 6.50, "ec_ds_m": 0.20,
        "nitrogen_kg_ha": 90.0, "phosphorus_kg_ha": 50.0,
        "potassium_kg_ha": 280.0, "organic_matter_pct": 3.20,
    },
    "central_europe": {
        "display_name": "Central Europe - Germany/Poland (loam Luvisol, wheat-sugar beet)",
        "texture": "loam",
        "ph": 6.80, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 85.0, "phosphorus_kg_ha": 45.0,
        "potassium_kg_ha": 260.0, "organic_matter_pct": 2.80,
    },
    "mediterranean": {
        "display_name": "Mediterranean - Spain/Italy/Greece (clay loam, calcareous)",
        "texture": "clay_loam",
        "ph": 7.80, "ec_ds_m": 0.50,
        "nitrogen_kg_ha": 65.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 300.0, "organic_matter_pct": 1.50,
    },
}

NORTH_AMERICA_PRESETS: dict[str, dict] = {
    "us_corn_belt": {
        "display_name": "USA - Corn Belt / Iowa (loam Mollisol, maize-soybean)",
        "texture": "loam",
        "ph": 6.80, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 110.0, "phosphorus_kg_ha": 60.0,
        "potassium_kg_ha": 350.0, "organic_matter_pct": 4.50,
    },
    "us_great_plains": {
        "display_name": "USA - Great Plains (loam Boroll, winter wheat)",
        "texture": "loam",
        "ph": 7.20, "ec_ds_m": 0.30,
        "nitrogen_kg_ha": 75.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 290.0, "organic_matter_pct": 2.50,
    },
    "canada_prairies": {
        "display_name": "Canada - Saskatchewan Prairies (loam, spring wheat-canola)",
        "texture": "loam",
        "ph": 7.50, "ec_ds_m": 0.28,
        "nitrogen_kg_ha": 80.0, "phosphorus_kg_ha": 35.0,
        "potassium_kg_ha": 300.0, "organic_matter_pct": 3.50,
    },
    "california_valley": {
        "display_name": "USA - California Central Valley (loam, irrigated, diverse crops)",
        "texture": "loam",
        "ph": 7.80, "ec_ds_m": 0.55,
        "nitrogen_kg_ha": 70.0, "phosphorus_kg_ha": 40.0,
        "potassium_kg_ha": 360.0, "organic_matter_pct": 1.80,
    },
}

CENTRAL_ASIA_MIDEAST_PRESETS: dict[str, dict] = {
    "uzbekistan_ferghana": {
        "display_name": "Uzbekistan - Ferghana Valley (loam, irrigated, cotton-wheat, saline)",
        "texture": "loam",
        "ph": 8.20, "ec_ds_m": 2.20,
        "nitrogen_kg_ha": 55.0, "phosphorus_kg_ha": 20.0,
        "potassium_kg_ha": 280.0, "organic_matter_pct": 1.00,
    },
    "euphrates_basin": {
        "display_name": "Iraq/Syria - Euphrates Basin (clay loam, irrigated, wheat-barley)",
        "texture": "clay_loam",
        "ph": 8.10, "ec_ds_m": 1.80,
        "nitrogen_kg_ha": 60.0, "phosphorus_kg_ha": 18.0,
        "potassium_kg_ha": 250.0, "organic_matter_pct": 0.90,
    },
    "turkey_anatolia": {
        "display_name": "Turkey - Central Anatolia (clay loam, dryland wheat-barley)",
        "texture": "clay_loam",
        "ph": 7.60, "ec_ds_m": 0.45,
        "nitrogen_kg_ha": 65.0, "phosphorus_kg_ha": 22.0,
        "potassium_kg_ha": 310.0, "organic_matter_pct": 1.60,
    },
}

AUSTRALIA_PRESETS: dict[str, dict] = {
    "aus_wheatbelt": {
        "display_name": "Australia - WA Wheatbelt (sandy loam, dryland wheat-canola)",
        "texture": "sandy_loam",
        "ph": 5.80, "ec_ds_m": 0.15,
        "nitrogen_kg_ha": 40.0, "phosphorus_kg_ha": 15.0,
        "potassium_kg_ha": 140.0, "organic_matter_pct": 1.20,
    },
    "aus_murray_darling": {
        "display_name": "Australia - Murray-Darling Basin (clay loam, irrigated)",
        "texture": "clay_loam",
        "ph": 7.20, "ec_ds_m": 0.60,
        "nitrogen_kg_ha": 75.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 290.0, "organic_matter_pct": 1.80,
    },
}

# ---------------------------------------------------------------------------
# EU country-level detailed soil presets (France, Poland, UK, NL, Italy, Spain)
# Sources: INRAE, JRC ESDAC, Soils of Europe (Lal & Stewart 2012),
# country NSIS data, FAO/UNESCO Soil Map of the World
# ---------------------------------------------------------------------------
FRANCE_PRESETS: dict[str, dict] = {
    "france_paris_basin": {
        "display_name": "France — Paris Basin (Luvisol/Cambisol, intensive cereal-beet-rapeseed)",
        "texture": "loam",
        "ph": 7.10, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 88.0, "phosphorus_kg_ha": 55.0,
        "potassium_kg_ha": 230.0, "organic_matter_pct": 2.20,
    },
    "france_brittany": {
        "display_name": "France — Brittany / Normandy (Cambisol, Atlantic cereal-potato zone)",
        "texture": "loam",
        "ph": 6.30, "ec_ds_m": 0.20,
        "nitrogen_kg_ha": 82.0, "phosphorus_kg_ha": 48.0,
        "potassium_kg_ha": 210.0, "organic_matter_pct": 3.00,
    },
    "france_southwest": {
        "display_name": "France — South-West (Aquitaine/Midi-Pyrénées, maize-sunflower-grapes)",
        "texture": "loam",
        "ph": 6.80, "ec_ds_m": 0.25,
        "nitrogen_kg_ha": 78.0, "phosphorus_kg_ha": 45.0,
        "potassium_kg_ha": 220.0, "organic_matter_pct": 2.40,
    },
}

POLAND_PRESETS: dict[str, dict] = {
    "poland_greater_poland": {
        "display_name": "Poland — Greater Poland / Wielkopolska (Luvisol, intensive arable)",
        "texture": "loam",
        "ph": 6.50, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 78.0, "phosphorus_kg_ha": 42.0,
        "potassium_kg_ha": 200.0, "organic_matter_pct": 2.00,
    },
    "poland_masovia": {
        "display_name": "Poland — Masovia / Warsaw region (Cambisol, mixed arable)",
        "texture": "sandy_loam",
        "ph": 6.10, "ec_ds_m": 0.18,
        "nitrogen_kg_ha": 62.0, "phosphorus_kg_ha": 32.0,
        "potassium_kg_ha": 165.0, "organic_matter_pct": 1.80,
    },
    "poland_pomerania": {
        "display_name": "Poland — West Pomerania (Luvisol on glacial till, rapeseed-wheat)",
        "texture": "loam",
        "ph": 6.30, "ec_ds_m": 0.20,
        "nitrogen_kg_ha": 70.0, "phosphorus_kg_ha": 38.0,
        "potassium_kg_ha": 185.0, "organic_matter_pct": 2.20,
    },
}

UK_PRESETS: dict[str, dict] = {
    "uk_east_anglia": {
        "display_name": "UK — East Anglia (chalk Luvisol, intensive cereal-potato-beet)",
        "texture": "loam",
        "ph": 7.20, "ec_ds_m": 0.25,
        "nitrogen_kg_ha": 92.0, "phosphorus_kg_ha": 58.0,
        "potassium_kg_ha": 265.0, "organic_matter_pct": 3.00,
    },
    "uk_east_midlands": {
        "display_name": "UK — East Midlands / Lincolnshire (clay Cambisol, cereals-potato)",
        "texture": "clay_loam",
        "ph": 7.30, "ec_ds_m": 0.30,
        "nitrogen_kg_ha": 88.0, "phosphorus_kg_ha": 52.0,
        "potassium_kg_ha": 280.0, "organic_matter_pct": 2.50,
    },
    "uk_scotland": {
        "display_name": "UK — Scotland arable belt (Brown Earth, barley-wheat-potato)",
        "texture": "loam",
        "ph": 6.10, "ec_ds_m": 0.18,
        "nitrogen_kg_ha": 72.0, "phosphorus_kg_ha": 44.0,
        "potassium_kg_ha": 210.0, "organic_matter_pct": 4.00,
    },
}

NETHERLANDS_PRESETS: dict[str, dict] = {
    "netherlands_clay_polders": {
        "display_name": "Netherlands — Clay Polders / Holland (marine clay, intensive potato-veg)",
        "texture": "clay",
        "ph": 7.40, "ec_ds_m": 0.65,
        "nitrogen_kg_ha": 98.0, "phosphorus_kg_ha": 72.0,
        "potassium_kg_ha": 320.0, "organic_matter_pct": 3.50,
    },
    "netherlands_sandy_east": {
        "display_name": "Netherlands — Sandy East (Arenosol, intensive maize-potato-horticulture)",
        "texture": "sandy",
        "ph": 5.90, "ec_ds_m": 0.22,
        "nitrogen_kg_ha": 80.0, "phosphorus_kg_ha": 65.0,
        "potassium_kg_ha": 195.0, "organic_matter_pct": 3.00,
    },
}

ITALY_PRESETS: dict[str, dict] = {
    "italy_po_valley": {
        "display_name": "Italy — Po Valley, Pianura Padana (Fluvisol, wheat-maize-rice)",
        "texture": "loam",
        "ph": 7.50, "ec_ds_m": 0.40,
        "nitrogen_kg_ha": 85.0, "phosphorus_kg_ha": 58.0,
        "potassium_kg_ha": 240.0, "organic_matter_pct": 2.00,
    },
    "italy_apulia": {
        "display_name": "Italy — Apulia / Puglia (Vertisol/calcareous, olive-durum-vegetables)",
        "texture": "clay_loam",
        "ph": 8.00, "ec_ds_m": 0.80,
        "nitrogen_kg_ha": 55.0, "phosphorus_kg_ha": 35.0,
        "potassium_kg_ha": 210.0, "organic_matter_pct": 1.20,
    },
    "italy_tuscany": {
        "display_name": "Italy — Tuscany / Central Italy (Luvisol hills, grapes-olive-cereals)",
        "texture": "loam",
        "ph": 7.20, "ec_ds_m": 0.45,
        "nitrogen_kg_ha": 65.0, "phosphorus_kg_ha": 40.0,
        "potassium_kg_ha": 220.0, "organic_matter_pct": 2.00,
    },
}

SPAIN_PRESETS: dict[str, dict] = {
    "spain_castile_leon": {
        "display_name": "Spain — Castile and León, Meseta Norte (Cambisol, dryland wheat-barley)",
        "texture": "loam",
        "ph": 7.80, "ec_ds_m": 0.45,
        "nitrogen_kg_ha": 52.0, "phosphorus_kg_ha": 30.0,
        "potassium_kg_ha": 195.0, "organic_matter_pct": 1.20,
    },
    "spain_andalusia": {
        "display_name": "Spain — Andalusia (Vertisol/Luvisol, olive-wheat-cotton-vegetables)",
        "texture": "clay_loam",
        "ph": 7.90, "ec_ds_m": 0.90,
        "nitrogen_kg_ha": 48.0, "phosphorus_kg_ha": 28.0,
        "potassium_kg_ha": 185.0, "organic_matter_pct": 0.80,
    },
    "spain_aragon": {
        "display_name": "Spain — Aragon / Ebro Valley (Fluvisol/Calcisol, irrigated maize-wheat)",
        "texture": "loam",
        "ph": 8.00, "ec_ds_m": 0.70,
        "nitrogen_kg_ha": 68.0, "phosphorus_kg_ha": 38.0,
        "potassium_kg_ha": 220.0, "organic_matter_pct": 1.50,
    },
}

# Master index — global regions organised by sub-continent/country
REGION_SOIL_PRESETS: dict[str, dict[str, dict]] = {
    "India — Punjab":           PUNJAB_SOIL_PRESETS,
    "India — UP / Bihar":       INDIA_UP_BIHAR_PRESETS,
    "India — Central":          INDIA_CENTRAL_PRESETS,
    "India — South":            INDIA_SOUTH_PRESETS,
    "Germany":                  GERMANY_SOIL_PRESETS,
    "France":                   FRANCE_PRESETS,
    "Poland":                   POLAND_PRESETS,
    "UK":                       UK_PRESETS,
    "Netherlands":              NETHERLANDS_PRESETS,
    "Italy":                    ITALY_PRESETS,
    "Spain":                    SPAIN_PRESETS,
    "East Asia":                EAST_ASIA_PRESETS,
    "Southeast Asia":           SOUTHEAST_ASIA_PRESETS,
    "Sub-Saharan / N. Africa":  AFRICA_PRESETS,
    "Latin America":            LATIN_AMERICA_PRESETS,
    "Europe (other)":           EUROPE_PRESETS,
    "North America":            NORTH_AMERICA_PRESETS,
    "Central Asia / Mid-East":  CENTRAL_ASIA_MIDEAST_PRESETS,
    "Australia":                AUSTRALIA_PRESETS,
}

# ---------------------------------------------------------------------------
# Region → major agricultural cities for the city selector UI
# ---------------------------------------------------------------------------
REGION_CITIES: dict[str, list[str]] = {
    # India
    "punjab_mansa":         ["Mansa", "Bathinda", "Faridkot", "Muktsar", "Barnala"],
    "punjab_ludhiana":      ["Ludhiana", "Jalandhar", "Amritsar", "Patiala", "Ferozepur"],
    "punjab_patiala":       ["Patiala", "Sangrur", "Fatehgarh Sahib", "Rupnagar"],
    "up_western":           ["Meerut", "Muzaffarnagar", "Saharanpur", "Agra", "Aligarh"],
    "up_eastern":           ["Varanasi", "Gorakhpur", "Allahabad", "Azamgarh"],
    "bihar_plains":         ["Patna", "Gaya", "Muzaffarpur", "Bhagalpur", "Darbhanga"],
    "maharashtra_vidarbha": ["Nagpur", "Amravati", "Wardha", "Yavatmal", "Akola"],
    "mp_malwa":             ["Indore", "Ujjain", "Dewas", "Ratlam", "Mandsaur"],
    "rajasthan_semi_arid":  ["Jaipur", "Jodhpur", "Bikaner", "Kota", "Ajmer"],
    "tamil_nadu_cauvery":   ["Trichy", "Thanjavur", "Madurai", "Coimbatore", "Salem"],
    "karnataka_deccan":     ["Bengaluru", "Mysuru", "Dharwad", "Belagavi", "Tumkur"],
    "gujarat_semi_arid":    ["Ahmedabad", "Surat", "Rajkot", "Vadodara", "Junagadh"],
    # Germany
    "germany_saxony_anhalt": ["Magdeburg", "Halle", "Bernburg", "Quedlinburg", "Merseburg", "Köthen"],
    "germany_bavaria":       ["Munich", "Augsburg", "Regensburg", "Würzburg", "Ingolstadt", "Straubing"],
    "germany_lower_saxony":  ["Hannover", "Braunschweig", "Göttingen", "Wolfenbüttel", "Hildesheim", "Celle"],
    "germany_nrw":           ["Cologne", "Düsseldorf", "Münster", "Bonn", "Aachen", "Kleve"],
    "germany_mecklenburg":   ["Rostock", "Schwerin", "Stralsund", "Greifswald", "Güstrow", "Neubrandenburg"],
    "germany_brandenburg":   ["Potsdam", "Frankfurt (Oder)", "Cottbus", "Eberswalde", "Müncheberg"],
    # France
    "france_paris_basin":   ["Paris", "Orléans", "Chartres", "Reims", "Troyes", "Rouen"],
    "france_brittany":      ["Rennes", "Caen", "Brest", "Saint-Brieuc", "Quimper", "Cherbourg"],
    "france_southwest":     ["Bordeaux", "Toulouse", "Agen", "Mont-de-Marsan", "Pau", "Auch"],
    # Poland
    "poland_greater_poland":["Poznań", "Gniezno", "Kalisz", "Konin", "Leszno", "Piła"],
    "poland_masovia":       ["Warsaw", "Łódź", "Radom", "Płock", "Siedlce", "Ciechanów"],
    "poland_pomerania":     ["Szczecin", "Koszalin", "Stargard", "Świnoujście", "Gryfino"],
    # UK
    "uk_east_anglia":       ["Norwich", "Cambridge", "Ipswich", "Ely", "Diss", "Kings Lynn"],
    "uk_east_midlands":     ["Lincoln", "Nottingham", "Leicester", "Spalding", "Grantham"],
    "uk_scotland":          ["Perth", "Dundee", "Forfar", "Cupar", "Kinross", "Aberdeen"],
    # Netherlands
    "netherlands_clay_polders": ["Amsterdam", "The Hague", "Hoorn", "Emmeloord", "Goes", "Middelburg"],
    "netherlands_sandy_east":   ["Nijmegen", "Arnhem", "Deventer", "Zwolle", "Tilburg", "Eindhoven"],
    # Italy
    "italy_po_valley":      ["Bologna", "Milan", "Ferrara", "Cremona", "Mantua", "Parma"],
    "italy_apulia":         ["Bari", "Foggia", "Lecce", "Taranto", "Brindisi", "Andria"],
    "italy_tuscany":        ["Florence", "Siena", "Arezzo", "Grosseto", "Perugia", "Ancona"],
    # Spain
    "spain_castile_leon":   ["Valladolid", "Salamanca", "Burgos", "León", "Zamora", "Palencia"],
    "spain_andalusia":      ["Seville", "Córdoba", "Granada", "Jaén", "Almería", "Huelva"],
    "spain_aragon":         ["Zaragoza", "Lleida", "Huesca", "Teruel", "Logroño", "Pamplona"],
    # East Asia
    "china_north_plain":    ["Beijing", "Tianjin", "Shijiazhuang", "Zhengzhou", "Jinan"],
    "china_yangtze":        ["Shanghai", "Nanjing", "Wuhan", "Hangzhou", "Hefei"],
    "vietnam_mekong":       ["Can Tho", "Long Xuyen", "Rach Gia", "Soc Trang", "Vinh Long"],
    "thailand_central":     ["Bangkok", "Ayutthaya", "Suphanburi", "Nakhon Sawan", "Chai Nat"],
    # Southeast Asia
    "indonesia_java":       ["Yogyakarta", "Surabaya", "Malang", "Solo", "Semarang"],
    "philippines_luzon":    ["Manila", "Cabanatuan", "Tarlac", "San Jose", "Munoz"],
    # Africa
    "sahel_zone":           ["Niamey", "Bamako", "Ouagadougou", "Zinder", "Maradi"],
    "ethiopia_highlands":   ["Addis Ababa", "Ambo", "Bishoftu", "Jimma", "Nazret"],
    "east_africa_highlands":["Nairobi", "Nakuru", "Kigali", "Kisumu", "Eldoret"],
    "south_africa_highveld":["Johannesburg", "Pretoria", "Bloemfontein", "Potchefstroom"],
    "nile_delta":           ["Cairo", "Alexandria", "Tanta", "Damanhur", "Mansoura"],
    # Latin America
    "argentina_pampas":     ["Buenos Aires", "Rosario", "Córdoba", "Santa Fe", "Pergamino"],
    "brazil_cerrado":       ["Brasília", "Goiânia", "Uberlândia", "Sorriso", "Sinop"],
    "mexico_central":       ["Mexico City", "Puebla", "Toluca", "Texcoco", "Celaya"],
    # Europe (other)
    "nw_europe":            ["London", "Paris", "Brussels", "Amsterdam", "Ghent"],
    "central_europe":       ["Berlin", "Warsaw", "Prague", "Vienna", "Dresden"],
    "mediterranean":        ["Rome", "Madrid", "Athens", "Valencia", "Thessaloniki"],
    # North America
    "us_corn_belt":         ["Des Moines", "Ames", "Champaign", "Peoria", "Columbus"],
    "us_great_plains":      ["Wichita", "Dodge City", "Amarillo", "Lubbock", "Lincoln"],
    "canada_prairies":      ["Saskatoon", "Regina", "Winnipeg", "Lethbridge", "Swift Current"],
    "california_valley":    ["Fresno", "Bakersfield", "Stockton", "Modesto", "Visalia"],
    # Central Asia / Mid-East
    "uzbekistan_ferghana":  ["Fergana", "Andijan", "Namangan", "Kokand", "Margilan"],
    "euphrates_basin":      ["Baghdad", "Mosul", "Aleppo", "Deir ez-Zor", "Fallujah"],
    "turkey_anatolia":      ["Ankara", "Konya", "Eskişehir", "Çorum", "Yozgat"],
    # Australia
    "aus_wheatbelt":        ["Perth", "Merredin", "Northam", "Geraldton", "Moora"],
    "aus_murray_darling":   ["Griffith", "Wagga Wagga", "Mildura", "Shepparton", "Dubbo"],
}

# Flat lookup: preset_key → preset dict (for fast server-side lookups)
REGION_PRESET_FLAT: dict[str, dict] = {
    k: v
    for group in REGION_SOIL_PRESETS.values()
    for k, v in group.items()
}
