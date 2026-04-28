"""Soil nitrogen transformations — nitrification, denitrification, crop uptake.

All functions mutate SoilLayer fields in-place and return the amount transformed
(kg N/ha) for diagnostic tracking.
"""
from __future__ import annotations
from typing import List
from .layer import SoilLayer

# ── Rate constants ────────────────────────────────────────────────────────────
K_NIT = 18.25   # yr⁻¹ nitrification at optimal conditions (~5 %/day × 365)
K_DEN =  7.30   # yr⁻¹ denitrification at optimal conditions (~2 %/day × 365)
Q10_N =  2.0    # temperature sensitivity


def nitrify(layer: SoilLayer, temp_c: float, dt: float) -> float:
    """NH4⁺ → NO3⁻ nitrification.  Returns N nitrified (kg N/ha).

    Suppressed when cold (< 5 °C) or waterlogged (WFPS > 0.8).
    Optimal at 20–35 °C and WFPS 0.4–0.6.
    """
    if layer.n_nh4 <= 0.0:
        return 0.0

    # Temperature modifier
    if temp_c <= 5.0:
        t_mod = 0.0
    elif temp_c <= 25.0:
        t_mod = (temp_c - 5.0) / 20.0
    elif temp_c <= 35.0:
        t_mod = 1.0
    else:
        t_mod = max(0.0, 1.0 - (temp_c - 35.0) / 15.0)

    # WFPS moisture modifier
    wfps = layer.water_filled_pore_space
    if wfps < 0.10:
        m_mod = 0.0
    elif wfps <= 0.40:
        m_mod = wfps / 0.40
    elif wfps <= 0.60:
        m_mod = 1.0
    elif wfps <= 0.80:
        m_mod = (0.80 - wfps) / 0.20
    else:
        m_mod = 0.0

    delta = min(K_NIT * t_mod * m_mod * layer.n_nh4 * dt, layer.n_nh4)
    layer.n_nh4 -= delta
    layer.n_no3 += delta
    return delta


def denitrify(layer: SoilLayer, temp_c: float, dt: float) -> float:
    """NO3⁻ → N₂O/N₂ under anaerobic conditions.  Returns N lost (kg N/ha).

    Only active above WFPS 0.60.  Rate scales with labile C availability
    (proxied by soc_bio + soc_dpm) and increases sharply toward saturation.
    """
    if layer.n_no3 <= 0.0:
        return 0.0
    wfps = layer.water_filled_pore_space
    if wfps <= 0.60:
        return 0.0

    t_mod = Q10_N ** ((temp_c - 20.0) / 10.0)
    m_mod = min(1.0, ((wfps - 0.60) / 0.40) ** 1.5)

    # Labile C availability scales denitrification (more C → faster N2O)
    labile_c = layer.soc_bio + layer.soc_dpm * 50.0   # weight DPM higher (fresh)
    c_mod = min(1.0, labile_c / max(labile_c + 0.5, 1e-6))

    delta = min(K_DEN * t_mod * m_mod * c_mod * layer.n_no3 * dt, layer.n_no3)
    layer.n_no3 -= delta
    return delta


def uptake_n(
    layers: List[SoilLayer],
    demand_kg_ha: float,
    root_depth_cm: float = 60.0,
) -> float:
    """Remove mineral N from root zone to satisfy weekly crop demand.

    Preferentially removes NO3⁻ (preferred by most crops).
    Plants cannot deplete below a 20 % residual (diffusion limitation).
    Returns actual N taken up (kg N/ha).
    """
    if demand_kg_ha <= 0.0:
        return 0.0

    rz = [l for l in layers if l.depth_top_cm < root_depth_cm and l.n_mineral > 0.0]
    total_available = sum(l.n_mineral for l in rz)
    if total_available <= 0.0:
        return 0.0

    # Plants can access at most 80 % of available mineral N per week
    actual = min(demand_kg_ha, total_available * 0.80)
    frac = actual / total_available

    for layer in rz:
        take = layer.n_mineral * frac
        from_no3 = min(take, layer.n_no3)
        layer.n_no3 -= from_no3
        layer.n_nh4 = max(0.0, layer.n_nh4 - (take - from_no3))

    return actual
