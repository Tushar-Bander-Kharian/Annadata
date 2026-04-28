"""
Annadata Web Application — Flask backend.

Exposes a browser-based UI that replaces the terminal prompts while
keeping the existing simulation engine and LLM agents intact.

Run:
    python -m annadata.web.app
    # or:
    flask --app annadata.web.app run --debug
"""

from __future__ import annotations

import json
import asyncio
import threading
from typing import Any

from flask import Flask, render_template, request, jsonify, Response, stream_with_context

from annadata.data.varieties import (
    ALL_VARIETIES, list_varieties, get_variety, get_variety_names
)
from annadata.data.location_intel import (
    LOCATION_INTELLIGENCE, list_states,
    get_weed_hr_factor, get_disease_risk, get_insect_risk,
    get_soil_profile, get_water_profile,
)
from annadata.data.location_intel_eu import EU_LOCATION_INTELLIGENCE, get_eu_region_intel
from annadata.data.stress_responses import (
    DISEASE_MAX_PENALTY, WEED_MAX_PENALTY, INSECT_MAX_PENALTY
)
from annadata.config import CROP_DB, SOIL_TEXTURES, IRRIGATION_MM_PER_WEEK, REGION_SOIL_PRESETS, REGION_PRESET_FLAT, REGION_CITIES
# Alias to match new code expectations
CROPS = CROP_DB
IRRIGATION_METHODS = {k: {"weekly_mm": v} for k, v in IRRIGATION_MM_PER_WEEK.items()}
from annadata.models.inputs import CropVariety, SoilState, WaterQuality, StressOverrides
from annadata.engine.simulator import run_simulation
from annadata.climate.geocoder import geocode
from annadata.climate.fetcher import fetch_season_climate
from annadata.llm import LLMClient

app = Flask(__name__)

# ──────────────────────────────────────────────────────────────────────────────
#  PAGE ROUTES
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


# ──────────────────────────────────────────────────────────────────────────────
#  DATA API — seed the UI dropdowns
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/crops")
def api_crops():
    """Return all supported crops with base parameters."""
    return jsonify({
        crop_key: {
            "name": info["display_name"],
            "base_yield": info["base_yield_t_ha"],
            "season_days": info["growing_days"],
        }
        for crop_key, info in CROPS.items()
    })


@app.route("/api/varieties/<crop>")
def api_varieties(crop: str):
    """Return all varieties for a crop."""
    varieties = list_varieties(crop)
    return jsonify([
        {
            "key":   v.key,
            "name":  v.name,
            "release_year": v.release_year,
            "released_by": v.released_by,
            "yield_potential": v.yield_potential_t_ha,
            "season_days": v.season_days,
            "heat_modifier":        v.heat_stress_modifier,
            "drought_modifier":     v.drought_stress_modifier,
            "waterlogging_modifier":v.waterlogging_modifier,
            "salinity_modifier":    v.salinity_modifier,
            "cold_modifier":        v.cold_stress_modifier,
            "notified_states":      v.notified_states,
            "disease_resistance":   v.disease_resistance,
            "notes": v.notes,
        }
        for v in varieties
    ])


@app.route("/api/states")
def api_states():
    return jsonify(list_states())


