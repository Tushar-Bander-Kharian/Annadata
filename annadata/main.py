"""Annadata — Crop Yield Potential Simulator.

Usage:
    ANNADATA_BACKEND=grok   python -m annadata.main
    ANNADATA_BACKEND=claude python -m annadata.main
    ANNADATA_BACKEND=ollama python -m annadata.main
"""
from __future__ import annotations

import asyncio
import sys
from datetime import date, timedelta

from rich.console import Console
from rich.prompt import FloatPrompt, Prompt

from annadata.agents.agronomist import write_final_report
from annadata.agents.stage_analyst import assess_stage
from annadata.climate.fetcher import fetch_season_climate
from annadata.climate.geocoder import geocode
from annadata.config import (
    ANTHROPIC_API_KEY,
    CROP_DB,
    GROK_API_KEY,
    LLM_BACKEND,
    REGION_SOIL_PRESETS,
    SOIL_TEXTURES,
    STAGE_BOUNDARIES,
)
from annadata.display.renderer import (
    console,
    print_alerts,
    print_banner,
    print_climate_preview,
    print_final_report,
    print_final_results,
    print_input_summary,
    print_stage_transition,
    print_weekly_stress,
)
from annadata.engine.simulator import run_simulation
from annadata.engine.stress import (
    nutrient_factor,
    radiation_factor,
    salinity_factor,
    soil_ph_factor,
    temperature_factor,
    water_stress_factor,
)
from annadata.llm import create_client
from annadata.models.climate import SeasonClimate
from annadata.models.inputs import CropVariety, SoilState, WaterQuality
from annadata.models.state import WeeklyStress


def _get_crop() -> CropVariety:
    crops = list(CROP_DB.keys())
    console.print("\n[bold]Available crops:[/bold]")
    for i, k in enumerate(crops, 1):
        console.print(f"  {i}. {CROP_DB[k]['display_name']}")

    choice = Prompt.ask(
        "\nEnter crop name",
        choices=crops,
        default="wheat",
    )
    db = CROP_DB[choice]
    variety = Prompt.ask("Variety label (e.g. HD-2967, local)", default="local")

    return CropVariety(
        key=choice,
        display_name=db["display_name"],
        variety_label=variety,
        base_yield_t_ha=db["base_yield_t_ha"],
        growing_days=db["growing_days"],
        optimal_temp_min=db["optimal_temp_min"],
        optimal_temp_max=db["optimal_temp_max"],
        critical_temp_high=db["critical_temp_high"],
        critical_temp_low=db["critical_temp_low"],
        optimal_ph_min=db["optimal_ph_min"],
        optimal_ph_max=db["optimal_ph_max"],
        ec_threshold_ds_m=db["ec_threshold_ds_m"],
        ec_slope_pct_per_ds_m=db["ec_slope_pct_per_ds_m"],
        n_demand_kg_per_t=db["n_demand_kg_per_t"],
        p_demand_kg_per_t=db["p_demand_kg_per_t"],
        k_demand_kg_per_t=db["k_demand_kg_per_t"],
        kc=db["kc"],
    )


def _get_soil() -> SoilState:
    """Collect soil parameters, optionally loading from a regional preset."""
    console.print("\n[bold]Soil Parameters[/bold]")

    # --- Regional preset shortcut ---
    all_preset_keys = [
        key
        for presets in REGION_SOIL_PRESETS.values()
        for key in presets
    ]
    console.print("  [dim]Available regional presets (measured field data):[/dim]")
    for state, presets in REGION_SOIL_PRESETS.items():
        for key, meta in presets.items():
            console.print(f"    [cyan]{key}[/cyan] — {meta['display_name']}")
    console.print("  [dim]Enter a preset key above, or press Enter to input manually.[/dim]")
    preset_choice = Prompt.ask("  Load regional preset", default="manual")

    defaults: dict = {}
    if preset_choice in all_preset_keys:
        for state, presets in REGION_SOIL_PRESETS.items():
            if preset_choice in presets:
                defaults = presets[preset_choice]
                break
        console.print(
            f"  [green]✓[/green] Loaded preset: [bold]{defaults['display_name']}[/bold]"
        )
        console.print("  [dim](You may still override individual values below.)[/dim]")

    textures = list(SOIL_TEXTURES.keys())
    ph  = FloatPrompt.ask("  Soil pH",               default=float(defaults.get("ph", 6.5)))
    n   = FloatPrompt.ask("  Nitrogen (kg/ha)",       default=float(defaults.get("nitrogen_kg_ha", 80.0)))
    p   = FloatPrompt.ask("  Phosphorus (kg/ha)",     default=float(defaults.get("phosphorus_kg_ha", 30.0)))
    k   = FloatPrompt.ask("  Potassium (kg/ha)",      default=float(defaults.get("potassium_kg_ha", 120.0)))
    om  = FloatPrompt.ask("  Organic matter (%)",     default=float(defaults.get("organic_matter_pct", 1.5)))
    console.print(f"  Soil textures: {', '.join(textures)}")
    tex = Prompt.ask(
        "  Soil texture",
        choices=textures,
        default=str(defaults.get("texture", "loam")),
    )
    return SoilState(ph=ph, nitrogen_kg_ha=n, phosphorus_kg_ha=p,
                     potassium_kg_ha=k, organic_matter_pct=om, texture=tex)


