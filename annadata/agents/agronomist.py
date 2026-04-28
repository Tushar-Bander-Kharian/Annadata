"""LLM Agronomist — writes the final advisory report."""
from __future__ import annotations

from annadata.config import REPORT_MODEL
from annadata.llm import LLMClient
from annadata.models.climate import SeasonClimate
from annadata.models.inputs import CropVariety, SoilState, WaterQuality
from annadata.models.state import SimulationResult


SYSTEM_PROMPT = """\
You are a senior agronomist at an agricultural research institute.
You have received a full-season crop simulation report and must write a structured advisory for the farmer.

Use EXACTLY this format (plain text, no markdown symbols):

SEASON SUMMARY
[2-3 sentences on yield outcome and main limiting factor]

PRIMARY CONSTRAINTS
1. [Most limiting factor with brief explanation]
2. [Second constraint]
3. [Third constraint]

FIELD OBSERVATIONS
[2-3 sentences on observable symptoms that occurred during the season]

RECOMMENDATIONS FOR NEXT SEASON
1. [Specific, actionable recommendation]
2. [Second recommendation]
3. [Third recommendation]
4. [Fourth recommendation]

OUTLOOK
[One sentence on feasibility of reaching target yield with the improvements above]"""


async def write_final_report(
    result: SimulationResult,
    crop: CropVariety,
    soil: SoilState,
    water: WaterQuality,
    season: SeasonClimate,
    llm: LLMClient,
) -> str:
    # Find worst weeks
    if result.weekly_stress:
        worst_temp_wk = min(result.weekly_stress, key=lambda w: w.temperature_factor)
        worst_water_wk = min(result.weekly_stress, key=lambda w: w.water_factor)
    else:
        worst_temp_wk = worst_water_wk = None

    stage_text = "\n".join(
        f"  {stage.upper()}: {text[:200]}"
        for stage, text in result.stage_reports.items()
    )

    prompt = f"""\
SIMULATION REPORT — {result.crop_name} ({result.variety_label})
Location: {result.location}
Season: {result.sowing_date} to {result.harvest_date} ({result.season_weeks} weeks)

YIELD OUTCOME
  Potential (ideal conditions): {result.potential_yield_t_ha:.1f} t/ha
  Simulated (actual):           {result.simulated_yield_t_ha:.2f} t/ha
  Yield gap:                    {result.yield_gap_pct:.1f}% below potential

SEASONAL CLIMATE
  Mean temperature: {result.mean_temp_c:.1f}°C
  Total rainfall:   {result.total_rain_mm:.0f} mm
  Optimal temp range for this crop: {crop.optimal_temp_min}–{crop.optimal_temp_max}°C

STRESS SUMMARY
  Dominant stresses: {', '.join(result.dominant_stresses)}
  Worst temperature week: Week {worst_temp_wk.week if worst_temp_wk else 'N/A'} (factor={worst_temp_wk.temperature_factor:.2f} if worst_temp_wk else 'N/A')
  Worst water week:       Week {worst_water_wk.week if worst_water_wk else 'N/A'} (factor={worst_water_wk.water_factor:.2f if worst_water_wk else 'N/A'})

STAGE ASSESSMENTS
{stage_text if stage_text else '  No stage assessments available.'}

SOIL INPUTS
  pH: {soil.ph}  |  N: {soil.nitrogen_kg_ha} kg/ha  |  P: {soil.phosphorus_kg_ha} kg/ha
  K: {soil.potassium_kg_ha} kg/ha  |  OM: {soil.organic_matter_pct}%  |  Texture: {soil.texture}

WATER INPUTS
  Irrigation method: {water.method}  |  EC: {water.ec_ds_m} dS/m  |  pH: {water.ph}

CRITICAL ALERTS ({len(result.alerts)} total)
{chr(10).join(f'  - {a}' for a in result.alerts[:5]) if result.alerts else '  None'}

Please write your agronomist advisory report for this farmer."""

    try:
        resp = await llm.generate(
            model=REPORT_MODEL,
            system=SYSTEM_PROMPT,
            prompt=prompt,
            max_tokens=600,
        )
        return resp.text.strip()
    except Exception as e:
        return f"[Final report unavailable: {type(e).__name__}]"