@app.route("/api/location-intel/<state>/<crop>")
def api_location_intel(state: str, crop: str):
    """Return location intelligence for a state/region × crop combination."""
    intel = LOCATION_INTELLIGENCE.get(state) or get_eu_region_intel(state)
    if not intel:
        return jsonify({"error": "state not found"}), 404

    soil = intel.soil_fertility
    water = intel.irrigation_water

    weed_cases = [
        {
            "species":      w.weed_species,
            "resistant_to": w.resistant_to,
            "moa":          w.moa_class,
            "severity":     w.severity,
            "notes":        w.distribution,
        }
        for w in intel.weed_hr_cases if w.crop_system == crop
    ]

    diseases = [
        {
            "disease_key": d.disease_key,
            "risk_level":  d.risk_level,
            "season":      d.season,
            "notes":       d.notes,
        }
        for d in intel.disease_pressure if d.crop == crop
    ]

    insects = [
        {
            "pest":       i.pest_name,
            "risk_level": i.risk_level,
            "season":     i.season,
            "notes":      i.notes,
        }
        for i in intel.insect_pressure if i.crop == crop
    ]

    return jsonify({
        "state":     state,
        "crop":      crop,
        "region":    intel.region,
        "weed_hr":   weed_cases,
        "diseases":  diseases,
        "insects":   insects,
        "soil": {
            "ph_range":            list(soil.ph_range),
            "ec_range":            list(soil.ec_ds_m_range),
            "om_pct":              soil.organic_matter_pct,
            "nitrogen_status":     soil.nitrogen_status,
            "phosphorus_status":   soil.phosphorus_status,
            "potassium_status":    soil.potassium_status,
            "zinc_deficient_pct":  soil.zinc_deficient_pct,
            "boron_deficient_pct": soil.boron_deficient_pct,
            "sulphur_deficient_pct": soil.sulphur_deficient_pct,
            "soil_type":           soil.dominant_soil_type,
            "texture":             soil.dominant_texture,
            "notes":               soil.notes,
        },
        "water": {
            "typical_ec":       water.typical_ec_ds_m,
            "ec_range":         list(water.ec_range),
            "ph_range":         list(water.ph_range),
            "sar_range":        list(water.sar_range),
            "source":           water.primary_source,
            "quality_class":    water.quality_class,
            "contaminants":     water.common_contaminants,
            "fluoride_risk":    water.fluoride_risk,
            "arsenic_risk":     water.arsenic_risk,
            "nitrate_risk":     water.nitrate_risk,
            "notes":            water.notes,
        },
        "agronomic_notes": intel.agronomic_notes,
    })


@app.route("/api/soil-presets")
def api_soil_presets():
    """Return regional soil presets structured as {region: {key: preset}}."""
    out = {}
    for region, presets in REGION_SOIL_PRESETS.items():
        out[region] = {
            k: {"display_name": v["display_name"], **v}
            for k, v in presets.items()
        }
    return jsonify(out)


@app.route("/api/regions")
def api_regions():
    """Return globally grouped region list for the region selector."""
    groups = []
    for group_name, presets in REGION_SOIL_PRESETS.items():
        groups.append({
            "group": group_name,
            "options": [
                {"key": k, "label": v["display_name"]}
                for k, v in presets.items()
            ],
        })
    return jsonify(groups)


@app.route("/api/cities/<region_key>")
def api_cities(region_key: str):
    """Return list of major agricultural cities for a region key."""
    cities = REGION_CITIES.get(region_key, [])
    return jsonify(cities)


@app.route("/api/disease-list/<crop>")
def api_disease_list(crop: str):
    """Return disease keys relevant to a crop with max penalties."""
    crop_prefix = {
        "wheat":    ["wheat_", "fusarium_head_blight", "karnal_bunt",
                     "septoria_tritici_blotch", "fusarium_crown_rot", "pyrenophora_tritici"],
        "rice":     ["rice_"],
        "maize":    ["maize_"],
        "soybean":  ["soybean_", "charcoal_rot"],
        "chickpea": ["chickpea_"],
        "mustard":  ["alternaria_blight", "white_rust", "sclerotinia"],
        "tomato":   ["early_blight", "late_blight", "fusarium_wilt",
                     "bacterial_wilt", "tuta_absoluta"],
        "potato":   ["potato_", "late_blight", "early_blight",
                     "rhizoctonia_root_rot", "fusarium_dry_rot_potato", "nematode_potato"],
        "barley":   ["barley_", "ramularia_leaf_spot"],
        "rapeseed": ["phoma_stem_canker", "sclerotinia_rapeseed",
                     "rapeseed_light_leaf_spot", "clubroot"],
        "sugarbeet":["cercospora_leaf_spot", "beet_yellows_virus",
                     "rhizoctonia_root_rot"],
        "grapes":   ["grape_downy_mildew", "grape_powdery_mildew",
                     "xylella_fastidiosa"],
        "sunflower":["sclerotinia"],
    }
    prefixes = crop_prefix.get(crop, [])
    diseases = []
    for key, max_p in DISEASE_MAX_PENALTY.items():
        if key == "default":
            continue
        match = any(
            key.startswith(p) if p.endswith("_") else key == p
            for p in prefixes
        )
        if match:
            diseases.append({"key": key, "max_penalty_pct": round(max_p * 100)})
    return jsonify(sorted(diseases, key=lambda d: d["key"]))


