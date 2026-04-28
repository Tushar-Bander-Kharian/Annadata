"""Soil water movement — ET drawdown, tipping-bucket drainage, NO3 leaching."""
from __future__ import annotations
import math
from typing import List
from .layer import SoilLayer


def et_drawdown(
    layers: List[SoilLayer],
    et0_mm: float,
    kc: float = 1.0,
    root_depth_cm: float = 60.0,
    beta: float = 0.035,
) -> float:
    """Remove actual crop ET from soil layers before precipitation is added.

    Root water uptake follows an exponential distribution with depth (β = 0.035/cm
    is typical for cereals).  Uptake is limited by available water above wilting
    point in each layer.  Returns actual ET removed (mm).
    """
    etc_cm = et0_mm * kc / 10.0   # potential crop ET in cm

    # Integrate root density per layer: ∫ exp(−β·z) dz from top to bot
    root_fracs: list[float] = []
    for layer in layers:
        if layer.depth_top_cm >= root_depth_cm:
            root_fracs.append(0.0)
        else:
            bot = min(layer.depth_bot_cm, root_depth_cm)
            frac = (
                math.exp(-beta * layer.depth_top_cm)
                - math.exp(-beta * bot)
            ) / beta
            root_fracs.append(max(0.0, frac))

    total_frac = sum(root_fracs)
    if total_frac < 1e-9:
        return 0.0

    actual_et_cm = 0.0
    for layer, frac in zip(layers, root_fracs):
        if frac == 0.0:
            continue
        demand_cm   = etc_cm * frac / total_frac
        available_cm = max(0.0, (layer.theta - layer.wp) * layer.thickness_cm)
        actual_cm   = min(demand_cm, available_cm)
        layer.theta -= actual_cm / layer.thickness_cm
        actual_et_cm += actual_cm

    return actual_et_cm * 10.0   # cm → mm


def tipping_bucket_step(
    layers: List[SoilLayer],
    precip_mm: float,
) -> tuple[float, float]:
    """Sequential tipping-bucket water routing with NO3 leaching.

    Water fills each layer to FC; excess drains downward carrying dissolved
    NO3 proportional to the drainage fraction of water in that layer.

    Returns (deep_drainage_mm, leached_no3_kg_ha).

    ── UPGRADE PATH → Richards equation ────────────────────────────────────
    ∂θ/∂t = ∂/∂z [ K(θ)(∂h/∂z + 1) ] − S
    Requires van Genuchten-Mualem parameters (α, n, Ks) per layer.
    Replace with a finite-difference solver when those parameters are
    measured or estimated from pedotransfer functions.
    ────────────────────────────────────────────────────────────────────────
    """
    inflow_cm   = precip_mm / 10.0
    inflow_no3  = 0.0   # NO3 carried with inflowing water (kg N/ha)

    for layer in layers:
        # Deposit incoming NO3 into this layer before routing water
        layer.n_no3 += inflow_no3
        inflow_no3 = 0.0

        if inflow_cm <= 0.0:
            break

        capacity = (layer.fc - layer.theta) * layer.thickness_cm
        if inflow_cm <= capacity:
            layer.theta += inflow_cm / layer.thickness_cm
            inflow_cm = 0.0
        else:
            overflow = inflow_cm - capacity
            layer.theta = layer.fc
            # NO3 leaches proportionally to drainage fraction of pore water
            water_in_layer = max(layer.theta * layer.thickness_cm, 1e-6)
            frac_leached   = min(1.0, overflow / water_in_layer)
            leached_no3    = layer.n_no3 * frac_leached
            layer.n_no3   -= leached_no3
            inflow_no3     = leached_no3   # carries into next layer
            inflow_cm      = overflow

    # inflow_no3 that exits the bottom is permanently lost (below root zone)
    deep_drainage_mm = inflow_cm * 10.0
    return deep_drainage_mm, inflow_no3
