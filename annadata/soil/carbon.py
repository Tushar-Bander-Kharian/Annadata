"""Five-pool RothC-style decomposition.

Pools:  DPM (fast fresh)  →  BIO + HUM + CO2
        RPM (slow fresh)  →  BIO + HUM + CO2
        BIO (microbial)   →  BIO + HUM + CO2  (self-recycling)
        HUM (stable)      →  BIO + HUM + CO2
        IOM (inert)       →  no decomposition

N coupling: each decomposing pool either mineralises or immobilises mineral N
depending on its C:N ratio vs microbial biomass C:N requirement.
"""
from __future__ import annotations
import math
from .layer import SoilLayer

# ── Rate constants (yr⁻¹) ────────────────────────────────────────────────────
K_DPM = 10.00   # Decomposable Plant Material  (RothC standard)
K_RPM =  0.30   # Resistant Plant Material
K_BIO =  0.66   # Microbial Biomass
K_HUM =  0.02   # Humified SOM
K_IOM =  0.00   # Inert Organic Matter

# ── C:N ratios of each pool ──────────────────────────────────────────────────
CN_DPM = 12.0   # Fresh crop residue (mixed quality)
CN_RPM = 40.0   # Lignin-rich material
CN_BIO =  8.0   # Microbial biomass requirement
CN_HUM = 10.0   # Humified SOM
CN_IOM = 10.0   # Same as HUM

DT_WEEKS = 1.0 / 52.0  # One week in years

# Clay fraction lookup — drives RothC partitioning
_CLAY_FRAC: dict[str, float] = {
    "sandy":      0.05,
    "sandy_loam": 0.10,
    "loam":       0.20,
    "silty":      0.18,
    "clay_loam":  0.34,
    "clay":       0.50,
}


def _temp_modifier(temp_c: float) -> float:
    """Q10 = 2.0 response relative to 20 °C reference."""
    return 2.0 ** ((temp_c - 20.0) / 10.0)


def _moisture_modifier(theta: float, fc: float, wp: float) -> float:
    """Three-zone piecewise:
    below WP → 0 (microbes inactive)
    WP to FC → linear 0→1
    above FC → anaerobic suppression, floor 0.1
    """
    if theta <= wp:
        return 0.0
    if theta <= fc:
        return (theta - wp) / max(fc - wp, 1e-6)
    return max(0.1, 1.0 - 0.5 * (theta - fc) / max(1.0 - fc, 1e-6))


def _ph_modifier(ph: float) -> float:
    """Microbial decomposition suppressed outside pH 5.5–8.0 (BODIUM parameterisation)."""
    if 5.5 <= ph <= 8.0:
        return 1.0
    if ph < 5.5:
        return max(0.2, (ph - 3.0) / 2.5)
    return max(0.4, 1.0 - (ph - 8.0) / 2.5)


def _partition_fracs(clay_frac: float) -> tuple[float, float, float]:
    """RothC CO₂ : BIO : HUM partition, clay-dependent.

    At 20 % clay: CO₂ ≈ 78.5 %, BIO ≈ 9.9 %, HUM ≈ 11.6 %
    Higher clay → less CO₂, more stable product.
    """
    clay_pct = clay_frac * 100.0
    x = 1.67 * (1.85 + 1.60 * math.exp(-0.0786 * clay_pct))
    co2_f = x / (x + 1.0)
    bio_f = (1.0 - co2_f) * 0.46
    hum_f = (1.0 - co2_f) * 0.54
    return co2_f, bio_f, hum_f


def decompose(layer: SoilLayer, temp_c: float, dt: float = DT_WEEKS) -> dict:
    """Five-pool RothC decomposition for one layer over dt years.

    Mutates layer C and N pools in-place.
    Returns a diagnostics dict with per-pool C loss and net N change.
    """
    modifier = (
        _temp_modifier(temp_c)
        * _moisture_modifier(layer.theta, layer.fc, layer.wp)
        * _ph_modifier(layer.ph)
    )

    clay_frac = _CLAY_FRAC.get(layer.texture, 0.20)
    co2_f, bio_f, hum_f = _partition_fracs(clay_frac)

    # ── Per-pool decomposition ──────────────────────────────────────────────
    d_dpm = min(K_DPM * modifier * layer.soc_dpm * dt, layer.soc_dpm)
    d_rpm = min(K_RPM * modifier * layer.soc_rpm * dt, layer.soc_rpm)
    d_bio = min(K_BIO * modifier * layer.soc_bio * dt, layer.soc_bio)
    d_hum = min(K_HUM * modifier * layer.soc_hum * dt, layer.soc_hum)
    # IOM: no decomposition

    total_d = d_dpm + d_rpm + d_bio + d_hum

    # Products: recycled into BIO and HUM pools
    new_bio = total_d * bio_f
    new_hum = total_d * hum_f

    layer.soc_dpm = max(0.0, layer.soc_dpm - d_dpm)
    layer.soc_rpm = max(0.0, layer.soc_rpm - d_rpm)
    layer.soc_bio = max(0.0, layer.soc_bio - d_bio + new_bio)
    layer.soc_hum = max(0.0, layer.soc_hum - d_hum + new_hum)
    # soc_iom unchanged

    # ── N mineralisation / immobilisation ──────────────────────────────────
    # Each decomposing pool either releases or consumes mineral N.
    # Net N = (N in substrate) − (N needed to build new microbial BIO)
    def _n_net(d_c: float, cn_pool: float) -> float:
        n_in_substrate = d_c / cn_pool           # N released from pool
        n_for_new_bio  = (d_c * bio_f) / CN_BIO  # N locked into new BIO
        return n_in_substrate - n_for_new_bio    # positive=mineralised, negative=immobilised

    n_net_tc = (
        _n_net(d_dpm, CN_DPM)
        + _n_net(d_rpm, CN_RPM)
        + _n_net(d_bio, CN_BIO)
        + _n_net(d_hum, CN_HUM)
    )
    n_net_kg = n_net_tc * 1000.0   # t C/ha → kg N/ha

    if n_net_kg >= 0.0:
        layer.n_nh4 += n_net_kg          # mineralisation → NH4
    else:
        immob = abs(n_net_kg)
        from_nh4 = min(immob, layer.n_nh4)
        layer.n_nh4 -= from_nh4
        from_no3 = min(immob - from_nh4, layer.n_no3)
        layer.n_no3 = max(0.0, layer.n_no3 - from_no3)

    return {
        "d_dpm": d_dpm, "d_rpm": d_rpm, "d_bio": d_bio, "d_hum": d_hum,
        "co2_t_ha": total_d * co2_f,
        "n_net_kg_ha": n_net_kg,
    }


def add_residue(layer: SoilLayer, c_input_t_ha: float,
                dpm_frac: float = 0.59, rpm_frac: float = 0.41) -> None:
    """Add fresh plant material to DPM and RPM pools.

    Default DPM:RPM = 59:41 is the RothC standard for arable crops.
    For woody inputs use 25:75.  Call once per layer per time step with
    the C input allocated to that layer by root-density weighting.
    """
    layer.soc_dpm += c_input_t_ha * dpm_frac
    layer.soc_rpm += c_input_t_ha * rpm_frac
