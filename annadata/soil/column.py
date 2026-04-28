"""SoilColumn — orchestrates all per-layer soil physics each time step."""
from __future__ import annotations
import math
from dataclasses import dataclass, field
from typing import List, Optional

from .layer import SoilLayer
from .carbon import decompose, add_residue, DT_WEEKS
from .water_flow import et_drawdown, tipping_bucket_step
from .nitrogen import nitrify, denitrify, uptake_n


# Ground temperature used for soil-temp depth profile (°C)
# Approximate mean annual soil temperature for the Indo-Gangetic Plain
_T_DEEP_C = 15.0
_DAMPING_DEPTH_CM = 100.0   # thermal damping depth for weekly timestep


def _soil_temp(air_temp_c: float, mid_depth_cm: float) -> float:
    """Exponential damping of air temperature with depth.

    At surface (0 cm):  T_soil ≈ T_air
    At 100 cm:          T_soil ≈ T_deep (15 °C)
    """
    return _T_DEEP_C + (air_temp_c - _T_DEEP_C) * math.exp(-mid_depth_cm / _DAMPING_DEPTH_CM)


@dataclass
class FertiliserEvent:
    """A single fertiliser application event."""
    week: int            # simulation week number (1-indexed)
    n_kg_ha: float       # kg N/ha applied
    form: str = "urea"   # "urea" | "ammonia" → n_nh4 | "nitrate" → n_no3
    depth_cm: float = 5.0   # incorporation depth (applied to layers above this)


# DPM:RPM split by crop type (RothC standard ratios)
_RESIDUE_RATIO: dict[str, tuple[float, float]] = {
    "wheat":    (0.59, 0.41),
    "rice":     (0.59, 0.41),
    "maize":    (0.59, 0.41),
    "soybean":  (0.49, 0.51),
    "cotton":   (0.44, 0.56),
    "default":  (0.59, 0.41),
}

# SOC layer fractions (relative to 0–20 cm measured layer, per 20 cm equivalent)
_LAYER_SOC_REL = [1.00, 0.50, 0.25, 0.24]   # last entry for 60–100 cm (40 cm × 0.12/cm)
_LAYER_N_FRAC  = [0.55, 0.27, 0.13, 0.05]   # mineral N distribution

# Hydraulic presets per texture
_PRESETS: dict[str, dict] = {
    "loam":       {"fc": 0.30, "wp": 0.14, "bd": 1.30},
    "clay_loam":  {"fc": 0.36, "wp": 0.20, "bd": 1.25},
    "sandy_loam": {"fc": 0.22, "wp": 0.10, "bd": 1.45},
    "clay":       {"fc": 0.42, "wp": 0.24, "bd": 1.20},
    "sandy":      {"fc": 0.15, "wp": 0.07, "bd": 1.55},
    "silty":      {"fc": 0.28, "wp": 0.13, "bd": 1.35},
}


