"""
Quantitative stress–yield response functions.

All penalty functions return a value in [0, 1] where:
  1.0 = no yield loss  (optimal)
  0.0 = complete crop failure

The 'severity' parameter is always normalised 0–1:
  0.0 = stress absent / negligible
  0.5 = moderate stress
  1.0 = maximum / lethal stress

Literature basis for penalty magnitudes
─────────────────────────────────────────────────────────────────────────────
Drought
  Daryanto et al. (2016) Meta-analysis:   maize 39.3 %, wheat 20.6 %
  Daryanto et al. (2017):                 rice   51.3 %
  Maleki et al. (2013):                   soybean 42 %
  Mafakheri et al. (2010):                chickpea 27–40 %
  Farooq et al. (2017):                   cowpea  68 %
  Zhao et al. (2020) / Tandfonline 2023:  wheat 50–60 % severe drought

Heat
  Zachariah et al. (2021) GRL:            wheat  8–27 % yield probability loss (IGP)
  Frontiers 2023 wheat heat review:        grain number –40 %, grain weight –25 %
                                            per °C above threshold ~2–5 %
  Kobayashi 2006 / Frontiers rice 2023:   rice blast severity ↑ with T

Waterlogging
  Setter & Waters (2003):                 wheat 20–30 % at anthesis
  IRRI data:                              rice tolerant; maize −30 to −50 %

Salinity
  FAO Irrigation & Drainage Paper 29:     threshold EC + linear slope model

Disease
  Savary et al. (2016) Food Security:     rice sheath blight 40 %; blast 20–30 %
  Crop Losses review (Ficke 2016):        wheat rust 10–70 %
  Banded Leaf Sheath Blight (BLSB):       maize up to 100 % in severe cases
  Fusarium head blight:                    wheat 20–30 % in epidemic years

Weeds
  Savary et al. (2016):                   rice weeds 0.7–1.5 t/ha absolute loss
  IGP wheat / P. minor:                   20–40 % loss uncontrolled
─────────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
import math


# ──────────────────────────────────────────────────────────────────────────────
#  HELPER UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def _linear_response(severity: float, max_penalty: float) -> float:
    """Simple linear penalty: penalty = severity × max_penalty."""
    return 1.0 - _clamp(severity) * max_penalty


def _sigmoid_response(severity: float, max_penalty: float,
                       k: float = 6.0) -> float:
    """
    Sigmoid (logistic) penalty — captures the accelerating nature of stress
    damage.  Low severity → small loss; high severity → rapid increase toward
    max_penalty.
    """
    if severity <= 0:
        return 1.0
    sig = 1.0 / (1.0 + math.exp(-k * (severity - 0.5)))
    # normalise so sigmoid(0)≈0 and sigmoid(1)≈max_penalty
    sig0 = 1.0 / (1.0 + math.exp(k * 0.5))
    sig1 = 1.0 / (1.0 + math.exp(-k * 0.5))
    normalised = (sig - sig0) / (sig1 - sig0)
    return 1.0 - _clamp(normalised * max_penalty, 0.0, max_penalty)


# ──────────────────────────────────────────────────────────────────────────────
#  ABIOTIC STRESS PENALTIES
# ──────────────────────────────────────────────────────────────────────────────

# Maximum yield penalties at severity = 1.0  (literature-calibrated per crop)
# format: { crop_key: max_fractional_penalty }

DROUGHT_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.58,   # Daryanto 2016 + Zhao 2020 (20.6–60 %)
    "rice":     0.65,   # Daryanto 2017 (50–90 % range; median ~65 %)
    "maize":    0.45,   # Daryanto 2016 (39.3 %) + reproductive stage
    "soybean":  0.42,   # Maleki 2013
    "chickpea": 0.35,   # Mafakheri 2010 (27–40 %)
    "mustard":  0.38,
    "cotton":   0.40,
    "tomato":   0.35,
    "potato":   0.32,
    "default":  0.38,
}

HEAT_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.55,   # Frontiers 2023; 8–27 % moderate; up to 55 % severe
    "rice":     0.40,   # terminal heat at anthesis
    "maize":    0.45,   # reproductive stage pollen failure
    "soybean":  0.35,
    "chickpea": 0.42,
    "mustard":  0.45,   # very sensitive at flowering
    "tomato":   0.50,   # pollen failure > 35 °C
    "potato":   0.48,   # tuber initiation impaired > 29 °C
    "default":  0.40,
}

WATERLOGGING_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.35,   # Setter & Waters 2003
    "rice":     0.05,   # tolerant (flooded crop)
    "maize":    0.48,   # very sensitive
    "soybean":  0.40,
    "chickpea": 0.50,
    "mustard":  0.35,
    "cotton":   0.38,
    "tomato":   0.45,
    "potato":   0.40,
    "default":  0.40,
}

SALINITY_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.40,   # moderately tolerant (ECe threshold 6 dS/m)
    "rice":     0.50,   # sensitive (ECe threshold 3 dS/m)
    "maize":    0.52,   # sensitive
    "soybean":  0.45,
    "chickpea": 0.55,
    "mustard":  0.38,   # moderate tolerance
    "cotton":   0.25,   # fairly tolerant
    "tomato":   0.48,
    "potato":   0.50,
    "default":  0.45,
}

COLD_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.20,   # vernalization crop; tolerant to mild cold
    "rice":     0.50,   # chilling at anthesis
    "maize":    0.55,   # seedling + anthesis sensitive
    "soybean":  0.40,
    "chickpea": 0.35,
    "mustard":  0.18,   # cool-season crop
    "tomato":   0.60,
    "potato":   0.35,
    "default":  0.38,
}

NITROGEN_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.45,
    "rice":     0.40,
    "maize":    0.50,   # highest N demand
    "soybean":  0.20,   # BNF partially compensates
    "chickpea": 0.15,   # legume
    "mustard":  0.42,
    "cotton":   0.38,
    "tomato":   0.35,
    "potato":   0.40,
    "default":  0.38,
}

PHOSPHORUS_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.28,
    "rice":     0.25,
    "maize":    0.30,
    "soybean":  0.25,
    "chickpea": 0.22,
    "mustard":  0.28,
    "default":  0.26,
}

POTASSIUM_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.20,
    "rice":     0.22,
    "maize":    0.20,
    "soybean":  0.18,
    "tomato":   0.25,
    "potato":   0.28,   # high K demand for tuber
    "default":  0.20,
}

ZINC_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.22,   # hidden hunger common in IGP alkaline soils
    "rice":     0.25,
    "maize":    0.20,
    "soybean":  0.18,
    "default":  0.20,
}


# ──────────────────────────────────────────────────────────────────────────────
#  BIOTIC STRESS PENALTIES
# ──────────────────────────────────────────────────────────────────────────────

DISEASE_MAX_PENALTY: dict[str, float] = {
    # WHEAT
    "wheat_yellow_rust":      0.60,  # epidemics → 40–70 % (Ficke 2016)
    "wheat_leaf_rust":        0.45,  # 10–45 %
    "wheat_stem_rust":        0.70,  # up to 70 % (Ug99 strains)
    "wheat_loose_smut":       0.30,
    "karnal_bunt":            0.20,  # quality/export loss
    "fusarium_head_blight":   0.35,  # + mycotoxin penalty
    # RICE
    "rice_blast":             0.45,  # neck blast → 20–30 % loss (Savary 2016)
    "rice_sheath_blight":     0.42,  # strongest yield reducer in tropical Asia
    "rice_bacterial_blight":  0.28,
    "rice_bph":               0.40,  # hopperburn
    "rice_false_smut":        0.12,
    # MAIZE
    "maize_blsb":             0.70,  # Rhizoctonia — up to 100 % in severe
    "maize_turcicum":         0.35,  # Northern leaf blight
    "maize_downy_mildew":     0.50,
    "maize_smut":             0.20,
    # SOYBEAN
    "soybean_yellow_mosaic":  0.45,  # YMV — most damaging virus
    "soybean_rust":           0.40,
    "charcoal_rot":           0.35,
    # CHICKPEA
    "chickpea_wilt":          0.55,
    "chickpea_ascochyta":     0.40,
    "chickpea_bgm":           0.30,  # Botrytis grey mould
    # MUSTARD
    "alternaria_blight":      0.35,
    "white_rust":             0.25,
    "sclerotinia":            0.40,
    # TOMATO
    "early_blight":           0.35,
    "late_blight":            0.55,
    "fusarium_wilt":          0.60,
    "bacterial_wilt":         0.70,
    # POTATO
    "potato_virus_y":         0.25,
    "potato_late_blight":     0.60,   # Phytophthora infestans — 30–80 % loss untreated
    "rhizoctonia_root_rot":   0.35,   # R. solani — stem canker / black scurf
    # WHEAT / CEREALS (European context)
    "septoria_tritici_blotch":0.50,   # Z. tritici — 5–50 % loss (Fones & Gurr 2015)
    "wheat_powdery_mildew":   0.28,   # Blumeria graminis — 5–30 % loss
    "wheat_eyespot":          0.25,   # Oculimacula spp. — lodging + yield 5–25 %
    "barley_net_blotch":      0.35,   # Pyrenophora teres — 10–40 %
    "barley_yellow_dwarf":    0.30,   # BYDV — virus vector-borne, 5–30 %
    # OILSEED RAPE / CANOLA
    "phoma_stem_canker":      0.35,   # Leptosphaeria maculans — 5–30 % (Murray 2012)
    "sclerotinia_rapeseed":   0.42,   # Sclerotinia sclerotiorum — up to 50 % in wet years
    "rapeseed_light_leaf_spot":0.25,  # Pyrenopeziza brassicae
    # SUGAR BEET
    "cercospora_leaf_spot":   0.45,   # Cercospora beticola — up to 50 % in severe years
    "beet_yellows_virus":     0.40,   # BMYV/BYV — aphid-vectored; major EU concern
    # EUROPE — additional keys (France, Poland, UK, Netherlands, Italy, Spain)
    "fusarium_crown_rot":     0.30,   # Fusarium culmorum/pseudograminearum — wheat crown rot
    "grape_downy_mildew":     0.55,   # Plasmopara viticola — major EU vine disease
    "grape_powdery_mildew":   0.50,   # Erysiphe necator — grapevine powdery mildew
    "pyrenophora_tritici":    0.28,   # Pyrenophora tritici-repentis — tan spot wheat
    "aphanomyces_root_rot":   0.35,   # Aphanomyces euteiches — pea root rot Poland/N.EU
    "clubroot":               0.45,   # Plasmodiophora brassicae — rapeseed/brassica
    "ramularia_leaf_spot":    0.30,   # Ramularia collo-cygni — barley (UK/Scotland primary)
    "fusarium_dry_rot_potato":0.30,   # Fusarium sulphureum — potato dry rot Netherlands
    "nematode_potato":        0.40,   # Globodera pallida/rostochiensis — potato cyst nematode
    "xylella_fastidiosa":     0.80,   # Xylella fastidiosa — olive/vine sudden death (Italy/Spain)
    "tuta_absoluta":          0.45,   # Tuta absoluta — tomato/potato leafminer moth S. Europe
    "default":                0.30,
}

WEED_MAX_PENALTY: dict[str, float] = {
    "wheat":    0.40,   # P. minor uncontrolled — 20–40 % loss (IGP studies)
    "rice":     0.48,   # Savary 2016: 0.7–1.5 t/ha absolute
    "maize":    0.45,
    "soybean":  0.40,
    "chickpea": 0.35,
    "mustard":  0.38,
    "default":  0.38,
}

INSECT_MAX_PENALTY: dict[str, float] = {
    "rice":        0.30,   # stem borer, BPH, leaf folder
    "wheat":       0.20,   # aphids, termites; 0.25 with BYDV losses
    "maize":       0.35,   # FAW (fall armyworm) — up to 60 % severe
    "soybean":     0.28,
    "chickpea":    0.35,   # pod borer
    "cotton":      0.40,   # bollworm complex
    "tomato":      0.38,
    "potato":      0.32,   # Colorado potato beetle + wireworm
    "rapeseed":    0.30,   # pollen beetle + flea beetle + cabbage root fly
    "barley":      0.22,   # aphids, BYDV vectors
    "sugarbeet":   0.35,   # beet aphid (BYD virus); mite; nematode
    "sunflower":   0.25,
    "default":     0.28,
}


# ──────────────────────────────────────────────────────────────────────────────
#  PENALTY CALCULATION FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def drought_penalty(crop: str, severity: float,
                    variety_modifier: float = 1.0) -> float:
    """
    Drought yield penalty using sigmoid response.
    severity: 0 (none) → 1 (wilting/crop failure).
    """
    max_p = DROUGHT_MAX_PENALTY.get(crop, DROUGHT_MAX_PENALTY["default"])
    return _sigmoid_response(severity, max_p * variety_modifier)


def heat_penalty(crop: str, severity: float,
                 variety_modifier: float = 1.0) -> float:
    """
    Heat stress penalty.  Primarily affects reproductive stage (pollen sterility,
    grain filling rate).  Uses sigmoid — rapid increase above moderate severity.
    """
    max_p = HEAT_MAX_PENALTY.get(crop, HEAT_MAX_PENALTY["default"])
    return _sigmoid_response(severity, max_p * variety_modifier)


def waterlogging_penalty(crop: str, severity: float,
                          variety_modifier: float = 1.0) -> float:
    """
    Waterlogging penalty.  Linear (root anoxia increases proportionally
    with duration × depth).
    """
    max_p = WATERLOGGING_MAX_PENALTY.get(
        crop, WATERLOGGING_MAX_PENALTY["default"])
    return _linear_response(severity, max_p * variety_modifier)


def salinity_penalty(crop: str, severity: float,
                     variety_modifier: float = 1.0) -> float:
    """
    Salinity penalty based on FAO-29 linear yield-loss model above threshold.
    severity maps 0 = EC at threshold, 1 = EC at 100 % yield loss.
    """
    max_p = SALINITY_MAX_PENALTY.get(crop, SALINITY_MAX_PENALTY["default"])
    return _linear_response(severity, max_p * variety_modifier)


def cold_stress_penalty(crop: str, severity: float,
                         variety_modifier: float = 1.0) -> float:
    max_p = COLD_MAX_PENALTY.get(crop, COLD_MAX_PENALTY["default"])
    return _linear_response(severity, max_p * variety_modifier)


def nitrogen_penalty(crop: str, severity: float,
                      variety_modifier: float = 1.0) -> float:
    """
    Nitrogen deficiency penalty.  Uses sigmoid — initial deficiency has small
    impact, severe deficiency causes steep decline.
    """
    max_p = NITROGEN_MAX_PENALTY.get(crop, NITROGEN_MAX_PENALTY["default"])
    return _sigmoid_response(severity, max_p * variety_modifier, k=5.0)


def phosphorus_penalty(crop: str, severity: float,
                        variety_modifier: float = 1.0) -> float:
    max_p = PHOSPHORUS_MAX_PENALTY.get(
        crop, PHOSPHORUS_MAX_PENALTY["default"])
    return _linear_response(severity, max_p * variety_modifier)


def potassium_penalty(crop: str, severity: float,
                       variety_modifier: float = 1.0) -> float:
    max_p = POTASSIUM_MAX_PENALTY.get(crop, POTASSIUM_MAX_PENALTY["default"])
    return _linear_response(severity, max_p * variety_modifier)


def zinc_penalty(crop: str, severity: float) -> float:
    max_p = ZINC_MAX_PENALTY.get(crop, ZINC_MAX_PENALTY["default"])
    return _linear_response(severity, max_p)


def disease_penalty(disease_key: str, severity: float,
                     variety_resistance: float = 1.0) -> float:
    """
    Disease yield penalty.
    variety_resistance: 0 = immune, 1 = fully susceptible.
    Effective penalty = literature max × variety_resistance × severity.
    """
    max_p = DISEASE_MAX_PENALTY.get(disease_key, DISEASE_MAX_PENALTY["default"])
    effective_max = max_p * variety_resistance
    return _sigmoid_response(severity, effective_max, k=5.5)


def weed_penalty(crop: str, severity: float,
                  herbicide_resistance_factor: float = 0.0) -> float:
    """
    Weed competition penalty.
    herbicide_resistance_factor: additional penalty multiplier when
    herbicide resistance is present (0 = no resistance, 1 = full resistance).
    Resistant weeds cannot be controlled chemically — modelled as 30 %
    additional yield exposure on top of the base weed pressure.
    """
    max_p = WEED_MAX_PENALTY.get(crop, WEED_MAX_PENALTY["default"])
    # resistance amplifies weed pressure (harder to control)
    effective_severity = _clamp(severity * (1.0 + 0.3 * herbicide_resistance_factor))
    return _sigmoid_response(effective_severity, max_p, k=5.0)


def insect_penalty(crop: str, severity: float) -> float:
    max_p = INSECT_MAX_PENALTY.get(crop, INSECT_MAX_PENALTY["default"])
    return _sigmoid_response(severity, max_p, k=4.5)


# ──────────────────────────────────────────────────────────────────────────────
#  COMBINED BIOTIC STRESS
# ──────────────────────────────────────────────────────────────────────────────

def combined_biotic_factor(
    crop: str,
    disease_severities: dict[str, float],   # {disease_key: 0–1}
    disease_resistances: dict[str, float],  # {disease_key: 0–1} from variety
    weed_severity: float,
    herbicide_resistance_factor: float,
    insect_severity: float,
) -> float:
    """
    Multiplicative combination of all biotic stress factors.
    Returns combined factor in [0, 1].
    """
    factor = 1.0

    for disease_key, sev in disease_severities.items():
        resistance = disease_resistances.get(disease_key, 1.0)
        factor *= disease_penalty(disease_key, sev, resistance)

    factor *= weed_penalty(crop, weed_severity, herbicide_resistance_factor)
    factor *= insect_penalty(crop, insect_severity)

    return _clamp(factor, 0.0, 1.0)


# ──────────────────────────────────────────────────────────────────────────────
#  ENVIRONMENT–DISEASE INTERACTION MODIFIERS
# ──────────────────────────────────────────────────────────────────────────────
# Each entry: (temp_lo, temp_hi, humidity_threshold) → disease_multiplier
# These are applied to modify effective disease severity based on real weather.
# Source: PMC 5967643, PMC 10153038, Nature Climate Change 2021

DISEASE_ENVIRONMENT_MODIFIERS: dict[str, dict] = {
    "wheat_yellow_rust": {
        "optimal_temp_range": (8, 15),   # °C — cooler
        "high_humidity_boost": 1.35,     # RH > 85 %
        "low_humidity_suppressor": 0.60,
        "temp_above_20_suppressor": 0.50, # race shift but old races suppressed
        "description": "Favoured by cool-moist conditions 8–15 °C; "
                        "suppressed above 25 °C.",
    },
    "wheat_leaf_rust": {
        "optimal_temp_range": (15, 22),
        "high_humidity_boost": 1.30,
        "low_humidity_suppressor": 0.65,
        "temp_above_28_suppressor": 0.70,
        "description": "Moderate temperature + high humidity; "
                        "globally most common wheat rust.",
    },
    "wheat_stem_rust": {
        "optimal_temp_range": (18, 28),
        "high_humidity_boost": 1.40,
        "low_humidity_suppressor": 0.55,
        "description": "Warm + humid; Ug99 highly virulent.",
    },
    "rice_blast": {
        "optimal_temp_range": (24, 28),
        "high_humidity_boost": 1.50,
        "low_humidity_suppressor": 0.50,
        "night_dew_boost": 1.25,
        "description": "Warm nights + leaf wetness → spore release. "
                        "Severity ↑ with elevated CO₂ (Kobayashi 2006).",
    },
    "rice_sheath_blight": {
        "optimal_temp_range": (28, 32),
        "high_humidity_boost": 1.40,
        "high_density_boost": 1.30,      # dense canopy
        "description": "Warm-humid + dense canopy. "
                        "Strongest yield reducer in tropical Asia (Savary 2016).",
    },
    "rice_bacterial_blight": {
        "optimal_temp_range": (25, 34),
        "high_humidity_boost": 1.35,
        "wind_damage_boost": 1.25,       # cyclone / storm entry
        "description": "Hot + humid + flooding or wind damage.",
    },
    "maize_blsb": {
        "optimal_temp_range": (26, 30),
        "high_humidity_boost": 1.60,    # critical importance
        "low_humidity_suppressor": 0.40,
        "description": "Rhizoctonia solani — peak at 28 °C humid "
                        "(Springer 2015). Can cause 100 % loss.",
    },
    "maize_turcicum": {
        "optimal_temp_range": (18, 27),
        "high_humidity_boost": 1.30,
        "description": "Exserohilum turcicum — cooler humid conditions.",
    },
    "late_blight": {
        "optimal_temp_range": (10, 20),
        "high_humidity_boost": 1.70,   # Phytophthora infestans
        "low_humidity_suppressor": 0.30,
        "description": "Phytophthora infestans — the original famine pathogen. "
                        "Cool-moist conditions. Climate warming shifts distribution.",
    },
    "fusarium_head_blight": {
        "optimal_temp_range": (25, 30),  # F. graminearum (warm) replacing
        "high_humidity_boost": 1.55,     # F. culmorum (cool)
        "description": "Warm-moist at anthesis. Produces DON mycotoxin. "
                        "F. graminearum expanding poleward (Nature Climate Change).",
    },
    "soybean_yellow_mosaic": {
        "optimal_temp_range": (25, 33),
        "high_humidity_boost": 1.20,    # indirectly via whitefly vector
        "description": "YMV transmitted by whitefly Bemisia tabaci. "
                        "Hot-dry conditions promote whitefly populations.",
    },
    "chickpea_wilt": {
        "optimal_temp_range": (18, 25),
        "high_humidity_boost": 1.40,
        "description": "Fusarium oxysporum f.sp. ciceris — warm-moist soils.",
    },
    "alternaria_blight": {
        "optimal_temp_range": (20, 28),
        "high_humidity_boost": 1.35,
        "description": "Alternaria brassicae on mustard — warm + humid.",
    },
    "grape_downy_mildew": {
        "optimal_temp_range": (15, 25),
        "high_humidity_boost": 1.65,
        "low_humidity_suppressor": 0.25,
        "description": "Plasmopara viticola — cool-wet springs + rain during flowering. "
                        "Primary yield threat in French/Italian/Spanish vineyards.",
    },
    "grape_powdery_mildew": {
        "optimal_temp_range": (18, 28),
        "high_humidity_boost": 1.25,
        "low_humidity_suppressor": 0.55,
        "description": "Erysiphe necator — unlike downy mildew, thrives in warm-dry conditions.",
    },
    "clubroot": {
        "optimal_temp_range": (16, 24),
        "high_humidity_boost": 1.50,
        "low_humidity_suppressor": 0.40,
        "description": "Plasmodiophora brassicae — moist cool acid soils; "
                        "soil pH < 6.5 significantly increases risk.",
    },
    "ramularia_leaf_spot": {
        "optimal_temp_range": (10, 18),
        "high_humidity_boost": 1.45,
        "low_humidity_suppressor": 0.50,
        "description": "Ramularia collo-cygni — cool-humid maritime conditions; "
                        "Scotland worst affected in EU (Walters et al. 2008).",
    },
    "xylella_fastidiosa": {
        "optimal_temp_range": (20, 32),
        "high_humidity_boost": 1.10,
        "low_humidity_suppressor": 0.80,
        "description": "Xylella fastidiosa — warm/dry conditions favour vector "
                        "(Philaenus spumarius); outbreak in Apulia 2013– catastrophic.",
    },
    "tuta_absoluta": {
        "optimal_temp_range": (22, 30),
        "high_humidity_boost": 1.15,
        "description": "Tuta absoluta — warm conditions; year-round in S. Europe greenhouses.",
    },
    "pyrenophora_tritici": {
        "optimal_temp_range": (15, 25),
        "high_humidity_boost": 1.40,
        "low_humidity_suppressor": 0.55,
        "description": "Pyrenophora tritici-repentis (tan spot) — warm + humid at flag leaf stage.",
    },
}


def environment_disease_modifier(
    disease_key: str,
    mean_temp_c: float,
    relative_humidity_pct: float,
) -> float:
    """
    Returns a multiplier (0.5–1.7) that adjusts effective disease severity
    based on environmental conditions.  1.0 = neutral.
    """
    info = DISEASE_ENVIRONMENT_MODIFIERS.get(disease_key)
    if not info:
        return 1.0

    modifier = 1.0
    lo, hi = info["optimal_temp_range"]

    # Temperature penalty if outside optimal window
    if mean_temp_c < lo:
        deficit = (lo - mean_temp_c) / lo
        modifier *= max(0.4, 1.0 - deficit * 0.5)
    elif mean_temp_c > hi:
        excess = (mean_temp_c - hi) / hi
        # check for specific suppressor
        sup_key = [k for k in info if "suppressor" in k and
                   "temp_above" in k]
        if sup_key:
            modifier *= info[sup_key[0]]
        else:
            modifier *= max(0.5, 1.0 - excess * 0.4)

    # Humidity boost / suppressor
    if relative_humidity_pct >= 80:
        modifier *= info.get("high_humidity_boost", 1.0)
    elif relative_humidity_pct < 55:
        modifier *= info.get("low_humidity_suppressor", 1.0)

    return _clamp(modifier, 0.3, 2.0)