# ──────────────────────────────────────────────────────────────────────────────
#  SIMULATION API
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """
    Run a full simulation.  Accepts JSON body, returns simulation results.

    Request body schema:
    {
        "crop":         "wheat",
        "variety_key":  "hd_3385",          # or null for generic
        "sowing_date":  "2024-11-15",
        "location":     "Ludhiana",
        "state":        "Punjab",

        # Soil (all optional — filled from state intel defaults if absent)
        "soil": {
            "texture": "loam",
            "ph": 7.8,
            "ec_ds_m": 0.4,
            "nitrogen_kg_ha": 80,
            "phosphorus_kg_ha": 35,
            "potassium_kg_ha": 180,
            "organic_matter_pct": 0.7
        },

        # Irrigation
        "water": {
            "ec_ds_m": 0.4,
            "ph": 7.5,
            "method": "tube-well"
        },

        # Stress overrides — sliders (0–1 each)
        "stress_overrides": {
            "heat":         0.0,    # extra heat beyond what weather shows
            "drought":      0.0,
            "waterlogging": 0.0,
            "salinity":     0.0,
            "cold":         0.0,
            "n_deficiency": 0.0,
            "p_deficiency": 0.0,
            "k_deficiency": 0.0,
            "zinc":         0.0,
            "weed":         0.5,    # 0 = none, 1 = uncontrolled
            "insect":       0.3,
            "disease_severities": {
                "wheat_yellow_rust": 0.4,
                "wheat_leaf_rust":   0.2
            }
        }
    }
    """
    body: dict[str, Any] = request.get_json(force=True)

    # ── 1. Geocode ───────────────────────────────────────────────────────────
    location_name = (body.get("location") or "").strip()
    if not location_name:
        return jsonify({"error": "Please enter a city or location name (e.g. 'Ludhiana', 'Iowa City')."}), 400
    try:
        result = asyncio.run(geocode(location_name))
        lat, lon = result[0], result[1]
    except Exception as exc:
        return jsonify({"error": f"Geocoding failed: {exc}"}), 400

    # ── 2. Build CropVariety ─────────────────────────────────────────────────
    crop_key = body.get("crop", "wheat")
    variety_key = body.get("variety_key")
    variety_profile = get_variety(crop_key, variety_key) if variety_key else None

    if variety_profile:
        cv = CropVariety(
            name=variety_profile.name,
            base_yield_t_ha=variety_profile.yield_potential_t_ha,
            season_days=variety_profile.season_days,
            optimal_temp_min=variety_profile.optimal_temp_min,
            optimal_temp_max=variety_profile.optimal_temp_max,
            critical_temp_high=variety_profile.critical_temp_high,
            critical_temp_low=variety_profile.critical_temp_low,
            heat_modifier=variety_profile.heat_stress_modifier,
            drought_modifier=variety_profile.drought_stress_modifier,
            waterlogging_modifier=variety_profile.waterlogging_modifier,
            salinity_modifier=variety_profile.salinity_modifier,
            cold_modifier=variety_profile.cold_stress_modifier,
            disease_resistance=variety_profile.disease_resistance,
        )
    else:
        # Fall back to crop defaults from config
        crop_info = CROPS.get(crop_key, CROPS["wheat"])
        cv = CropVariety(
            name=body.get("variety_label", "Generic"),
            base_yield_t_ha=crop_info["base_yield_t_ha"],
            season_days=crop_info["growing_days"],
            optimal_temp_min=crop_info["optimal_temp_min"],
            optimal_temp_max=crop_info["optimal_temp_max"],
            critical_temp_high=crop_info["critical_temp_high"],
            critical_temp_low=crop_info["critical_temp_low"],
        )

    # ── 3. Build SoilState ───────────────────────────────────────────────────
    soil_body = body.get("soil", {})
    state = body.get("state", "")
    soil_defaults = _soil_defaults_for_state(state)

    soil = SoilState(
        texture=soil_body.get("texture", soil_defaults["texture"]),
        ph=float(soil_body.get("ph", soil_defaults["ph"])),
        ec_ds_m=float(soil_body.get("ec_ds_m", soil_defaults["ec"])),
        nitrogen_kg_ha=float(soil_body.get("nitrogen_kg_ha",
                                            soil_defaults["n"])),
        phosphorus_kg_ha=float(soil_body.get("phosphorus_kg_ha",
                                              soil_defaults["p"])),
        potassium_kg_ha=float(soil_body.get("potassium_kg_ha",
                                             soil_defaults["k"])),
        organic_matter_pct=float(soil_body.get("organic_matter_pct",
                                                soil_defaults["om"])),
    )

    # ── 4. Build WaterQuality ────────────────────────────────────────────────
    water_body = body.get("water", {})
    water_defaults = _water_defaults_for_state(state)

    water = WaterQuality(
        ec_ds_m=float(water_body.get("ec_ds_m", water_defaults["ec"])),
        ph=float(water_body.get("ph", water_defaults["ph"])),
        irrigation_method=water_body.get("method", "tube-well"),
    )

    # ── 5. Build StressOverrides ─────────────────────────────────────────────
    so_body = body.get("stress_overrides", {})
    # Only use diseases explicitly set by the user via sliders.
    # Location intel risk levels are shown in the UI for reference and pre-fill
    # the disease sliders, but should NOT be silently injected into every run —
    # risk_level is epidemiological probability, not a confirmed season severity.
    merged_diseases = so_body.get("disease_severities", {})

    overrides = StressOverrides(
        heat=float(so_body.get("heat", 0.0)),
        drought=float(so_body.get("drought", 0.0)),
        waterlogging=float(so_body.get("waterlogging", 0.0)),
        salinity=float(so_body.get("salinity", 0.0)),
        cold=float(so_body.get("cold", 0.0)),
        n_deficiency=float(so_body.get("n_deficiency", 0.0)),
        p_deficiency=float(so_body.get("p_deficiency", 0.0)),
        k_deficiency=float(so_body.get("k_deficiency", 0.0)),
        zinc=float(so_body.get("zinc", 0.0)),
        weed=float(so_body.get("weed", 0.3)),
        insect=float(so_body.get("insect", 0.2)),
        disease_severities=merged_diseases,
        herbicide_resistance_factor=_weed_hr_factor(state, crop_key),
    )

    # ── 6. Fetch climate ─────────────────────────────────────────────────────
    sowing_date = body.get("sowing_date", "2024-11-01")
    try:
        from datetime import date
        sowing_date_obj = date.fromisoformat(sowing_date)
        climate = asyncio.run(fetch_season_climate(
            lat, lon, location_name, sowing_date_obj, cv.season_days))
    except Exception as exc:
        return jsonify({"error": f"Climate fetch failed: {exc}"}), 500

    # ── 7. Run simulation ────────────────────────────────────────────────────
    fertiliser_events = body.get("fertiliser", [])
    som_quality = body.get("som_quality", "typical")
    result = run_simulation(crop_key, cv, soil, water, climate, overrides,
                            fertiliser_events, som_quality=som_quality)

    # ── 8. Build weekly data for charts ─────────────────────────────────────
    weekly_rows = []
    climate_weeks = {w.week_index: w for w in climate.weeks} if hasattr(climate, "weeks") else {}
    for ws in result.weekly_stress:
        cw = climate_weeks.get(ws.week - 1)
        weekly_rows.append({
            "week":         ws.week,
            "stage":        ws.stage,
            "combined":     round(ws.combined, 3),
            "temperature":  round(ws.temperature_factor, 3),
            "water":        round(ws.water_factor, 3),
            "salinity":     round(ws.salinity_factor, 3),
            "ph":           round(ws.ph_factor, 3),
            "nutrient":     round(ws.nutrient_factor, 3),
            "radiation":    round(ws.radiation_factor, 3),
            "biotic":       round(getattr(ws, "biotic_factor", 1.0), 3),
            "temp_mean":    round(cw.temp_mean, 1) if cw else 0.0,
            "precip_mm":    round(cw.precipitation_mm, 1) if cw else 0.0,
        })

    # ── 9. Limiting factor analysis ─────────────────────────────────────────
    avg_factors = _average_factors(result.weekly_stress)
    ranked = sorted(avg_factors.items(), key=lambda x: x[1])  # lowest first

    return jsonify({
        "simulated_yield":   round(result.simulated_yield_t_ha, 2),
        "potential_yield":   round(result.potential_yield_t_ha, 2),
        "yield_gap_pct":     round(result.yield_gap_pct, 1),
        "variety":           cv.name,
        "crop":              crop_key,
        "location":          location_name,
        "state":             state,
        "sowing_date":       sowing_date,
        "season_weeks":      len(weekly_rows),
        "weekly":            weekly_rows,
        "weekly_soil":       result.weekly_soil,
        "limiting_factors":  ranked,
        "alerts":            result.alerts,
        "lat":               round(lat, 4),
        "lon":               round(lon, 4),
    })


