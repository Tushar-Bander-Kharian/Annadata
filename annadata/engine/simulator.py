"""Week-by-week crop simulation engine."""
from __future__ import annotations

from annadata.config import STAGE_BOUNDARIES, STAGE_WEIGHTS
from annadata.engine.stress import (
    identify_dominant_stresses,
    nutrient_factor,
    radiation_factor,
    salinity_factor,
    soil_ph_factor,
    temperature_factor,
    water_stress_factor,
)
from annadata.models.climate import SeasonClimate
from annadata.models.inputs import CropVariety, SoilState, WaterQuality
from annadata.models.state import SimulationResult, WeeklyStress


def _get_stage(progress: float) -> str:
    for stage, (lo, hi) in STAGE_BOUNDARIES.items():
        if lo <= progress < hi:
            return stage
    return "maturity"


def _get_kc(crop: CropVariety, stage: str, stage_progress: float) -> float:
    """Interpolate Kc within a stage for smoother transition."""
    stages = list(STAGE_BOUNDARIES.keys())
    idx = stages.index(stage)
    kc_now = crop.kc[stage]
    if idx < len(stages) - 1:
        kc_next = crop.kc[stages[idx + 1]]
        return kc_now + (kc_next - kc_now) * stage_progress
    return kc_now


def run_simulation(
    crop: CropVariety,
    soil: SoilState,
    water: WaterQuality,
    season: SeasonClimate,
    stage_reports: dict[str, str],  # filled in by agents during the async loop
) -> SimulationResult:
    """
    Pure deterministic simulation pass. Stage reports are injected externally
    (filled by LLM agents in main.py between stage transitions).
    Returns a complete SimulationResult.
    """
    total_weeks = len(season.weeks)
    if total_weeks == 0:
        raise ValueError("Season has no climate data.")

    # Pre-compute static nutrient factor (doesn't change week to week)
    f_nutr = nutrient_factor(
        soil.nitrogen_kg_ha, soil.phosphorus_kg_ha, soil.potassium_kg_ha,
        soil.organic_matter_pct, crop.base_yield_t_ha,
        crop.n_demand_kg_per_t, crop.p_demand_kg_per_t, crop.k_demand_kg_per_t,
    )
    f_ph = soil_ph_factor(soil.ph, crop.optimal_ph_min, crop.optimal_ph_max)
    f_salt = salinity_factor(water.ec_ds_m, crop.ec_threshold_ds_m, crop.ec_slope_pct_per_ds_m)

    weekly_stress: list[WeeklyStress] = []
    alerts: list[str] = []
    weighted_factor_sum = 0.0
    total_weight = 0.0
    consecutive_heat_weeks = 0
    heat_sterility_applied = False
    current_stage = "germination"

    for wk in season.weeks:
        week_idx = wk.week_number - 1
        progress = week_idx / total_weeks
        stage = _get_stage(progress)

        # Stage progress within current stage (for Kc interpolation)
        lo, hi = STAGE_BOUNDARIES[stage]
        stage_progress = (progress - lo) / max(hi - lo, 0.01)
        kc = _get_kc(crop, stage, stage_progress)

        f_temp  = temperature_factor(
            wk.temp_mean,
            crop.critical_temp_low,
            crop.optimal_temp_min,
            crop.optimal_temp_max,
            crop.critical_temp_high,
        )
        f_water = water_stress_factor(
            wk.precipitation_mm, wk.et0_mm, kc, water.method, soil.texture
        )
        f_rad   = radiation_factor(wk.solar_radiation_mj_m2)
        combined = f_temp * f_water * f_salt * f_ph * f_nutr * f_rad

        ws = WeeklyStress(
            week=wk.week_number,
            stage=stage,
            temperature_factor=round(f_temp, 3),
            water_factor=round(f_water, 3),
            salinity_factor=round(f_salt, 3),
            ph_factor=round(f_ph, 3),
            nutrient_factor=round(f_nutr, 3),
            radiation_factor=round(f_rad, 3),
            combined=round(combined, 3),
        )
        weekly_stress.append(ws)

        # Stage-weighted accumulation
        w = STAGE_WEIGHTS[stage]
        weighted_factor_sum += combined * w
        total_weight += w

        # Alert thresholds
        if f_temp < 0.6:
            alerts.append(f"Week {wk.week_number} ({stage}): Temperature stress (factor={f_temp:.2f})")
        if f_water < 0.5:
            alerts.append(f"Week {wk.week_number} ({stage}): Severe water stress (factor={f_water:.2f})")
        if f_salt < 0.75:
            alerts.append(f"Week {wk.week_number} ({stage}): Salinity stress (EC={water.ec_ds_m} dS/m)")

        # Consecutive heat stress during reproductive stage
        if stage == "reproductive" and wk.temp_max_avg > crop.critical_temp_high:
            consecutive_heat_weeks += 1
            if consecutive_heat_weeks >= 3 and not heat_sterility_applied:
                heat_sterility_applied = True
                alerts.append(f"Week {wk.week_number}: Sustained heat during grain fill — floret sterility penalty applied (-20%)")
        else:
            consecutive_heat_weeks = 0

        current_stage = stage

    yield_factor = weighted_factor_sum / max(total_weight, 0.01)
    if heat_sterility_applied:
        yield_factor *= 0.80

    simulated_yield = crop.base_yield_t_ha * yield_factor
    yield_gap_pct = (1.0 - yield_factor) * 100.0
    dominant_stresses = identify_dominant_stresses(weekly_stress)

    return SimulationResult(
        crop_name=crop.display_name,
        variety_label=crop.variety_label,
        location=season.location,
        sowing_date=season.sowing_date.isoformat(),
        harvest_date=season.harvest_date.isoformat(),
        potential_yield_t_ha=crop.base_yield_t_ha,
        simulated_yield_t_ha=round(simulated_yield, 2),
        yield_gap_pct=round(yield_gap_pct, 1),
        season_weeks=total_weeks,
        mean_temp_c=round(season.mean_temp, 1),
        total_rain_mm=round(season.total_precipitation_mm, 0),
        weekly_stress=weekly_stress,
        stage_reports=stage_reports,
        final_report="",
        dominant_stresses=dominant_stresses,
        alerts=alerts,
    )