class SoilColumn:
    """Manages a vertical 0–100 cm stack of SoilLayer objects.

    Each call to step() runs, in order:
      1. ET drawdown (water removed by roots before rain arrives)
      2. Tipping-bucket drainage with NO3 leaching
      3. Fertiliser application (if any event is scheduled for this week)
      4. Fresh C inputs to DPM/RPM pools
      5. Nitrification (NH4⁺ → NO3⁻) per layer
      6. Denitrification (NO3⁻ → N₂O) per layer — only if waterlogged
      7. Five-pool decomposition with temperature-depth profile
      8. Crop N uptake from root zone (called separately via uptake_n())

    N uptake is NOT inside step() — the simulator calls uptake_n() after
    computing combined_factor so it can scale demand by actual growth.
    """

    def __init__(self, layers: List[SoilLayer]):
        self.layers = layers
        self.fertiliser_schedule: list[FertiliserEvent] = []

    # ── Public API ────────────────────────────────────────────────────────────

    def schedule_fertiliser(self, event: FertiliserEvent) -> None:
        self.fertiliser_schedule.append(event)

    def step(
        self,
        temp_c: float,
        precip_mm: float,
        et0_mm: float = 0.0,
        kc: float = 1.0,
        c_input_t_ha: float = 0.0,
        root_depth_cm: float = 60.0,
        week: int = 0,
        dt: float = DT_WEEKS,
        crop_key: str = "default",
        irrigation_mm: float = 0.0,
    ) -> dict:
        """Advance all soil processes one time step.

        Returns a diagnostics dict consumed by the simulator for
        the weekly_soil output that feeds the UI charts.
        """
        # 1. ET drawdown — remove water before precipitation
        actual_et_mm = et_drawdown(self.layers, et0_mm, kc, root_depth_cm)

        # 2. Tipping-bucket + NO3 leaching (precipitation + applied irrigation)
        drainage_mm, leached_no3 = tipping_bucket_step(self.layers, precip_mm + irrigation_mm)

        # 3. Fertiliser events for this week
        self._apply_fertiliser(week)

        # 4. Fresh C input (root exudates + rhizodeposition) weighted by layer
        if c_input_t_ha > 0.0:
            self._distribute_residue(c_input_t_ha, root_depth_cm, crop_key)

        # 5–7. Per-layer transformations with depth-damped soil temperature
        total_nitrified   = 0.0
        total_denitrified = 0.0
        total_co2         = 0.0

        for layer in self.layers:
            t_soil = _soil_temp(temp_c, layer.mid_depth_cm)
            total_nitrified   += nitrify(layer, t_soil, dt)
            total_denitrified += denitrify(layer, t_soil, dt)
            result = decompose(layer, t_soil, dt)
            total_co2         += result["co2_t_ha"]

        return {
            "actual_et_mm":    round(actual_et_mm,    1),
            "drainage_mm":     round(drainage_mm,     1),
            "leached_no3":     round(leached_no3,     2),
            "denitrified_n":   round(total_denitrified, 2),
            "nitrified_n":     round(total_nitrified, 2),
            "co2_t_ha":        round(total_co2,       4),
        }

    def uptake_n(self, demand_kg_ha: float, root_depth_cm: float = 60.0) -> float:
        """Remove mineral N from root zone to satisfy crop N demand."""
        return uptake_n(self.layers, demand_kg_ha, root_depth_cm)

    # ── Summary accessors ─────────────────────────────────────────────────────

    def total_soc(self) -> float:
        """Total SOC (t C/ha) across all five pools and all layers."""
        return sum(l.total_soc for l in self.layers)

    def rootzone_n(self, root_depth_cm: float = 60.0) -> float:
        """Total mineral N (NH4 + NO3) within the root zone (kg N/ha)."""
        return sum(l.n_mineral for l in self.layers if l.depth_top_cm < root_depth_cm)

    def rootzone_nh4(self, root_depth_cm: float = 60.0) -> float:
        return sum(l.n_nh4 for l in self.layers if l.depth_top_cm < root_depth_cm)

    def rootzone_no3(self, root_depth_cm: float = 60.0) -> float:
        return sum(l.n_no3 for l in self.layers if l.depth_top_cm < root_depth_cm)

    def pool_total(self, pool: str) -> float:
        """Sum a named C pool across all layers (e.g. 'soc_bio', 'soc_hum')."""
        return sum(getattr(l, pool, 0.0) for l in self.layers)

    def water_stress_ks(self, root_depth_cm: float = 60.0, p: float = 0.5) -> float:
        """FAO-56 water stress coefficient Ks derived from actual soil moisture.

        Replaces the old precipitation-ratio approach with physics-based stress:
          Ks = 1.0  when rootzone depletion ≤ readily-available water (RAW = p × TAW)
          Ks → 0    as soil dries toward wilting point

        p = 0.5 is the FAO-56 default depletion fraction for most field crops.
        """
        rz = [l for l in self.layers if l.depth_top_cm < root_depth_cm]
        total_taw = 0.0
        total_dr = 0.0
        for layer in rz:
            bot = min(layer.depth_bot_cm, root_depth_cm)
            thick = bot - layer.depth_top_cm
            taw = max(0.0, layer.fc - layer.wp) * thick   # cm of available water
            dr  = max(0.0, layer.fc - layer.theta) * thick  # cm depletion from FC
            total_taw += taw
            total_dr  += dr
        if total_taw < 1e-6:
            return 1.0
        raw = p * total_taw
        if total_dr <= raw:
            return 1.0
        return max(0.0, (total_taw - total_dr) / max((1.0 - p) * total_taw, 1e-6))

    def surface_theta(self) -> float:
        return self.layers[0].theta

    # ── Constructors ──────────────────────────────────────────────────────────

    @classmethod
    def from_soil_state(cls, soil, som_quality: str = "typical") -> "SoilColumn":
        """Build a column from user-measured SoilState inputs.

        som_quality controls the microbial BIO pool fraction relative to total SOC:
          "degraded"  → BIO × 0.4  (compacted, low biological activity)
          "typical"   → BIO × 1.0  (Falloon 1998 standard: ~3 % of non-IOM SOC)
          "amended"   → BIO × 2.5  (recently manured / compost-amended soil)
        """
        tex = soil.texture.lower().replace(" ", "_")
        p   = _PRESETS.get(tex, _PRESETS["loam"])
        fc, wp, bd = p["fc"], p["wp"], p["bd"]
        surface_ph = getattr(soil, "ph", 7.5)

        # SOC in 0–20 cm from user's OM% (Van Bemmelen: SOC% = OM%/1.724)
        soc_pct      = soil.organic_matter_pct / 1.724       # %
        soc_top_tcha = (soc_pct / 100.0) * bd * 0.20 * 10000  # t C/ha

        # Layer SOC (t C/ha), declining exponentially with depth
        layer_soc = [soc_top_tcha * r for r in _LAYER_SOC_REL]

        # SOM quality → BIO pool multiplier
        _bio_mult = {"degraded": 0.40, "typical": 1.0, "amended": 2.5}.get(som_quality, 1.0)

        # Pool allocation within each layer
        def _split_pools(soc: float):
            # IOM: Falloon et al. 1998 equation
            iom = min(soc * 0.12, 0.049 * (max(soc, 0.1) ** 1.139))
            remaining = max(0.0, soc - iom)
            bio = min(remaining * 0.03 * _bio_mult, remaining * 0.25)  # cap at 25 % of non-IOM
            hum = remaining - bio
            return bio, hum, iom

        # Mineral N distribution across layers (70 % NH4 / 30 % NO3 for upland)
        n_total = getattr(soil, "nitrogen_kg_ha", 90.0)

        layers = []
        for idx, (top, bot) in enumerate([(0, 20), (20, 40), (40, 60), (60, 100)]):
            soc      = layer_soc[idx]
            bio, hum, iom = _split_pools(soc)
            n_layer  = n_total * _LAYER_N_FRAC[idx]
            layer_ph = min(9.0, surface_ph + idx * 0.10)

            layers.append(SoilLayer(
                depth_top_cm=top, depth_bot_cm=bot, texture=tex,
                theta=fc * (0.90 - idx * 0.08),
                fc=fc - idx * 0.01, wp=wp,
                soc_dpm=0.0, soc_rpm=0.0,
                soc_bio=bio, soc_hum=hum, soc_iom=iom,
                n_nh4=n_layer * 0.70, n_no3=n_layer * 0.30,
                ph=layer_ph, bulk_density=bd,
            ))
        return cls(layers)

    @classmethod
    def from_defaults(cls, texture: str = "loam") -> "SoilColumn":
        """Four-layer column with hardcoded Udaipur Alfisol/Inceptisol values.

        Kept for smoke-testing and backward compatibility.
        Use from_soil_state() for real simulations.
        """
        p = _PRESETS.get(texture, _PRESETS["loam"])
        fc, wp, bd = p["fc"], p["wp"], p["bd"]
        return cls([
            SoilLayer( 0,  20, texture, theta=fc*0.90, fc=fc,       wp=wp,
                       soc_bio=0.80, soc_hum=4.20, soc_iom=0.50,
                       n_nh4=21.0, n_no3=9.0, ph=7.5, bulk_density=bd),
            SoilLayer(20,  40, texture, theta=fc*0.80, fc=fc-0.02,  wp=wp,
                       soc_bio=0.30, soc_hum=2.10, soc_iom=0.20,
                       n_nh4=10.5, n_no3=4.5, ph=7.8, bulk_density=bd),
            SoilLayer(40,  60, texture, theta=fc*0.70, fc=fc-0.03,  wp=wp,
                       soc_bio=0.10, soc_hum=1.00, soc_iom=0.08,
                       n_nh4=5.6,  n_no3=2.4, ph=8.0, bulk_density=bd),
            SoilLayer(60, 100, texture, theta=fc*0.60, fc=fc-0.04,  wp=wp,
                       soc_bio=0.05, soc_hum=0.50, soc_iom=0.04,
                       n_nh4=1.4,  n_no3=0.6, ph=8.1, bulk_density=bd),
        ])

    # ── Private helpers ───────────────────────────────────────────────────────

    def _apply_fertiliser(self, week: int) -> None:
        for event in self.fertiliser_schedule:
            if event.week != week:
                continue
            for layer in self.layers:
                if layer.depth_top_cm < event.depth_cm:
                    if event.form == "nitrate":
                        layer.n_no3 += event.n_kg_ha
                    else:
                        layer.n_nh4 += event.n_kg_ha   # urea / ammonia → NH4
                    break  # apply to first matching layer only

    def _distribute_residue(
        self, c_input_t_ha: float, root_depth_cm: float, crop_key: str
    ) -> None:
        """Distribute weekly root C input across root-zone layers by thickness."""
        dpm_f, rpm_f = _RESIDUE_RATIO.get(crop_key, _RESIDUE_RATIO["default"])
        rz = [l for l in self.layers if l.depth_top_cm < root_depth_cm]
        if not rz:
            return
        total_thick = sum(
            min(l.depth_bot_cm, root_depth_cm) - l.depth_top_cm for l in rz
        )
        for layer in rz:
            effective_thick = min(layer.depth_bot_cm, root_depth_cm) - layer.depth_top_cm
            frac = effective_thick / max(total_thick, 1e-6)
            add_residue(layer, c_input_t_ha * frac, dpm_f, rpm_f)