# ──────────────────────────────────────────────────────────────────────────────
#  MULTI-RUN (MONTE CARLO) SIMULATION API
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/simulate-multi", methods=["POST"])
def api_simulate_multi():
    """
    Run N perturbed simulations (Monte Carlo sensitivity analysis).

    Extra body fields (on top of regular simulate payload):
      n_runs       int   — number of runs (10–200, default 50)
      temp_sd      float — SD of weekly temperature perturbation (°C, default 1.5)
      precip_cv    float — coefficient of variation for precipitation (0–1, default 0.20)
      n_fert_sd    float — SD of total season N fertiliser (kg/ha, default 15)
      pest_random  bool  — randomise weed/insect/disease by ±50 % (default True)

    Returns yield distribution statistics + top sensitivity factors.
    """
    import random, statistics

    body: dict = request.get_json(force=True)
    n_runs     = max(5, min(500, int(body.get("n_runs",     50))))
    temp_sd    = float(body.get("temp_sd",    1.5))
    precip_cv  = float(body.get("precip_cv",  0.20))
    n_fert_sd  = float(body.get("n_fert_sd",  15.0))
    pest_random= bool(body.get("pest_random", True))

    # Re-use all the setup logic from the single-run endpoint ─────────────────
    location_name = (body.get("location") or "").strip()
    if not location_name:
        return jsonify({"error": "Location required"}), 400

    try:
        result = asyncio.run(geocode(location_name))
        lat, lon = result[0], result[1]
    except Exception as exc:
        return jsonify({"error": f"Geocoding failed: {exc}"}), 400

    crop_key     = body.get("crop", "wheat")
    crop_info    = CROPS.get(crop_key, CROPS["wheat"])
    variety_key  = body.get("variety_key")
    variety_profile = get_variety(crop_key, variety_key) if variety_key else None

    if variety_profile:
        cv = CropVariety(
            name=variety_profile.name,
            base_yield_t_ha=variety_profile.yield_potential_t_ha,
            season_days=variety_profile.season_days,
            optimal_temp_min=variety_profile.optimal_temp_min,
            optimal_temp_max=variety_profile.optimal_temp_max,
            critical_temp_high=variety_profile.critical_temp_high,
            critical_temp_low=variety_profile.critical_temp_low,
            heat_modifier=variety_profile.heat_stress_modifier,
            drought_modifier=variety_profile.drought_stress_modifier,
            waterlogging_modifier=variety_profile.waterlogging_modifier,
            salinity_modifier=variety_profile.salinity_modifier,
            cold_modifier=variety_profile.cold_stress_modifier,
            disease_resistance=variety_profile.disease_resistance,
        )
    else:
        cv = CropVariety(
            name=body.get("variety_label", "Generic"),
            base_yield_t_ha=crop_info["base_yield_t_ha"],
            season_days=crop_info["growing_days"],
            optimal_temp_min=crop_info["optimal_temp_min"],
            optimal_temp_max=crop_info["optimal_temp_max"],
            critical_temp_high=crop_info["critical_temp_high"],
            critical_temp_low=crop_info["critical_temp_low"],
        )

    state = body.get("state", "")
    soil_body = body.get("soil", {})
    soil_defaults = _soil_defaults_for_state(state)
    base_soil = SoilState(
        texture=soil_body.get("texture", soil_defaults["texture"]),
        ph=float(soil_body.get("ph", soil_defaults["ph"])),
        ec_ds_m=float(soil_body.get("ec_ds_m", soil_defaults["ec"])),
        nitrogen_kg_ha=float(soil_body.get("nitrogen_kg_ha", soil_defaults["n"])),
        phosphorus_kg_ha=float(soil_body.get("phosphorus_kg_ha", soil_defaults["p"])),
        potassium_kg_ha=float(soil_body.get("potassium_kg_ha", soil_defaults["k"])),
        organic_matter_pct=float(soil_body.get("organic_matter_pct", soil_defaults["om"])),
    )

    water_body = body.get("water", {})
    water_defaults = _water_defaults_for_state(state)
    water = WaterQuality(
        ec_ds_m=float(water_body.get("ec_ds_m", water_defaults["ec"])),
        ph=float(water_body.get("ph", water_defaults["ph"])),
        irrigation_method=water_body.get("method", "tube-well"),
    )

    so_body = body.get("stress_overrides", {})
    base_diseases = so_body.get("disease_severities", {})
    base_weed   = float(so_body.get("weed",   0.3))
    base_insect = float(so_body.get("insect", 0.2))

    sowing_date = body.get("sowing_date", "2024-11-01")
    try:
        from datetime import date as _date
        sowing_date_obj = _date.fromisoformat(sowing_date)
        base_climate = asyncio.run(fetch_season_climate(
            lat, lon, location_name, sowing_date_obj, cv.season_days))
    except Exception as exc:
        return jsonify({"error": f"Climate fetch failed: {exc}"}), 500

    fertiliser_events = body.get("fertiliser", [])
    som_quality = body.get("som_quality", "typical")

    # ── Monte Carlo runs ──────────────────────────────────────────────────────
    yields, factor_sums = [], {k: 0.0 for k in
        ["temperature_factor","water_factor","salinity_factor",
         "ph_factor","nutrient_factor","radiation_factor"]}

    rng = random.Random()
    for _ in range(n_runs):
        # Perturb climate: add Gaussian noise to temperature, lognormal to precip
        from dataclasses import replace as dc_replace
        perturbed_weeks = []
        for wk in base_climate.weeks:
            dt = rng.gauss(0, temp_sd)
            dp = rng.lognormvariate(0, precip_cv) if wk.precipitation_mm > 0 else 1.0
            perturbed_weeks.append(dc_replace(
                wk,
                temp_mean=wk.temp_mean + dt,
                temp_max_avg=wk.temp_max_avg + dt,
                temp_min_avg=wk.temp_min_avg + dt,
                precipitation_mm=max(0.0, wk.precipitation_mm * dp),
                et0_mm=max(0.0, wk.et0_mm * (1 + dt * 0.03)),
            ))
        from dataclasses import replace as _dcr
        climate_p = _dcr(base_climate, weeks=perturbed_weeks)

        # Perturb soil N
        n_mult = max(0.4, 1.0 + rng.gauss(0, n_fert_sd) / max(base_soil.nitrogen_kg_ha, 1))
        soil_p = SoilState(
            texture=base_soil.texture,
            ph=base_soil.ph,
            ec_ds_m=base_soil.ec_ds_m,
            nitrogen_kg_ha=base_soil.nitrogen_kg_ha * n_mult,
            phosphorus_kg_ha=base_soil.phosphorus_kg_ha,
            potassium_kg_ha=base_soil.potassium_kg_ha,
            organic_matter_pct=base_soil.organic_matter_pct,
        )

        # Perturb pest pressure
        if pest_random:
            weed_p   = _clamp(base_weed   * rng.uniform(0.5, 1.5))
            insect_p = _clamp(base_insect * rng.uniform(0.5, 1.5))
            dis_p    = {k: _clamp(v * rng.uniform(0.6, 1.4))
                        for k, v in base_diseases.items()}
        else:
            weed_p, insect_p, dis_p = base_weed, base_insect, base_diseases

        overrides_p = StressOverrides(
            heat=float(so_body.get("heat", 0.0)),
            drought=float(so_body.get("drought", 0.0)),
            waterlogging=float(so_body.get("waterlogging", 0.0)),
            salinity=float(so_body.get("salinity", 0.0)),
            cold=float(so_body.get("cold", 0.0)),
            n_deficiency=float(so_body.get("n_deficiency", 0.0)),
            p_deficiency=float(so_body.get("p_deficiency", 0.0)),
            k_deficiency=float(so_body.get("k_deficiency", 0.0)),
            zinc=float(so_body.get("zinc", 0.0)),
            weed=weed_p, insect=insect_p,
            disease_severities=dis_p,
            herbicide_resistance_factor=_weed_hr_factor(state, crop_key),
        )

        res = run_simulation(crop_key, cv, soil_p, water, climate_p,
                             overrides_p, fertiliser_events, som_quality=som_quality)
        yields.append(round(res.simulated_yield_t_ha, 3))
        for ws in res.weekly_stress:
            for k in factor_sums:
                factor_sums[k] += getattr(ws, k, 1.0)

    yields.sort()
    n = len(yields)
    factor_avgs = {k: round(v / (n * len(base_climate.weeks)), 3)
                   for k, v in factor_sums.items()}
    sensitivity = sorted(factor_avgs.items(), key=lambda x: x[1])  # lowest = most limiting

    def pct(p): return yields[min(n-1, max(0, int(n*p/100)))]

    return jsonify({
        "n_runs":       n_runs,
        "potential_yield": round(cv.base_yield_t_ha, 2),
        "mean":         round(statistics.mean(yields), 2),
        "median":       round(statistics.median(yields), 2),
        "stdev":        round(statistics.stdev(yields) if n > 1 else 0, 2),
        "min":          round(yields[0], 2),
        "max":          round(yields[-1], 2),
        "p10":          round(pct(10),  2),
        "p25":          round(pct(25),  2),
        "p75":          round(pct(75),  2),
        "p90":          round(pct(90),  2),
        "yields":       yields,
        "factor_sensitivity": [{"factor": k, "avg": v} for k, v in sensitivity],
        "params": {"temp_sd": temp_sd, "precip_cv": precip_cv,
                   "n_fert_sd": n_fert_sd, "pest_random": pest_random},
    })


