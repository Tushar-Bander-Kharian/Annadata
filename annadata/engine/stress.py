"""Yield stress factor formulas — pure math, no LLM, no I/O.

Every function returns a float in [0.0, 1.0]:
  1.0 = no stress (optimal conditions)
  0.0 = complete crop failure from that factor
"""
from __future__ import annotations
import math

from annadata.config import IRRIGATION_MM_PER_WEEK, OPTIMAL_RADIATION_MJ_PER_WEEK


def soil_ph_factor(ph: float, optimal_min: float, optimal_max: float) -> float:
    """Trapezoidal pH response: full score inside optimal range, linear penalty outside."""
    if optimal_min <= ph <= optimal_max:
        return 1.0
    elif ph < optimal_min:
        if ph <= 4.5:
            return 0.0
        return (ph - 4.5) / (optimal_min - 4.5)
    else:
        if ph >= 9.0:
            return 0.0
        return 1.0 - (ph - optimal_max) / (9.0 - optimal_max)


def temperature_factor(
    temp_mean: float,
    t_base: float,
    t_opt1: float,
    t_opt2: float,
    t_max: float,
) -> float:
    """Trapezoidal temperature response curve (standard agronomy)."""
    dead_zone_high = t_max + 5.0
    if temp_mean <= t_base or temp_mean >= dead_zone_high:
        return 0.0
    elif temp_mean < t_opt1:
        return (temp_mean - t_base) / max(t_opt1 - t_base, 0.01)
    elif temp_mean <= t_opt2:
        return 1.0
    else:
        return max(0.0, 1.0 - (temp_mean - t_opt2) / max(t_max - t_opt2, 0.01))


def water_stress_factor(
    precip_mm: float,
    et0_mm: float,
    kc: float,
    irrigation_method: str,
    soil_texture: str,
) -> float:
    """Water balance stress — considers irrigation method and soil drainage."""
    irr_mm = IRRIGATION_MM_PER_WEEK.get(irrigation_method, 0.0)
    supply = precip_mm + irr_mm
    etc = et0_mm * kc

    if etc < 1.0:
        return 1.0  # dormant / very cold week

    ratio = min(supply / etc, 2.5)

    # Clay soil + flood irrigation → waterlogging risk
    if irrigation_method == "flood" and soil_texture in ("clay", "clay_loam"):
        ratio *= 0.85

    if ratio < 0.4:
        return max(0.0, ratio * 1.5)
    elif ratio < 0.8:
        return 0.6 + (ratio - 0.4) * 1.0
    elif ratio <= 1.8:
        return min(1.0, 0.96 + (ratio - 0.8) * 0.04)
    else:
        # Waterlogging penalty for sensitive crops (handled upstream via ratio cap)
        return max(0.5, 1.0 - (ratio - 1.8) * 0.25)


def salinity_factor(
    irrigation_ec_ds_m: float,
    ec_threshold: float,
    ec_slope_pct_per_ds_m: float,
) -> float:
    """FAO 29 salinity response: linear yield loss above threshold EC."""
    # Soil saturation extract EC ≈ 70% of irrigation water EC
    soil_ec = irrigation_ec_ds_m * 0.7
    if soil_ec <= ec_threshold:
        return 1.0
    loss_pct = ec_slope_pct_per_ds_m * (soil_ec - ec_threshold)
    return max(0.0, 1.0 - loss_pct / 100.0)


def nutrient_factor(
    n_kg_ha: float,
    p_kg_ha: float,
    k_kg_ha: float,
    organic_matter_pct: float,
    base_yield_t_ha: float,
    n_demand_kg_per_t: float,
    p_demand_kg_per_t: float,
    k_demand_kg_per_t: float,
) -> float:
    """Liebig's Law of the Minimum — most deficient nutrient limits yield.

    N is compared to a 4-week critical buffer (not the full season total):
    the rootzone doesn't hold a full season's N simultaneously — it replenishes
    continuously through mineralisation, fertiliser, and leaching.
    P and K are compared against 3× their per-tonne demand (less mobile, slower
    turnover, crop draws from a larger pool than just the top 60 cm).
    """
    # N: rootzone mineral N is a flow, not a stock — compare to 4-week demand
    # buffer so 90 kg/ha at start is not "stressed" vs 145 kg seasonal need.
    # P, K: immobile soil pools compared directly to seasonal crop demand.
    n_critical = max((base_yield_t_ha * n_demand_kg_per_t) / 4.0, 1.0)
    p_critical = max(base_yield_t_ha * p_demand_kg_per_t, 1.0)
    k_critical = max(base_yield_t_ha * k_demand_kg_per_t, 1.0)

    f_n = min(1.0, n_kg_ha / n_critical)
    f_p = min(1.0, p_kg_ha / p_critical)
    f_k = min(1.0, k_kg_ha / k_critical)

    # Organic matter bonus: OM > 2% releases extra N via mineralization
    if organic_matter_pct > 2.0:
        om_bonus = min(0.15, (organic_matter_pct - 2.0) * 0.075)
        f_n = min(1.0, f_n + om_bonus)

    return min(f_n, f_p, f_k)


def radiation_factor(solar_mj_m2: float) -> float:
    """Solar radiation adequacy — floor at 0.3 (cloudy weeks still allow growth)."""
    factor = solar_mj_m2 / OPTIMAL_RADIATION_MJ_PER_WEEK
    return max(0.3, min(1.0, factor))


def canopy_radiation_factor(
    solar_mj_m2: float,
    lai: float,
    k: float = 0.5,
    lai_peak: float = 5.0,
) -> float:
    """Beer-Lambert light interception normalized to peak-canopy optimal radiation.

    Intercepted PAR = solar × (1 − e^{−k·LAI}).  Factor is normalized so that
    peak-LAI at OPTIMAL_RADIATION_MJ_PER_WEEK returns 1.0.

    At germination (LAI≈0.2–0.4) the sparse canopy intercepts little light →
    low rad factor, but the stage weight (0.05) limits its influence on yield.
    At reproductive peak-LAI the factor reaches 1.0 under adequate radiation.
    Floor at 0.10 (even a nearly bare soil has some photosynthetically active
    tissue at germination).
    """
    f_int = 1.0 - math.exp(-k * max(lai, 0.01))
    f_int_peak = 1.0 - math.exp(-k * max(lai_peak, 0.01))
    effective = solar_mj_m2 * f_int
    optimal_eff = OPTIMAL_RADIATION_MJ_PER_WEEK * f_int_peak
    return max(0.10, min(1.0, effective / max(optimal_eff, 1.0)))


def identify_dominant_stresses(weekly_stress: list) -> list[str]:
    """Return top 3 stress factor names by average season impact."""
    from collections import defaultdict
    totals: dict[str, float] = defaultdict(float)
    counts: dict[str, int] = defaultdict(int)

    factor_map = {
        "Temperature stress":  "temperature_factor",
        "Water stress":        "water_factor",
        "Salinity stress":     "salinity_factor",
        "Soil pH stress":      "ph_factor",
        "Nutrient deficiency": "nutrient_factor",
        "Low solar radiation": "radiation_factor",
    }

    for week in weekly_stress:
        for label, attr in factor_map.items():
            totals[label] += getattr(week, attr, 1.0)
            counts[label] += 1

    averages = {label: totals[label] / counts[label] for label in totals}
    # Sort ascending: lowest average = most limiting
    sorted_stresses = sorted(averages.items(), key=lambda x: x[1])
    return [name for name, _ in sorted_stresses[:3]]
