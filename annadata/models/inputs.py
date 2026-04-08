"""
Input data models for Annadata simulation.

Extends the original CropVariety / SoilState / WaterQuality dataclasses
with:
  - Stress modifier fields on CropVariety (from varieties.py profiles)
  - StressOverrides: user-facing slider values for UI control
  - Disease resistance dict on CropVariety
"""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CropVariety:
    """Core agronomic parameters for a named crop variety."""

    name:               str
    base_yield_t_ha:    float
    season_days:        int
    optimal_temp_min:   float
    optimal_temp_max:   float
    critical_temp_high: float
    critical_temp_low:  float

    # Stress tolerance modifiers  (1.0 = normal susceptibility)
    heat_modifier:          float = 1.0
    drought_modifier:       float = 1.0
    waterlogging_modifier:  float = 1.0
    salinity_modifier:      float = 1.0
    cold_modifier:          float = 1.0

    # Disease resistance  {disease_key: 0–1}  (0 = immune, 1 = susceptible)
    disease_resistance: dict[str, float] = field(default_factory=dict)

    # NUE modifier (< 1.0 = more efficient — needs less N for same yield)
    nue_modifier: float = 1.0


@dataclass
class SoilState:
    """Observed soil parameters at simulation start."""

    texture:            str     = "loam"
    ph:                 float   = 7.5
    ec_ds_m:            float   = 0.4
    nitrogen_kg_ha:     float   = 90.0
    phosphorus_kg_ha:   float   = 30.0
    potassium_kg_ha:    float   = 200.0
    organic_matter_pct: float   = 0.7


@dataclass
class WaterQuality:
    """Irrigation water quality and delivery method."""

    ec_ds_m:            float   = 0.4
    ph:                 float   = 7.2
    irrigation_method:  str     = "tube-well"


@dataclass
class StressOverrides:
    """
    User-specified stress severity sliders (0–1).

    0.0 = stress absent / negligible
    0.5 = moderate stress
    1.0 = maximum / lethal stress

    These are ADDITIVE to what the simulation engine already calculates
    from weather data.  They represent field-level conditions that the
    climate data alone cannot capture (e.g. a disease outbreak, pest
    attack, nutrient management decisions, or weed competition).

    Setting a slider to 0 does NOT mean the stress is being suppressed —
    it means the user is not adding any extra penalty beyond what the
    engine already calculates.
    """

    # ── Abiotic ─────────────────────────────────────────────────────────
    heat:           float = 0.0     # extra heat stress (beyond weather)
    drought:        float = 0.0     # extra water deficit
    waterlogging:   float = 0.0     # ponding / poor drainage
    salinity:       float = 0.0     # EC above crop threshold
    cold:           float = 0.0     # chilling / frost

    # ── Fertility ────────────────────────────────────────────────────────
    n_deficiency:   float = 0.0     # nitrogen deficiency severity
    p_deficiency:   float = 0.0     # phosphorus
    k_deficiency:   float = 0.0     # potassium
    zinc:           float = 0.0     # zinc micronutrient deficiency

    # ── Biotic ──────────────────────────────────────────────────────────
    weed:           float = 0.3     # weed competition level
    insect:         float = 0.2     # insect/pest pressure

    # per-disease severity; {disease_key: 0–1}
    disease_severities: dict[str, float] = field(default_factory=dict)

    # HR weed factor from location intel (auto-filled, 0–1)
    herbicide_resistance_factor: float = 0.0