# ──────────────────────────────────────────────────────────────────────────────
#  LLM REPORT API
# ──────────────────────────────────────────────────────────────────────────────

@app.route("/api/llm-report", methods=["POST"])
def api_llm_report():
    body = request.get_json(force=True)
    sim     = body.get("simulation_summary", {})
    backend = body.get("backend", "ollama")
    model   = body.get("model") or None

    import os
    os.environ["ANNADATA_BACKEND"] = backend
    if model:
        os.environ["ANNADATA_MODEL"] = model

    from annadata.config import REPORT_MODEL
    from annadata.llm import LLMClient

    loc_str = sim.get('location','?')
    state_str = sim.get('state','?')
    eu_state = state_str.startswith("germany_") or state_str.startswith("france_") or \
               state_str.startswith("poland_") or state_str.startswith("uk_") or \
               state_str.startswith("netherlands_") or state_str.startswith("italy_") or \
               state_str.startswith("spain_")
    region_context = "European" if eu_state else "Indian"

    prompt = f"""You are an experienced {region_context} agronomist writing an end-of-season advisory report.

SIMULATION RESULTS:
  Crop:            {sim.get('crop','?')}
  Variety:         {sim.get('variety','?')}
  Location:        {loc_str} ({state_str})
  Sowing date:     {sim.get('sowing_date','?')}
  Simulated yield: {sim.get('simulated_yield','?')} t/ha
  Potential yield: {sim.get('potential_yield','?')} t/ha
  Yield gap:       {sim.get('yield_gap_pct','?')}%

TOP LIMITING FACTORS:
{chr(10).join(f"  {n}: {v}" for n,v in (sim.get('limiting_factors') or []))}

AGRONOMIC ALERTS:
{chr(10).join(f"  - {a}" for a in (sim.get('alerts') or ['None']))}

Write a structured advisory with:
1. SEASON SUMMARY
2. PRIMARY CONSTRAINTS
3. FIELD OBSERVATIONS
4. RECOMMENDATIONS FOR NEXT SEASON (4 specific actions)

Be practical and specific to {region_context} farming conditions."""

    def generate():
        try:
            from annadata.llm import create_client
            client = create_client()
            import asyncio
            async def get_text():
                resp = await client.generate(
                    model=REPORT_MODEL,
                    system=f"You are a senior agronomist with 20 years experience in {region_context} agriculture.",
                    prompt=prompt,
                    max_tokens=600,
                )
                return resp.text
            text = asyncio.run(get_text())
            for i, word in enumerate(text.split(" ")):
                chunk = word + (" " if i < len(text.split(" "))-1 else "")
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return Response(stream_with_context(generate()),
                    mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})


