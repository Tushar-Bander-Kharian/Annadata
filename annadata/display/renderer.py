"""Rich terminal renderer for Annadata simulation output."""
from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from annadata.models.climate import SeasonClimate
from annadata.models.inputs import CropVariety, SoilState, WaterQuality
from annadata.models.state import SimulationResult, WeeklyStress

console = Console()

STAGE_COLORS = {
    "germination":  "green",
    "vegetative":   "bright_green",
    "reproductive": "yellow",
    "maturity":     "orange3",
}


def _bar(value: float, width: int = 10) -> str:
    """Visual bar: filled blocks scaled to 0–width."""
    filled = round(value * width)
    color = "green" if value >= 0.8 else "yellow" if value >= 0.6 else "red"
    return f"[{color}]{'█' * filled}{'░' * (width - filled)}[/{color}] {value:.2f}"


def print_banner() -> None:
    console.print(Panel(
        "[bold bright_yellow]ANNADATA[/bold bright_yellow]\n"
        "[dim]Crop Yield Potential Simulator[/dim]",
        border_style="bright_yellow", width=60,
    ))


def print_input_summary(crop: CropVariety, soil: SoilState, water: WaterQuality, location: str) -> None:
    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Field", style="dim", width=22)
    table.add_column("Value")

    table.add_row("Crop", f"[bold]{crop.display_name}[/bold]")
    table.add_row("Variety", crop.variety_label)
    table.add_row("Location", location)
    table.add_row("Growing season", f"{crop.growing_days} days")
    table.add_row("Potential yield", f"{crop.base_yield_t_ha:.1f} t/ha")
    table.add_row("─" * 20, "─" * 25)
    table.add_row("Soil pH", f"{soil.ph}  (optimal: {crop.optimal_ph_min}–{crop.optimal_ph_max})")
    table.add_row("N / P / K", f"{soil.nitrogen_kg_ha} / {soil.phosphorus_kg_ha} / {soil.potassium_kg_ha} kg/ha")
    table.add_row("Organic matter", f"{soil.organic_matter_pct}%")
    table.add_row("Soil texture", soil.texture)
    table.add_row("─" * 20, "─" * 25)
    table.add_row("Irrigation", water.method)
    table.add_row("Water EC", f"{water.ec_ds_m} dS/m  (threshold: {crop.ec_threshold_ds_m})")
    table.add_row("Water pH", str(water.ph))

    console.print(Panel(table, title="[bold]SIMULATION INPUTS[/bold]", border_style="bright_cyan"))


def print_climate_preview(season: SeasonClimate) -> None:
    table = Table(title="Climate Data Preview", box=box.SIMPLE_HEAVY)
    table.add_column("Week", justify="right", style="dim", width=6)
    table.add_column("Dates", style="dim", width=22)
    table.add_column("Mean Temp (°C)", justify="right")
    table.add_column("Rainfall (mm)", justify="right")
    table.add_column("ET₀ (mm)", justify="right")

    weeks_to_show = season.weeks[:4] + (["..."] if len(season.weeks) > 8 else []) + season.weeks[-4:]
    shown_ellipsis = False

    for w in season.weeks:
        if len(season.weeks) > 8 and 4 <= w.week_number <= len(season.weeks) - 4:
            if not shown_ellipsis:
                table.add_row("...", "...", "...", "...", "...")
                shown_ellipsis = True
            continue
        rain_color = "blue" if w.precipitation_mm > 20 else "dim"
        table.add_row(
            str(w.week_number),
            f"{w.start_date} → {w.end_date}",
            f"{w.temp_mean:.1f}",
            f"[{rain_color}]{w.precipitation_mm:.0f}[/{rain_color}]",
            f"{w.et0_mm:.0f}",
        )

    console.print(table)
    console.print(
        f"  [dim]Total rainfall: {season.total_precipitation_mm:.0f} mm  |  "
        f"Mean temp: {season.mean_temp:.1f}°C  |  "
        f"Total ET₀: {season.total_et0_mm:.0f} mm[/dim]"
    )


def print_weekly_stress(ws: WeeklyStress) -> None:
    stage_color = STAGE_COLORS.get(ws.stage, "white")
    combined_color = "green" if ws.combined >= 0.8 else "yellow" if ws.combined >= 0.6 else "red"
    console.print(
        f"  [dim]W{ws.week:02d}[/dim] [{stage_color}]{ws.stage[:4].upper()}[/{stage_color}]"
        f"  T:{ws.temperature_factor:.2f} W:{ws.water_factor:.2f}"
        f"  S:{ws.salinity_factor:.2f} N:{ws.nutrient_factor:.2f}"
        f"  ▶ [{combined_color}]{ws.combined:.2f}[/{combined_color}]"
    )


def print_stage_transition(stage: str, report_text: str) -> None:
    color = STAGE_COLORS.get(stage, "white")
    console.print()
    console.print(Panel(
        report_text,
        title=f"[bold]STAGE: {stage.upper()}[/bold]",
        border_style=color,
        width=70,
    ))


def print_alerts(alerts: list[str]) -> None:
    if not alerts:
        return
    console.print()
    console.print(Panel(
        "\n".join(f"  [yellow]⚠[/yellow] {a}" for a in alerts),
        title="[bold yellow]CRITICAL ALERTS[/bold yellow]",
        border_style="yellow",
    ))


def print_final_results(result: SimulationResult) -> None:
    console.print()

    # Yield table
    table = Table(box=box.ROUNDED, title="[bold]YIELD OUTCOME[/bold]")
    table.add_column("Metric", style="dim")
    table.add_column("Value", justify="right")

    gap_color = "green" if result.yield_gap_pct < 20 else "yellow" if result.yield_gap_pct < 40 else "red"
    table.add_row("Potential yield (ideal)", f"{result.potential_yield_t_ha:.1f} t/ha")
    table.add_row("Simulated yield", f"[bold]{result.simulated_yield_t_ha:.2f} t/ha[/bold]")
    table.add_row("Yield gap", f"[{gap_color}]{result.yield_gap_pct:.1f}% below potential[/{gap_color}]")
    table.add_row("Season weeks", str(result.season_weeks))
    table.add_row("Mean temperature", f"{result.mean_temp_c:.1f}°C")
    table.add_row("Total rainfall", f"{result.total_rain_mm:.0f} mm")

    console.print(table)

    # Dominant stresses
    if result.dominant_stresses:
        console.print()
        console.print("[bold]Top limiting factors:[/bold]")
        for i, s in enumerate(result.dominant_stresses, 1):
            console.print(f"  {i}. [red]{s}[/red]")


def print_final_report(report: str) -> None:
    console.print()
    console.print(Panel(
        report,
        title="[bold]AGRONOMIST ADVISORY REPORT[/bold]",
        border_style="bright_cyan",
        width=80,
    ))
