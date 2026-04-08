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
from annadata.data.stress_responses import (
    DISEASE_MAX_PENALTY, WEED_MAX_PENALTY, INSECT_MAX_PENALTY
)
from annadata.config import CROP_DB, SOIL_TEXTURES, IRRIGATION_MM_PER_WEEK, REGION_SOIL_PRESETS
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
    """Return location intelligence for a state × crop combination."""
    intel = LOCATION_INTELLIGENCE.get(state)
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
    """Return regional soil presets structured as {state: {key: preset}}."""
    out = {}
    for region, presets in REGION_SOIL_PRESETS.items():
        out[region] = {
            k: {"display_name": v["display_name"], **v}
            for k, v in presets.items()
        }
    return jsonify(out)


@app.route("/api/disease-list/<crop>")
def api_disease_list(crop: str):
    """Return disease keys relevant to a crop with max penalties."""
    crop_prefix = {
        "wheat":    ["wheat_", "fusarium_head_blight", "karnal_bunt"],
        "rice":     ["rice_"],
        "maize":    ["maize_"],
        "soybean":  ["soybean_", "charcoal_rot"],
        "chickpea": ["chickpea_"],
        "mustard":  ["alternaria_blight", "white_rust", "sclerotinia"],
        "tomato":   ["early_blight", "late_blight", "fusarium_wilt",
                     "bacterial_wilt"],
        "potato":   ["late_blight", "early_blight", "potato_virus_y"],
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
    location_name = body.get("location", "New Delhi")
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
    # Location-aware: bump disease severities from state intel if not provided
    location_diseases = get_disease_risk(state, crop_key) if state else {}
    manual_diseases = so_body.get("disease_severities", {})
    # manual overrides win; location data fills gaps
    merged_diseases = {**location_diseases, **manual_diseases}

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
        herbicide_resistance_factor=get_weed_hr_factor(state, crop_key),
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
    result = run_simulation(crop_key, cv, soil, water, climate, overrides)

    # ── 8. Build weekly data for charts ─────────────────────────────────────
    weekly_rows = []
    for ws in result.weekly_stress:
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
            "biotic":       1.0,
            "temp_mean":    0.0,
            "precip_mm":    0.0,
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
        "limiting_factors":  ranked,
        "alerts":            result.alerts,
        "lat":               round(lat, 4),
        "lon":               round(lon, 4),
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

    prompt = f"""You are an experienced Indian agronomist writing an end-of-season advisory report.

SIMULATION RESULTS:
  Crop:            {sim.get('crop','?')}
  Variety:         {sim.get('variety','?')}
  Location:        {sim.get('location','?')} ({sim.get('state','?')})
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

Be practical and specific to Indian farming conditions."""

    def generate():
        try:
            from annadata.llm import create_client
            client = create_client()
            import asyncio
            async def get_text():
                resp = await client.generate(
                    model=REPORT_MODEL,
                    system="You are a senior agronomist with 20 years experience in Indian agriculture.",
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

def _soil_defaults_for_state(state: str) -> dict:
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
            "texture": profile.dominant_texture.split()[0].lower(),
            "ph": round(ph_mid, 1),
            "ec": round(ec_mid, 2),
            "n": n_map.get(profile.nitrogen_status, 90),
            "p": p_map.get(profile.phosphorus_status, 30),
            "k": k_map.get(profile.potassium_status, 200),
            "om": profile.organic_matter_pct,
        }
    return {"texture": "loam", "ph": 7.5, "ec": 0.4,
            "n": 90, "p": 30, "k": 200, "om": 0.6}


def _water_defaults_for_state(state: str) -> dict:
    profile = get_water_profile(state)
    if profile:
        ph_mid = (profile.ph_range[0] + profile.ph_range[1]) / 2
        return {"ec": profile.typical_ec_ds_m, "ph": round(ph_mid, 1)}
    return {"ec": 0.4, "ph": 7.5}


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
