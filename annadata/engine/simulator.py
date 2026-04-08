"""Week-by-week deterministic crop yield simulator — Annadata v2."""
from __future__ import annotations
from typing import Optional

from annadata.config import CROP_DB, SOIL_TEXTURES, IRRIGATION_MM_PER_WEEK, STAGE_WEIGHTS
from annadata.engine.stress import (
    temperature_factor, water_stress_factor, salinity_factor,
    soil_ph_factor, nutrient_factor, radiation_factor,
)
from annadata.models.inputs import CropVariety, SoilState, WaterQuality, StressOverrides
from annadata.models.state import WeeklyStress, SimulationResult
from annadata.data.stress_responses import (
    drought_penalty, heat_penalty, waterlogging_penalty, salinity_penalty,
    cold_stress_penalty, nitrogen_penalty, phosphorus_penalty,
    potassium_penalty, zinc_penalty, disease_penalty, weed_penalty,
    insect_penalty, environment_disease_modifier,
)


def _clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def _stage(week, total):
    f = week / total
    if f < 0.10: return "germination"
    elif f < 0.50: return "vegetative"
    elif f < 0.80: return "reproductive"
    else: return "maturity"

def _rh(wk):
    rh = 60.0 + min(25.0, wk.precipitation_mm * 0.3) - max(0.0, (wk.temp_mean - 25.0) * 0.8)
    return max(30.0, min(95.0, rh))