def _get_water() -> WaterQuality:
    console.print("\n[bold]Water Quality[/bold]")
    methods = ["rainfed", "drip", "flood", "furrow", "sprinkler"]
    ph  = FloatPrompt.ask("  Irrigation water pH", default=7.0)
    ec  = FloatPrompt.ask("  Electrical conductivity EC (dS/m)", default=0.5)
    console.print(f"  Methods: {', '.join(methods)}")
    mth = Prompt.ask("  Irrigation method", choices=methods, default="drip")
    return WaterQuality(ph=ph, ec_ds_m=ec, method=mth)


def _get_sowing_date(growing_days: int) -> date:
    """Default: start the season 1 year ago so archive data is available."""
    default = date.today() - timedelta(days=365)
    console.print(f"\n[bold]Sowing Date[/bold]  [dim](archive data needed — defaults to 1 year ago)[/dim]")
    date_str = Prompt.ask("  Sowing date (YYYY-MM-DD)", default=default.isoformat())
    return date.fromisoformat(date_str)


async def run_simulation_async() -> None:
    print_banner()

    # --- Validate API keys ---
    if LLM_BACKEND == "grok" and not GROK_API_KEY:
        console.print("[red]GROK_API_KEY not set. Run: set GROK_API_KEY=your-key[/red]")
        sys.exit(1)
    if LLM_BACKEND == "claude" and not ANTHROPIC_API_KEY:
        console.print("[red]ANTHROPIC_API_KEY not set.[/red]")
        sys.exit(1)

    console.print(f"  [dim]LLM Backend: {LLM_BACKEND.upper()}[/dim]\n")

    # --- Collect inputs ---
    crop  = _get_crop()
    soil  = _get_soil()
    water = _get_water()
    sowing_date = _get_sowing_date(crop.growing_days)
    location_query = Prompt.ask("\nLocation (city name)", default="New Delhi")

    llm = create_client()

    # --- Geocode ---
    console.print()
    with console.status(f"Locating [bold]{location_query}[/bold]..."):
        lat, lon, resolved_name = await geocode(location_query)
    console.print(f"  [green]✓[/green] {resolved_name}  ({lat:.3f}°, {lon:.3f}°)")

    # --- Fetch climate ---
    with console.status("Fetching climate data from Open-Meteo..."):
        season = await fetch_season_climate(lat, lon, resolved_name, sowing_date, crop.growing_days)
    console.print(f"  [green]✓[/green] {len(season.weeks)} weeks of climate data loaded")

    print_input_summary(crop, soil, water, resolved_name)
    print_climate_preview(season)

    # --- Simulate with LLM stage assessments ---
    console.print("\n[bold]Running simulation...[/bold]\n")

    stage_reports: dict[str, str] = {}
    current_stage = ""
    stage_weeks: list[WeeklyStress] = []
    total_weeks = len(season.weeks)

    # We need to compute stress factors week-by-week here to trigger stage LLM calls.
    # We reuse the same stress functions from engine/stress.py.
    from annadata.config import STAGE_WEIGHTS
    from annadata.engine.stress import (
        identify_dominant_stresses,
    )

    all_weekly_stress: list[WeeklyStress] = []
    alerts: list[str] = []
    weighted_factor_sum = 0.0
    total_weight = 0.0
    consecutive_heat = 0
    heat_sterility = False

    f_nutr = nutrient_factor(
        soil.nitrogen_kg_ha, soil.phosphorus_kg_ha, soil.potassium_kg_ha,
        soil.organic_matter_pct, crop.base_yield_t_ha,
        crop.n_demand_kg_per_t, crop.p_demand_kg_per_t, crop.k_demand_kg_per_t,
    )
    f_ph   = soil_ph_factor(soil.ph, crop.optimal_ph_min, crop.optimal_ph_max)
    f_salt = salinity_factor(water.ec_ds_m, crop.ec_threshold_ds_m, crop.ec_slope_pct_per_ds_m)

    stage_order = ["germination", "vegetative", "reproductive", "maturity"]

    for wk in season.weeks:
        week_idx = wk.week_number - 1
        progress = week_idx / total_weeks
        lo_hi = {s: STAGE_BOUNDARIES[s] for s in stage_order}
        stage = next(
            (s for s, (lo, hi) in lo_hi.items() if lo <= progress < hi),
            "maturity",
        )

        # Stage transition detected
        if stage != current_stage:
            # Flush previous stage to LLM if we have weeks
            if current_stage and stage_weeks:
                console.print(f"  [dim]Requesting stage analysis: {current_stage}...[/dim]")
                report = await assess_stage(crop, soil, water, current_stage, stage_weeks, season, llm)
                stage_reports[current_stage] = report
                print_stage_transition(current_stage, report)

            current_stage = stage
            stage_weeks = []

        lo, hi = STAGE_BOUNDARIES[stage]
        stage_progress = (progress - lo) / max(hi - lo, 0.01)
        # Kc interpolation
        idx = stage_order.index(stage)
        kc_now = crop.kc[stage]
        kc_next = crop.kc[stage_order[min(idx + 1, len(stage_order) - 1)]]
        kc = kc_now + (kc_next - kc_now) * stage_progress

        f_temp  = temperature_factor(wk.temp_mean, crop.critical_temp_low,
                                     crop.optimal_temp_min, crop.optimal_temp_max, crop.critical_temp_high)
        f_water = water_stress_factor(wk.precipitation_mm, wk.et0_mm, kc, water.method, soil.texture)
        f_rad   = radiation_factor(wk.solar_radiation_mj_m2)
        combined = f_temp * f_water * f_salt * f_ph * f_nutr * f_rad

        ws = WeeklyStress(
            week=wk.week_number, stage=stage,
            temperature_factor=round(f_temp, 3),
            water_factor=round(f_water, 3),
            salinity_factor=round(f_salt, 3),
            ph_factor=round(f_ph, 3),
            nutrient_factor=round(f_nutr, 3),
            radiation_factor=round(f_rad, 3),
            combined=round(combined, 3),
        )
        all_weekly_stress.append(ws)
        stage_weeks.append(ws)
        print_weekly_stress(ws)

        w = STAGE_WEIGHTS[stage]
        weighted_factor_sum += combined * w
        total_weight += w

        if f_temp < 0.6:
            alerts.append(f"Week {wk.week_number} ({stage}): Temperature stress ({f_temp:.2f})")
        if f_water < 0.5:
            alerts.append(f"Week {wk.week_number} ({stage}): Severe water deficit ({f_water:.2f})")
        if f_salt < 0.75:
            alerts.append(f"Week {wk.week_number} ({stage}): Salinity stress (EC={water.ec_ds_m} dS/m)")

        if stage == "reproductive" and wk.temp_max_avg > crop.critical_temp_high:
            consecutive_heat += 1
            if consecutive_heat >= 3 and not heat_sterility:
                heat_sterility = True
                alerts.append(f"Week {wk.week_number}: Sustained heat during grain fill — sterility penalty applied")
        else:
            consecutive_heat = 0

    # Final stage flush
    if current_stage and stage_weeks:
        console.print(f"  [dim]Requesting stage analysis: {current_stage}...[/dim]")
        report = await assess_stage(crop, soil, water, current_stage, stage_weeks, season, llm)
        stage_reports[current_stage] = report
        print_stage_transition(current_stage, report)

    # Compute final yield
    yield_factor = weighted_factor_sum / max(total_weight, 0.01)
    if heat_sterility:
        yield_factor *= 0.80
    simulated_yield = round(crop.base_yield_t_ha * yield_factor, 2)
    yield_gap_pct = round((1.0 - yield_factor) * 100.0, 1)
    dominant_stresses = identify_dominant_stresses(all_weekly_stress)

    from annadata.models.state import SimulationResult
    result = SimulationResult(
        crop_name=crop.display_name,
        variety_label=crop.variety_label,
        location=resolved_name,
        sowing_date=sowing_date.isoformat(),
        harvest_date=(sowing_date + __import__("datetime").timedelta(days=crop.growing_days)).isoformat(),
        potential_yield_t_ha=crop.base_yield_t_ha,
        simulated_yield_t_ha=simulated_yield,
        yield_gap_pct=yield_gap_pct,
        season_weeks=total_weeks,
        mean_temp_c=round(season.mean_temp, 1),
        total_rain_mm=round(season.total_precipitation_mm, 0),
        weekly_stress=all_weekly_stress,
        stage_reports=stage_reports,
        final_report="",
        dominant_stresses=dominant_stresses,
        alerts=alerts,
    )

    print_alerts(alerts)
    print_final_results(result)

    # --- Final agronomist report ---
    console.print("\n[dim]Generating agronomist report...[/dim]")
    final_report = await write_final_report(result, crop, soil, water, season, llm)
    print_final_report(final_report)


def main() -> None:
    asyncio.run(run_simulation_async())


if __name__ == "__main__":
    main()