# ──────────────────────────────────────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def _parse_texture(dominant_texture: str) -> str:
    """Map a free-form dominant-texture description to a SoilColumn preset key."""
    t = dominant_texture.lower()
    if "sandy loam" in t:
        return "sandy_loam"
    if "clay loam" in t:
        return "clay_loam"
    if "clay" in t:
        return "clay"
    if "silty" in t or "silt" in t:
        return "silty"
    if "sandy" in t:
        return "sandy"
    if "loam" in t:
        return "loam"
    return "loam"


def _soil_defaults_for_state(state: str) -> dict:
    # 1. Try India location_intel (state name or preset key like "punjab_ludhiana")
    profile = get_soil_profile(state)
    if profile:
        ph_mid = (profile.ph_range[0] + profile.ph_range[1]) / 2
        ec_mid = (profile.ec_ds_m_range[0] + profile.ec_ds_m_range[1]) / 2
        n_map = {"low": 60, "low-medium": 75, "medium": 100,
                  "medium-high": 130, "high": 160}
        p_map = {"low": 20, "low-medium": 30, "medium": 45, "high": 70}
        k_map = {"low": 130, "low-medium": 180, "medium": 250,
                  "medium-high": 320, "high": 400}
        return {
            "texture": _parse_texture(profile.dominant_texture),
            "ph": round(ph_mid, 1),
            "ec": round(ec_mid, 2),
            "n": n_map.get(profile.nitrogen_status, 90),
            "p": p_map.get(profile.phosphorus_status, 30),
            "k": k_map.get(profile.potassium_status, 200),
            "om": profile.organic_matter_pct,
        }
    # 2. Try global preset flat lookup (key like "us_corn_belt", "nile_delta")
    preset = REGION_PRESET_FLAT.get(state)
    if preset:
        return {
            "texture": _parse_texture(preset.get("texture", "loam")),
            "ph":  preset.get("ph",  7.5),
            "ec":  preset.get("ec_ds_m", 0.4),
            "n":   preset.get("nitrogen_kg_ha",   90.0),
            "p":   preset.get("phosphorus_kg_ha", 30.0),
            "k":   preset.get("potassium_kg_ha",  200.0),
            "om":  preset.get("organic_matter_pct", 0.6),
        }
    return {"texture": "loam", "ph": 7.5, "ec": 0.4,
            "n": 90, "p": 30, "k": 200, "om": 0.6}


