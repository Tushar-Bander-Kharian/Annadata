from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class SoilLayer:
    # ── Geometry ─────────────────────────────────────────────────────────────
    depth_top_cm: float
    depth_bot_cm: float
    texture: str             # "loam" | "clay_loam" | "sandy_loam" | "clay" | "sandy" | "silty"

    # ── Water state (cm³/cm³) ────────────────────────────────────────────────
    theta: float             # current volumetric water content
    fc: float                # field capacity
    wp: float                # wilting point

    # ── Five-pool carbon (t C/ha per layer) ──────────────────────────────────
    soc_dpm: float = 0.0    # Decomposable Plant Material  (K ≈ 10/yr,  fresh fast fraction)
    soc_rpm: float = 0.0    # Resistant Plant Material     (K ≈ 0.3/yr, lignin-rich)
    soc_bio: float = 0.0    # Microbial Biomass            (K ≈ 0.66/yr)
    soc_hum: float = 0.0    # Humified SOM                 (K ≈ 0.02/yr)
    soc_iom: float = 0.0    # Inert Organic Matter         (K = 0, passive pool)

    # ── Nitrogen (kg N/ha per layer) ─────────────────────────────────────────
    n_nh4: float = 0.0      # Ammonium — from mineralisation, relatively immobile
    n_no3: float = 0.0      # Nitrate  — leachable, denitrifiable

    # ── Soil chemistry ───────────────────────────────────────────────────────
    ph: float = 7.0
    bulk_density: float = 1.3

    # ── Derived properties ───────────────────────────────────────────────────
    @property
    def thickness_cm(self) -> float:
        return self.depth_bot_cm - self.depth_top_cm

    @property
    def mid_depth_cm(self) -> float:
        return (self.depth_top_cm + self.depth_bot_cm) / 2.0

    @property
    def n_mineral(self) -> float:
        """Total mineral N (NH4 + NO3) — backward-compatible accessor."""
        return self.n_nh4 + self.n_no3

    @property
    def total_soc(self) -> float:
        """All five C pools summed (t C/ha)."""
        return self.soc_dpm + self.soc_rpm + self.soc_bio + self.soc_hum + self.soc_iom

    @property
    def water_filled_pore_space(self) -> float:
        """WFPS — key driver of nitrification and denitrification."""
        porosity = max(1.0 - (self.bulk_density / 2.65), 0.01)
        return min(1.0, self.theta / porosity)