def run_simulation(crop_key, variety, soil, water, climate, overrides=None):
    if overrides is None:
        overrides = StressOverrides()

    crop_info   = CROP_DB.get(crop_key, CROP_DB["wheat"])
    total_weeks = len(climate.weeks)
    pot_yield   = variety.base_yield_t_ha

    consec_heat = 0
    heat_pen_applied = False
    weekly_stresses = []
    acc_y = acc_w = 0.0
    alerts = []
    all_temps = []
    all_rain  = []

    for i, wk in enumerate(climate.weeks, start=1):
        stage  = _stage(i, total_weeks)
        sw     = STAGE_WEIGHTS.get(stage, 0.1)
        kc     = crop_info["kc"].get(stage, 1.0)

        all_temps.append(wk.temp_mean)
        all_rain.append(wk.precipitation_mm)

        # ── original 6 factors ──────────────────────────────────────────────
        t_f = temperature_factor(
            temp_mean=wk.temp_mean,
            t_base=variety.critical_temp_low,
            t_opt1=variety.optimal_temp_min,
            t_opt2=variety.optimal_temp_max,
            t_max=variety.critical_temp_high,
        )
        w_f = water_stress_factor(
            precip_mm=wk.precipitation_mm,
            et0_mm=wk.et0_mm,
            kc=kc,
            irrigation_method=water.irrigation_method,
            soil_texture=soil.texture,
        )
        s_f = salinity_factor(
            irrigation_ec_ds_m=water.ec_ds_m,
            ec_threshold=crop_info["ec_threshold_ds_m"],
            ec_slope_pct_per_ds_m=crop_info["ec_slope_pct_per_ds_m"],
        )
        ph_f = soil_ph_factor(
            ph=soil.ph,
            optimal_min=crop_info["optimal_ph_min"],
            optimal_max=crop_info["optimal_ph_max"],
        )
        n_f = nutrient_factor(
            n_kg_ha=soil.nitrogen_kg_ha,
            p_kg_ha=soil.phosphorus_kg_ha,
            k_kg_ha=soil.potassium_kg_ha,
            organic_matter_pct=soil.organic_matter_pct,
            base_yield_t_ha=pot_yield,
            n_demand_kg_per_t=crop_info["n_demand_kg_per_t"],
            p_demand_kg_per_t=crop_info["p_demand_kg_per_t"],
            k_demand_kg_per_t=crop_info["k_demand_kg_per_t"],
        )
        rad_f = radiation_factor(solar_mj_m2=wk.solar_radiation_mj_m2)

        # ── abiotic overrides ────────────────────────────────────────────────
        if overrides.heat > 0:
            t_f = _clamp(t_f * heat_penalty(crop_key, overrides.heat, variety.heat_modifier))
        if overrides.drought > 0:
            w_f = _clamp(w_f * drought_penalty(crop_key, overrides.drought, variety.drought_modifier))
        if overrides.waterlogging > 0:
            w_f = _clamp(w_f * waterlogging_penalty(crop_key, overrides.waterlogging, variety.waterlogging_modifier))
        if overrides.salinity > 0:
            s_f = _clamp(s_f * salinity_penalty(crop_key, overrides.salinity, variety.salinity_modifier))
        if overrides.cold > 0:
            t_f = _clamp(t_f * cold_stress_penalty(crop_key, overrides.cold, variety.cold_modifier))

        np2 = []
        if overrides.n_deficiency > 0: np2.append(nitrogen_penalty(crop_key, overrides.n_deficiency, variety.nue_modifier))
        if overrides.p_deficiency > 0: np2.append(phosphorus_penalty(crop_key, overrides.p_deficiency))
        if overrides.k_deficiency > 0: np2.append(potassium_penalty(crop_key, overrides.k_deficiency))
        if overrides.zinc > 0:         np2.append(zinc_penalty(crop_key, overrides.zinc))
        if np2: n_f = _clamp(n_f * min(np2))

        # ── biotic ───────────────────────────────────────────────────────────
        bio = 1.0
        for dk, bsev in overrides.disease_severities.items():
            env = environment_disease_modifier(dk, wk.temp_mean, _rh(wk))
            eff = _clamp(bsev * env)
            res = variety.disease_resistance.get(dk, 1.0)
            bio *= disease_penalty(dk, eff, res)
        bio *= weed_penalty(crop_key, overrides.weed, overrides.herbicide_resistance_factor)
        bio *= insect_penalty(crop_key, overrides.insect)
        bio  = _clamp(bio)

        # Multiply biotic into combined
        combined = _clamp(t_f * w_f * s_f * ph_f * n_f * rad_f * bio)

        # ── heat sterility ───────────────────────────────────────────────────
        if wk.temp_max_avg > variety.critical_temp_high and stage == "reproductive":
            consec_heat += 1
        else:
            consec_heat = 0
        if consec_heat >= 3 and not heat_pen_applied and stage == "reproductive":
            heat_pen_applied = True
            combined *= 0.80
            alerts.append(f"Week {i}: 3+ consecutive hot weeks in reproductive stage → 20% sterility penalty.")

        acc_y += combined * sw
        acc_w += sw

        if combined < 0.40:
            alerts.append(f"Week {i} [{stage}]: Combined factor {combined:.2f} — SEVERELY STRESSED.")
        if wk.temp_max_avg > variety.critical_temp_high:
            alerts.append(f"Week {i}: Tmax {wk.temp_max_avg:.1f}°C > critical {variety.critical_temp_high}°C.")
        if overrides.weed > 0.7 and i <= 4:
            alerts.append(f"Week {i}: Very high weed pressure in early season — critical control window.")

        # Use exact WeeklyStress field names from state.py
        weekly_stresses.append(WeeklyStress(
            week=i,
            stage=stage,
            temperature_factor=t_f,
            water_factor=w_f,
            salinity_factor=s_f,
            ph_factor=ph_f,
            nutrient_factor=n_f,
            radiation_factor=rad_f,
            combined=combined,
        ))

    mean_f    = acc_y / acc_w if acc_w else 0.0
    simulated = pot_yield * mean_f
    gap       = ((pot_yield - simulated) / pot_yield) * 100.0
    mean_temp = sum(all_temps) / len(all_temps) if all_temps else 0.0
    total_rain= sum(all_rain)

    # Identify dominant stresses
    factor_avgs = {}
    for label, attr in [
        ("Temperature stress", "temperature_factor"),
        ("Water stress",       "water_factor"),
        ("Salinity stress",    "salinity_factor"),
        ("Soil pH stress",     "ph_factor"),
        ("Nutrient deficiency","nutrient_factor"),
        ("Low solar radiation","radiation_factor"),
    ]:
        vals = [getattr(ws, attr) for ws in weekly_stresses]
        factor_avgs[label] = sum(vals) / len(vals) if vals else 1.0
    dominant = [k for k, _ in sorted(factor_avgs.items(), key=lambda x: x[1])[:3]]

    return SimulationResult(
        crop_name=crop_key,
        variety_label=variety.name,
        location=getattr(climate, 'location', ''),
        sowing_date=str(getattr(climate, 'sowing_date', '')),
        harvest_date=str(getattr(climate, 'harvest_date', '')),
        potential_yield_t_ha=pot_yield,
        simulated_yield_t_ha=simulated,
        yield_gap_pct=gap,
        season_weeks=total_weeks,
        mean_temp_c=round(mean_temp, 1),
        total_rain_mm=round(total_rain, 1),
        weekly_stress=weekly_stresses,
        stage_reports={},
        final_report="",
        dominant_stresses=dominant,
        alerts=alerts,
    )