def _water_defaults_for_state(state: str) -> dict:
    profile = get_water_profile(state)
    if profile:
        ph_mid = (profile.ph_range[0] + profile.ph_range[1]) / 2
        return {"ec": profile.typical_ec_ds_m, "ph": round(ph_mid, 1)}
    # Try EU intel
    eu = get_eu_region_intel(state)
    if eu:
        w = eu.irrigation_water
        ph_mid = (w.ph_range[0] + w.ph_range[1]) / 2
        return {"ec": w.typical_ec_ds_m, "ph": round(ph_mid, 1)}
    return {"ec": 0.4, "ph": 7.5}


def _weed_hr_factor(state: str, crop: str) -> float:
    """HR factor — checks India intel then EU intel."""
    factor = get_weed_hr_factor(state, crop)
    if factor > 0:
        return factor
    eu = get_eu_region_intel(state)
    if eu:
        relevant = [c.severity for c in eu.weed_hr_cases if c.crop_system == crop]
        return max(relevant, default=0.0)
    return 0.0


def _average_factors(weekly_stresses) -> dict[str, float]:
    if not weekly_stresses:
        return {}
    keys = ["temperature_factor", "water_factor", "salinity_factor",
            "ph_factor", "nutrient_factor", "radiation_factor", "biotic_factor"]
    totals = {k: 0.0 for k in keys}
    for ws in weekly_stresses:
        for k in keys:
            totals[k] += getattr(ws, k, 1.0)
    n = len(weekly_stresses)
    labels = {
        "temperature_factor": "Temperature",
        "water_factor":       "Water / Drought",
        "salinity_factor":    "Salinity",
        "ph_factor":          "Soil pH",
        "nutrient_factor":    "Nutrients (N/P/K)",
        "radiation_factor":   "Solar Radiation",
        "biotic_factor":      "Biotic Stresses",
    }
    return {labels[k]: round(v / n, 3) for k, v in totals.items()}


# ──────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=False, port=5000, use_reloader=False)
