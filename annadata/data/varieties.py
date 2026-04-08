"""
Crop variety database for Annadata.

Sources:
  - ICAR Annual Reports 2022–2024
  - CIMMYT South Asia variety catalogues
  - DWR (Directorate of Wheat Research) variety release notifications
  - NRRI (National Rice Research Institute) variety descriptors
  - DUS testing guidelines (PPV&FRA)
  - FAO/IRRI crop descriptor sheets
  - Zachariah et al. (2021) GRL — wheat heat stress
  - Daryanto et al. (2016, 2017) — drought yield loss benchmarks
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VarietyProfile:
    """
    Complete agronomic and stress-tolerance profile for a named variety.

    Stress modifiers are multipliers on the base penalty from the stress
    response curves (stress_responses.py).  A value of 0.60 means the
    variety reduces the stress penalty to 60 % of what a standard/susceptible
    variety would experience.  Values > 1.0 indicate hypersensitivity.

    All yield potential values are in t/ha under optimal management.
    """

    # ── identity ─────────────────────────────────────────────────────────
    key: str
    name: str
    crop: str
    release_year: Optional[int]
    released_by: str              # e.g. "IARI New Delhi", "PAU Ludhiana"
    notified_states: list[str]    # states where officially recommended

    # ── agronomic baseline ───────────────────────────────────────────────
    yield_potential_t_ha: float   # under fully optimal conditions
    season_days: int              # days from sowing to maturity
    plant_height_cm: float
    lodging_resistance: float     # 0–1  (1 = very resistant)

    # ── temperature windows ──────────────────────────────────────────────
    optimal_temp_min: float       # °C
    optimal_temp_max: float       # °C
    critical_temp_high: float     # °C — sterility / pollen failure threshold
    critical_temp_low: float      # °C — chilling damage threshold

    # ── stress tolerance modifiers (0–1 scale; lower = more tolerant) ───
    heat_stress_modifier: float       = 1.0   # 1.0 = normal susceptibility
    drought_stress_modifier: float    = 1.0
    waterlogging_modifier: float      = 1.0
    salinity_modifier: float          = 1.0
    cold_stress_modifier: float       = 1.0

    # ── disease resistance (0 = immune, 1 = fully susceptible) ──────────
    # Each key matches a disease key in diseases.py
    disease_resistance: dict[str, float] = field(default_factory=dict)

    # ── nutrient use efficiency modifiers ───────────────────────────────
    nue_modifier: float           = 1.0   # nitrogen use efficiency
    pue_modifier: float           = 1.0   # phosphorus
    kue_modifier: float           = 1.0   # potassium

    # ── notes & pedigree ────────────────────────────────────────────────
    notes: str = ""


# ============================================================
#  WHEAT (Triticum aestivum)
# ============================================================
WHEAT_VARIETIES: dict[str, VarietyProfile] = {

    "hd_2967": VarietyProfile(
        key="hd_2967", name="HD 2967", crop="wheat",
        release_year=2011, released_by="IARI New Delhi",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Bihar",
                         "Rajasthan", "Madhya Pradesh"],
        yield_potential_t_ha=5.8, season_days=120, plant_height_cm=92,
        lodging_resistance=0.65,
        optimal_temp_min=12, optimal_temp_max=22,
        critical_temp_high=31, critical_temp_low=2,
        heat_stress_modifier=1.0, drought_stress_modifier=1.0,
        disease_resistance={
            "wheat_yellow_rust": 0.35,
            "wheat_leaf_rust":   0.45,
            "wheat_stem_rust":   0.50,
            "wheat_loose_smut":  0.40,
            "karnal_bunt":       0.55,
        },
        notes="Most widely grown wheat variety in NW India. Standard susceptibility benchmark.",
    ),

    "hd_3385": VarietyProfile(
        key="hd_3385", name="HD 3385", crop="wheat",
        release_year=2019, released_by="IARI New Delhi",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Bihar",
                         "Rajasthan", "Madhya Pradesh"],
        yield_potential_t_ha=6.1, season_days=112, plant_height_cm=88,
        lodging_resistance=0.72,
        optimal_temp_min=12, optimal_temp_max=25,
        critical_temp_high=35, critical_temp_low=2,
        heat_stress_modifier=0.55,   # ~45 % reduction in heat penalty
        drought_stress_modifier=0.90,
        disease_resistance={
            "wheat_yellow_rust": 0.20,
            "wheat_leaf_rust":   0.30,
            "wheat_stem_rust":   0.35,
            "wheat_loose_smut":  0.30,
            "karnal_bunt":       0.40,
            "fusarium_head_blight": 0.60,
        },
        notes="Heat-tolerant variety bred for late-sown conditions. "
              "Carries Lr24+Lr28 for leaf rust, Yr17 for yellow rust. "
              "Critical temp raised to 35 °C vs 31 °C for HD-2967.",
    ),

    "dbw_187": VarietyProfile(
        key="dbw_187", name="DBW 187", crop="wheat",
        release_year=2020, released_by="DWR Karnal",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Bihar",
                         "Uttarakhand", "Himachal Pradesh"],
        yield_potential_t_ha=6.5, season_days=122, plant_height_cm=91,
        lodging_resistance=0.75,
        optimal_temp_min=11, optimal_temp_max=23,
        critical_temp_high=32, critical_temp_low=1,
        heat_stress_modifier=0.75, drought_stress_modifier=0.70,
        disease_resistance={
            "wheat_yellow_rust": 0.15,
            "wheat_leaf_rust":   0.25,
            "wheat_stem_rust":   0.30,
            "karnal_bunt":       0.30,
            "fusarium_head_blight": 0.55,
        },
        nue_modifier=0.88,
        notes="High yield + drought tolerance. Carries Lr28, Sr38, Yr17. "
              "NUE improved — 12 % lower N demand for same yield.",
    ),

    "pbw_343": VarietyProfile(
        key="pbw_343", name="PBW 343", crop="wheat",
        release_year=1995, released_by="PAU Ludhiana",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh"],
        yield_potential_t_ha=5.5, season_days=118, plant_height_cm=90,
        lodging_resistance=0.60,
        optimal_temp_min=12, optimal_temp_max=22,
        critical_temp_high=31, critical_temp_low=2,
        heat_stress_modifier=1.05, drought_stress_modifier=0.95,
        disease_resistance={
            "wheat_yellow_rust": 0.80,  # lost resistance — race shifts post-2005
            "wheat_leaf_rust":   0.55,
            "wheat_stem_rust":   0.45,
        },
        notes="Legacy variety; yellow rust resistance largely overcome by new races.",
    ),

    "k_307": VarietyProfile(
        key="k_307", name="K 307", crop="wheat",
        release_year=1996, released_by="GBPUAT Pantnagar",
        notified_states=["Uttar Pradesh", "Bihar", "Jharkhand"],
        yield_potential_t_ha=5.2, season_days=125, plant_height_cm=95,
        lodging_resistance=0.55,
        optimal_temp_min=11, optimal_temp_max=21,
        critical_temp_high=30, critical_temp_low=1,
        heat_stress_modifier=1.10, drought_stress_modifier=1.05,
        disease_resistance={
            "wheat_yellow_rust": 0.45,
            "wheat_leaf_rust":   0.50,
        },
        notes="Adapted to eastern UP / Bihar. Longer season, tall.",
    ),

    "hd_3226": VarietyProfile(
        key="hd_3226", name="HD 3226 (Pusa Wheat 3226)", crop="wheat",
        release_year=2016, released_by="IARI New Delhi",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Rajasthan"],
        yield_potential_t_ha=5.9, season_days=120, plant_height_cm=89,
        lodging_resistance=0.70,
        optimal_temp_min=12, optimal_temp_max=23,
        critical_temp_high=33, critical_temp_low=2,
        heat_stress_modifier=0.80, drought_stress_modifier=0.85,
        disease_resistance={
            "wheat_yellow_rust": 0.25,
            "wheat_leaf_rust":   0.30,
            "wheat_stem_rust":   0.35,
            "karnal_bunt":       0.40,
        },
        notes="Improved heat + disease package over HD 2967.",
    ),

    "raj_4120": VarietyProfile(
        key="raj_4120", name="Raj 4120", crop="wheat",
        release_year=2005, released_by="SKRAU Bikaner",
        notified_states=["Rajasthan", "Madhya Pradesh", "Gujarat"],
        yield_potential_t_ha=4.9, season_days=110, plant_height_cm=85,
        lodging_resistance=0.70,
        optimal_temp_min=13, optimal_temp_max=24,
        critical_temp_high=33, critical_temp_low=3,
        heat_stress_modifier=0.72, drought_stress_modifier=0.65,
        salinity_modifier=0.75,
        disease_resistance={
            "wheat_leaf_rust": 0.40,
            "wheat_yellow_rust": 0.45,
        },
        notes="Drought + heat tolerant for arid Rajasthan conditions. "
              "Moderate salinity tolerance.",
    ),

    "dbw_303": VarietyProfile(
        key="dbw_303", name="DBW 303", crop="wheat",
        release_year=2023, released_by="DWR Karnal",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Bihar"],
        yield_potential_t_ha=7.0, season_days=120, plant_height_cm=87,
        lodging_resistance=0.80,
        optimal_temp_min=11, optimal_temp_max=24,
        critical_temp_high=35, critical_temp_low=1,
        heat_stress_modifier=0.50, drought_stress_modifier=0.65,
        disease_resistance={
            "wheat_yellow_rust":    0.10,
            "wheat_leaf_rust":      0.15,
            "wheat_stem_rust":      0.20,
            "karnal_bunt":          0.20,
            "fusarium_head_blight": 0.45,
        },
        nue_modifier=0.85,
        notes="Latest DWR high-yielding heat-tolerant variety (2023 release). "
              "Excellent rust package. Recommended for early + timely sowing.",
    ),
}


# ============================================================
#  RICE (Oryza sativa)
# ============================================================
RICE_VARIETIES: dict[str, VarietyProfile] = {

    "pusa_44": VarietyProfile(
        key="pusa_44", name="Pusa 44", crop="rice",
        release_year=1994, released_by="IARI New Delhi",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh"],
        yield_potential_t_ha=9.0, season_days=155, plant_height_cm=105,
        lodging_resistance=0.50,
        optimal_temp_min=22, optimal_temp_max=32,
        critical_temp_high=38, critical_temp_low=15,
        drought_stress_modifier=1.20,  # very sensitive to drought
        waterlogging_modifier=0.80,
        disease_resistance={
            "rice_blast":           0.75,
            "rice_bph":             0.70,
            "rice_sheath_blight":   0.80,
            "rice_bacterial_blight":0.60,
        },
        notes="Highest-yielding long-duration variety in NW India. "
              "Very drought-sensitive. High water footprint.",
    ),

    "mtu_1010": VarietyProfile(
        key="mtu_1010", name="MTU 1010", crop="rice",
        release_year=1995, released_by="ANGRAU Guntur",
        notified_states=["Andhra Pradesh", "Telangana", "Karnataka", "Tamil Nadu"],
        yield_potential_t_ha=7.5, season_days=120, plant_height_cm=88,
        lodging_resistance=0.65,
        optimal_temp_min=23, optimal_temp_max=33,
        critical_temp_high=38, critical_temp_low=18,
        drought_stress_modifier=1.10,
        disease_resistance={
            "rice_blast":           0.55,
            "rice_sheath_blight":   0.65,
            "rice_bph":             0.45,
            "rice_bacterial_blight":0.50,
        },
        notes="Dominant variety in Andhra/Telangana. Medium blast resistance.",
    ),

    "sahbhagi_dhan": VarietyProfile(
        key="sahbhagi_dhan", name="Sahbhagi Dhan", crop="rice",
        release_year=2010, released_by="ICAR-NRRI Cuttack",
        notified_states=["Jharkhand", "Odisha", "Chhattisgarh", "Bihar",
                         "Uttar Pradesh", "Assam"],
        yield_potential_t_ha=5.5, season_days=110, plant_height_cm=85,
        lodging_resistance=0.72,
        optimal_temp_min=22, optimal_temp_max=32,
        critical_temp_high=37, critical_temp_low=17,
        drought_stress_modifier=0.45,  # very drought tolerant (Sub1 + DRO1)
        disease_resistance={
            "rice_blast":           0.50,
            "rice_bacterial_blight":0.45,
        },
        notes="IARI-IRRI joint development. Carries Dro1 gene for deep rooting "
              "under drought. 20-40 % better yield than check under rainfed drought. "
              "Adopted by 1.5 M ha in eastern India.",
    ),

    "swarna_sub1": VarietyProfile(
        key="swarna_sub1", name="Swarna Sub1", crop="rice",
        release_year=2009, released_by="ICAR-NRRI / IRRI",
        notified_states=["Odisha", "West Bengal", "Andhra Pradesh",
                         "Bihar", "Uttar Pradesh", "Assam"],
        yield_potential_t_ha=6.5, season_days=145, plant_height_cm=100,
        lodging_resistance=0.60,
        optimal_temp_min=22, optimal_temp_max=33,
        critical_temp_high=38, critical_temp_low=16,
        waterlogging_modifier=0.30,  # sub-mergence tolerant (Sub1 gene)
        drought_stress_modifier=1.05,
        disease_resistance={
            "rice_blast":           0.60,
            "rice_sheath_blight":   0.70,
            "rice_bacterial_blight":0.50,
            "rice_bph":             0.55,
        },
        notes="Swarna + Sub1 gene — tolerates 15 days complete submergence. "
              "Critical for flood-prone Eastern India.",
    ),

    "drr_dhan_44": VarietyProfile(
        key="drr_dhan_44", name="DRR Dhan 44", crop="rice",
        release_year=2016, released_by="ICAR-NRRI Cuttack",
        notified_states=["Andhra Pradesh", "Telangana", "Karnataka",
                         "Odisha", "Chhattisgarh"],
        yield_potential_t_ha=7.0, season_days=125, plant_height_cm=90,
        lodging_resistance=0.68,
        optimal_temp_min=22, optimal_temp_max=32,
        critical_temp_high=37, critical_temp_low=17,
        drought_stress_modifier=0.75,
        disease_resistance={
            "rice_blast":           0.20,  # excellent blast resistance
            "rice_sheath_blight":   0.50,
            "rice_bacterial_blight":0.35,
            "rice_bph":             0.40,
        },
        notes="Bred specifically for blast resistance. Carries Pi54, Pita2 genes.",
    ),

    "pusa_basmati_1121": VarietyProfile(
        key="pusa_basmati_1121", name="Pusa Basmati 1121", crop="rice",
        release_year=2003, released_by="IARI New Delhi",
        notified_states=["Punjab", "Haryana", "Uttar Pradesh", "Uttarakhand",
                         "Delhi"],
        yield_potential_t_ha=5.0, season_days=140, plant_height_cm=115,
        lodging_resistance=0.40,
        optimal_temp_min=22, optimal_temp_max=30,
        critical_temp_high=36, critical_temp_low=17,
        heat_stress_modifier=1.15,  # sensitive to high temp at anthesis
        drought_stress_modifier=1.20,
        disease_resistance={
            "rice_blast":           0.65,
            "rice_bacterial_blight":0.55,
            "rice_sheath_blight":   0.70,
        },
        notes="Premium basmati export variety. Very susceptible to lodging. "
              "Sensitive to heat at anthesis — grain set affected.",
    ),

    "ir_64": VarietyProfile(
        key="ir_64", name="IR 64", crop="rice",
        release_year=1985, released_by="IRRI Philippines",
        notified_states=["Multiple states"],
        yield_potential_t_ha=6.0, season_days=115, plant_height_cm=85,
        lodging_resistance=0.70,
        optimal_temp_min=22, optimal_temp_max=32,
        critical_temp_high=37, critical_temp_low=17,
        drought_stress_modifier=1.00,
        disease_resistance={
            "rice_blast":           0.50,
            "rice_bph":             0.35,
            "rice_bacterial_blight":0.40,
        },
        notes="International benchmark variety for indica type.",
    ),
}


# ============================================================
#  MAIZE (Zea mays)
# ============================================================
MAIZE_VARIETIES: dict[str, VarietyProfile] = {

    "dhm_117": VarietyProfile(
        key="dhm_117", name="DHM 117", crop="maize",
        release_year=2008, released_by="PAU Ludhiana",
        notified_states=["Punjab", "Haryana", "Himachal Pradesh",
                         "Jammu & Kashmir"],
        yield_potential_t_ha=9.5, season_days=95, plant_height_cm=195,
        lodging_resistance=0.70,
        optimal_temp_min=18, optimal_temp_max=30,
        critical_temp_high=38, critical_temp_low=10,
        heat_stress_modifier=0.90, drought_stress_modifier=0.95,
        disease_resistance={
            "maize_blsb":       0.50,
            "maize_turcicum":   0.45,
            "maize_downy_mildew": 0.55,
        },
        notes="High-yielding hybrid for NW plains.",
    ),

    "hqpm_1": VarietyProfile(
        key="hqpm_1", name="HQPM 1 (QPM)", crop="maize",
        release_year=2001, released_by="ICAR-IIMR Ludhiana",
        notified_states=["Punjab", "Haryana", "Uttarakhand", "Bihar",
                         "Jharkhand", "Odisha"],
        yield_potential_t_ha=7.5, season_days=90, plant_height_cm=180,
        lodging_resistance=0.65,
        optimal_temp_min=18, optimal_temp_max=30,
        critical_temp_high=37, critical_temp_low=10,
        drought_stress_modifier=0.90,
        disease_resistance={
            "maize_blsb":       0.55,
            "maize_turcicum":   0.50,
        },
        notes="Quality Protein Maize — 2x tryptophan/lysine. "
              "Nutrition security variety.",
    ),

    "vivek_qpm_9": VarietyProfile(
        key="vivek_qpm_9", name="Vivek QPM 9", crop="maize",
        release_year=2007, released_by="VPKAS Almora",
        notified_states=["Uttarakhand", "Himachal Pradesh", "NE India",
                         "Bihar", "Jharkhand"],
        yield_potential_t_ha=6.5, season_days=85, plant_height_cm=165,
        lodging_resistance=0.72,
        optimal_temp_min=16, optimal_temp_max=28,
        critical_temp_high=35, critical_temp_low=8,
        cold_stress_modifier=0.65,  # adapted to hill areas
        drought_stress_modifier=0.85,
        disease_resistance={
            "maize_blsb":       0.45,
            "maize_downy_mildew": 0.40,
        },
        notes="Hill-adapted QPM variety. Cold tolerant — can be grown at 1500m.",
    ),

    "nk_6240": VarietyProfile(
        key="nk_6240", name="NK 6240 (Syngenta)", crop="maize",
        release_year=2010, released_by="Syngenta India",
        notified_states=["Karnataka", "Tamil Nadu", "Andhra Pradesh",
                         "Telangana", "Maharashtra"],
        yield_potential_t_ha=10.0, season_days=100, plant_height_cm=200,
        lodging_resistance=0.75,
        optimal_temp_min=20, optimal_temp_max=32,
        critical_temp_high=40, critical_temp_low=12,
        heat_stress_modifier=0.80,
        disease_resistance={
            "maize_blsb":       0.40,
            "maize_turcicum":   0.35,
        },
        notes="High-performance commercial hybrid for peninsular India.",
    ),
}


# ============================================================
#  SOYBEAN (Glycine max)
# ============================================================
SOYBEAN_VARIETIES: dict[str, VarietyProfile] = {

    "js_335": VarietyProfile(
        key="js_335", name="JS 335", crop="soybean",
        release_year=1994, released_by="JNKVV Jabalpur",
        notified_states=["Madhya Pradesh", "Rajasthan", "Maharashtra",
                         "Karnataka"],
        yield_potential_t_ha=3.2, season_days=95, plant_height_cm=60,
        lodging_resistance=0.65,
        optimal_temp_min=22, optimal_temp_max=30,
        critical_temp_high=37, critical_temp_low=14,
        disease_resistance={
            "soybean_yellow_mosaic": 0.55,
            "soybean_rust":          0.60,
            "charcoal_rot":          0.65,
        },
        notes="Dominant soybean variety in central India for 30 years.",
    ),

    "macs_1407": VarietyProfile(
        key="macs_1407", name="MACS 1407", crop="soybean",
        release_year=2020, released_by="ARI Pune",
        notified_states=["Maharashtra", "Madhya Pradesh", "Karnataka",
                         "Andhra Pradesh"],
        yield_potential_t_ha=3.9, season_days=104, plant_height_cm=58,
        lodging_resistance=0.80,
        optimal_temp_min=22, optimal_temp_max=31,
        critical_temp_high=38, critical_temp_low=15,
        drought_stress_modifier=0.70,
        heat_stress_modifier=0.80,
        disease_resistance={
            "soybean_yellow_mosaic": 0.30,
            "soybean_rust":          0.40,
            "charcoal_rot":          0.45,
        },
        nue_modifier=0.90,
        notes="New drought + heat tolerant variety. Excellent YMV resistance. "
              "ICAR recommendation for climate-resilient soybean.",
    ),

    "nrc_7": VarietyProfile(
        key="nrc_7", name="NRC 7", crop="soybean",
        release_year=2003, released_by="ICAR-IISR Indore",
        notified_states=["Madhya Pradesh", "Maharashtra", "Rajasthan"],
        yield_potential_t_ha=2.9, season_days=88, plant_height_cm=55,
        lodging_resistance=0.70,
        optimal_temp_min=22, optimal_temp_max=30,
        critical_temp_high=36, critical_temp_low=14,
        drought_stress_modifier=0.90,
        disease_resistance={
            "soybean_yellow_mosaic": 0.45,
        },
        notes="Early-maturing variety — escapes late-season drought.",
    ),
}


# ============================================================
#  CHICKPEA (Cicer arietinum)
# ============================================================
CHICKPEA_VARIETIES: dict[str, VarietyProfile] = {

    "jg_11": VarietyProfile(
        key="jg_11", name="JG 11", crop="chickpea",
        release_year=2006, released_by="JNKVV Jabalpur",
        notified_states=["Madhya Pradesh", "Maharashtra", "Karnataka",
                         "Andhra Pradesh", "Rajasthan"],
        yield_potential_t_ha=2.8, season_days=105, plant_height_cm=48,
        lodging_resistance=0.75,
        optimal_temp_min=15, optimal_temp_max=25,
        critical_temp_high=32, critical_temp_low=4,
        drought_stress_modifier=0.70,
        heat_stress_modifier=0.75,
        disease_resistance={
            "chickpea_wilt":         0.25,
            "chickpea_ascochyta":    0.45,
            "chickpea_bgm":          0.50,
        },
        notes="Most widely grown Desi chickpea. Wilt resistant.",
    ),

    "kak_2": VarietyProfile(
        key="kak_2", name="KAK 2", crop="chickpea",
        release_year=2010, released_by="MPKV Rahuri",
        notified_states=["Maharashtra", "Madhya Pradesh", "Gujarat"],
        yield_potential_t_ha=2.5, season_days=100, plant_height_cm=44,
        lodging_resistance=0.80,
        optimal_temp_min=15, optimal_temp_max=25,
        critical_temp_high=33, critical_temp_low=4,
        drought_stress_modifier=0.65,
        disease_resistance={
            "chickpea_wilt":      0.20,
            "chickpea_ascochyta": 0.35,
        },
        notes="Drought tolerant Desi type.",
    ),

    "pusa_256": VarietyProfile(
        key="pusa_256", name="Pusa 256", crop="chickpea",
        release_year=2003, released_by="IARI New Delhi",
        notified_states=["Haryana", "Punjab", "Uttar Pradesh",
                         "Rajasthan"],
        yield_potential_t_ha=2.6, season_days=110, plant_height_cm=46,
        lodging_resistance=0.70,
        optimal_temp_min=14, optimal_temp_max=24,
        critical_temp_high=31, critical_temp_low=3,
        drought_stress_modifier=0.80,
        disease_resistance={
            "chickpea_wilt":  0.30,
        },
        notes="Desi type, adapted to NW India.",
    ),

    "jaki_9218": VarietyProfile(
        key="jaki_9218", name="JAKI 9218 (Kabuli)", crop="chickpea",
        release_year=2003, released_by="JNKVV Jabalpur",
        notified_states=["Madhya Pradesh", "Maharashtra", "Karnataka"],
        yield_potential_t_ha=3.0, season_days=115, plant_height_cm=50,
        lodging_resistance=0.70,
        optimal_temp_min=15, optimal_temp_max=24,
        critical_temp_high=31, critical_temp_low=4,
        drought_stress_modifier=0.85,
        disease_resistance={
            "chickpea_wilt":         0.35,
            "chickpea_ascochyta":    0.40,
        },
        notes="Large-seeded Kabuli type for export quality.",
    ),
}


# ============================================================
#  MUSTARD (Brassica juncea)
# ============================================================
MUSTARD_VARIETIES: dict[str, VarietyProfile] = {

    "rh_749": VarietyProfile(
        key="rh_749", name="RH 749", crop="mustard",
        release_year=2003, released_by="CCSHAU Hisar",
        notified_states=["Haryana", "Punjab", "Rajasthan", "Uttar Pradesh"],
        yield_potential_t_ha=2.8, season_days=130, plant_height_cm=175,
        lodging_resistance=0.55,
        optimal_temp_min=10, optimal_temp_max=22,
        critical_temp_high=28, critical_temp_low=2,
        disease_resistance={
            "alternaria_blight":  0.45,
            "white_rust":         0.55,
            "sclerotinia":        0.60,
        },
        notes="High oil (40 %) variety. Standard for NW India.",
    ),

    "nrchb_101": VarietyProfile(
        key="nrchb_101", name="NRCHB 101", crop="mustard",
        release_year=2008, released_by="ICAR-DRMR Bharatpur",
        notified_states=["Haryana", "Rajasthan", "Uttar Pradesh"],
        yield_potential_t_ha=3.0, season_days=128, plant_height_cm=165,
        lodging_resistance=0.60,
        optimal_temp_min=10, optimal_temp_max=23,
        critical_temp_high=29, critical_temp_low=2,
        heat_stress_modifier=0.80,
        disease_resistance={
            "alternaria_blight":  0.35,
            "white_rust":         0.40,
        },
        notes="Improved oil content (41 %). Reduced glucosinolates.",
    ),

    "pusa_tarak": VarietyProfile(
        key="pusa_tarak", name="Pusa Tarak", crop="mustard",
        release_year=2014, released_by="IARI New Delhi",
        notified_states=["Haryana", "Rajasthan", "Uttar Pradesh",
                         "Madhya Pradesh"],
        yield_potential_t_ha=2.9, season_days=125, plant_height_cm=158,
        lodging_resistance=0.65,
        optimal_temp_min=10, optimal_temp_max=23,
        critical_temp_high=29, critical_temp_low=1,
        disease_resistance={
            "alternaria_blight":  0.30,
            "white_rust":         0.35,
            "sclerotinia":        0.45,
        },
        notes="Moderately resistant to alternaria and white rust.",
    ),
}


# ============================================================
#  TOMATO (Solanum lycopersicum)
# ============================================================
TOMATO_VARIETIES: dict[str, VarietyProfile] = {

    "pusa_ruby": VarietyProfile(
        key="pusa_ruby", name="Pusa Ruby", crop="tomato",
        release_year=1972, released_by="IARI New Delhi",
        notified_states=["Multiple states"],
        yield_potential_t_ha=35.0, season_days=100, plant_height_cm=110,
        lodging_resistance=0.60,
        optimal_temp_min=20, optimal_temp_max=28,
        critical_temp_high=36, critical_temp_low=10,
        disease_resistance={
            "early_blight":    0.55,
            "late_blight":     0.60,
            "fusarium_wilt":   0.50,
        },
        notes="Determinate type. Widely grown open-pollinated variety.",
    ),

    "arka_vikas": VarietyProfile(
        key="arka_vikas", name="Arka Vikas", crop="tomato",
        release_year=1987, released_by="IIHR Bangalore",
        notified_states=["Karnataka", "Tamil Nadu", "Andhra Pradesh",
                         "Maharashtra"],
        yield_potential_t_ha=40.0, season_days=105, plant_height_cm=120,
        lodging_resistance=0.65,
        optimal_temp_min=20, optimal_temp_max=30,
        critical_temp_high=37, critical_temp_low=12,
        disease_resistance={
            "early_blight":    0.45,
            "late_blight":     0.55,
            "fusarium_wilt":   0.40,
            "bacterial_wilt":  0.45,
        },
        notes="High yielder for peninsular India.",
    ),
}


# ============================================================
#  POTATO (Solanum tuberosum)
# ============================================================
POTATO_VARIETIES: dict[str, VarietyProfile] = {

    "kufri_jyoti": VarietyProfile(
        key="kufri_jyoti", name="Kufri Jyoti", crop="potato",
        release_year=1968, released_by="CPRI Shimla",
        notified_states=["Uttar Pradesh", "Bihar", "West Bengal",
                         "Karnataka", "Himachal Pradesh"],
        yield_potential_t_ha=28.0, season_days=90, plant_height_cm=55,
        lodging_resistance=0.70,
        optimal_temp_min=15, optimal_temp_max=22,
        critical_temp_high=30, critical_temp_low=4,
        disease_resistance={
            "late_blight":    0.45,
            "early_blight":   0.50,
            "potato_virus_y": 0.55,
        },
        notes="Most widely cultivated potato in plains. Moderate late blight resistance.",
    ),

    "kufri_bahar": VarietyProfile(
        key="kufri_bahar", name="Kufri Bahar", crop="potato",
        release_year=1988, released_by="CPRI Shimla",
        notified_states=["Uttar Pradesh", "Bihar", "West Bengal"],
        yield_potential_t_ha=32.0, season_days=80, plant_height_cm=50,
        lodging_resistance=0.72,
        optimal_temp_min=15, optimal_temp_max=22,
        critical_temp_high=30, critical_temp_low=4,
        heat_stress_modifier=0.85,
        disease_resistance={
            "late_blight":    0.50,
            "early_blight":   0.45,
        },
        notes="Early-maturing high-yielder for spring crop.",
    ),

    "kufri_pushkar": VarietyProfile(
        key="kufri_pushkar", name="Kufri Pushkar", crop="potato",
        release_year=2008, released_by="CPRI Shimla",
        notified_states=["Uttar Pradesh", "West Bengal", "Gujarat"],
        yield_potential_t_ha=36.0, season_days=90, plant_height_cm=56,
        lodging_resistance=0.75,
        optimal_temp_min=14, optimal_temp_max=23,
        critical_temp_high=31, critical_temp_low=4,
        heat_stress_modifier=0.80,
        disease_resistance={
            "late_blight":    0.30,  # good resistance
            "early_blight":   0.40,
        },
        notes="High-yielding with improved late blight resistance.",
    ),
}


# ============================================================
#  MASTER REGISTRY
# ============================================================
ALL_VARIETIES: dict[str, dict[str, VarietyProfile]] = {
    "wheat":    WHEAT_VARIETIES,
    "rice":     RICE_VARIETIES,
    "maize":    MAIZE_VARIETIES,
    "soybean":  SOYBEAN_VARIETIES,
    "chickpea": CHICKPEA_VARIETIES,
    "mustard":  MUSTARD_VARIETIES,
    "tomato":   TOMATO_VARIETIES,
    "potato":   POTATO_VARIETIES,
}


def get_variety(crop: str, variety_key: str) -> Optional[VarietyProfile]:
    return ALL_VARIETIES.get(crop, {}).get(variety_key)


def list_varieties(crop: str) -> list[VarietyProfile]:
    return list(ALL_VARIETIES.get(crop, {}).values())


def get_variety_names(crop: str) -> list[tuple[str, str]]:
    """Return list of (key, display_name) tuples for a crop."""
    return [(k, v.name) for k, v in ALL_VARIETIES.get(crop, {}).items()]
