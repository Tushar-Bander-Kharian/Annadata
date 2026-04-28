"""LLM Stage Analyst — called once per growth stage transition."""
from __future__ import annotations

from annadata.config import STAGE_MODEL
from annadata.llm import LLMClient
from annadata.models.climate import SeasonClimate
from annadata.models.inputs import CropVariety, SoilState, WaterQuality
from annadata.models.state import WeeklyStress


SYSTEM_PROMPT = """\
You are an agricultural field agronomist conducting a crop health assessment.
You are observing real crop plants and reporting on observable conditions.

Write a concise field report in 3–4 sentences. Include:
1. The primary limiting stress visible at this growth stage
2. One observable symptom the farmer would see in the field
3. Whether the crop is ON TRACK, AT RISK, or SEVERELY STRESSED

Be specific and practical. No markdown formatting."""


async def assess_stage(
    crop: CropVariety,
    soil: SoilState,
    water: WaterQuality,
    stage: str,
    stage_weeks: list[WeeklyStress],
    season: SeasonClimate,
    llm: LLMClient,
) -> str:
    if not stage_weeks:
        return "Insufficient data for stage assessment."

    avg = lambda attr: sum(getattr(w, attr) for w in stage_weeks) / len(stage_weeks)
    avg_temp   = avg("temperature_factor")
    avg_water  = avg("water_factor")
    avg_salt   = avg("salinity_factor")
    avg_nutr   = avg("nutrient_factor")
    avg_rad    = avg("radiation_factor")
    avg_combo  = avg("combined")

    # Find worst week
    worst = min(stage_weeks, key=lambda w: w.combined)
    worst_week_climate = next(
        (wk for wk in season.weeks if wk.week_number == worst.week), None
    )
    worst_temp_str = ""
    if worst_week_climate:
        worst_temp_str = f"  Worst week (#{worst.week}): mean {worst_week_climate.temp_mean:.1f}°C, rain {worst_week_climate.precipitation_mm:.0f}mm"

    flags = []
    if avg_temp < 0.70:   flags.append("TEMPERATURE STRESS")
    if avg_water < 0.65:  flags.append("WATER DEFICIT")
    if avg_salt < 0.85:   flags.append("SALINITY DAMAGE")
    if avg_nutr < 0.75:   flags.append("NUTRIENT DEFICIENCY")

    prompt = f"""\
CROP: {crop.display_name} — Variety: {crop.variety_label}
STAGE: {stage.upper()} ({len(stage_weeks)} weeks)
LOCATION: {season.location}

AVERAGE STRESS FACTORS THIS STAGE:
  Temperature:   {avg_temp:.2f}  {'⚠' if avg_temp < 0.70 else '✓'}
  Water:         {avg_water:.2f}  {'⚠' if avg_water < 0.65 else '✓'}
  Salinity:      {avg_salt:.2f}  {'⚠' if avg_salt < 0.85 else '✓'}
  Soil pH:       {avg_salt:.2f}
  Nutrients:     {avg_nutr:.2f}  {'⚠' if avg_nutr < 0.75 else '✓'}
  Solar Rad:     {avg_rad:.2f}
  COMBINED:      {avg_combo:.2f}
{worst_temp_str}

ACTIVE STRESS FLAGS: {', '.join(flags) if flags else 'None — conditions acceptable'}

SOIL: pH={soil.ph}, N={soil.nitrogen_kg_ha}kg/ha, P={soil.phosphorus_kg_ha}kg/ha, K={soil.potassium_kg_ha}kg/ha, OM={soil.organic_matter_pct}%, texture={soil.texture}
WATER: {water.method} irrigation, EC={water.ec_ds_m}dS/m, pH={water.ph}

Write your field assessment for this growth stage."""

    try:
        resp = await llm.generate(
            model=STAGE_MODEL,
            system=SYSTEM_PROMPT,
            prompt=prompt,
            max_tokens=200,
        )
        return resp.text.strip()
    except Exception as e:
        return f"[Stage assessment unavailable: {type(e).__name__}]"
