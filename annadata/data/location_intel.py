"""
India State-wise Location Intelligence Database.

Each state entry covers:
  - weed_herbicide_resistance: confirmed HR cases + affected crops
  - prominent_diseases: crop → disease keys + risk level (0–1)
  - prominent_insects: crop → pest list
  - soil_fertility_profile: nutrient status, pH, OM, common deficiencies
  - irrigation_water_quality: typical EC, SAR, pH, common contaminants

Sources
──────────────────────────────────────────────────────────────────────────
Weed HR:
  Frontiers Agronomy 2026 (Maity et al.): Weed management scenario India
  Phytoparasitica 2023 (Soni et al.): Phalaris minor HR history
  Cambridge 2023 (Choudhary et al.): ALS resistance Echinochloa in rice, India
  ScienceDirect 2021 (Chhokar et al.): Herbicide resistance Haryana

Soil Fertility:
  Agriculture.Institute 2025: Soil fertility status India (NPK ratio 10.9:4.4:1)
  ICRIER report: Urea overuse, Zn deficiency 36–49 % of Indian soils
  National data: Boron deficiency 23–33 % soils; acidic NE soils

Disease / Insects:
  invadeagro.com 2025: Common crop diseases India
  PMC 10153038 (Nat Climate Change 2023): Climate-pathogen shifts
  Savary et al. 2016 (Food Security): Rice yield loss profiles, tropical Asia
  Frontiers wheat heat 2023: IGP rust epidemics

Irrigation water:
  State agricultural university reports; CGWB groundwater data
──────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from dataclasses import dataclass, field


# ──────────────────────────────────────────────────────────────────────────────
#  DATA STRUCTURES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class WeedResistanceCase:
    weed_species: str          # scientific / common name
    crop_system:  str          # e.g. "wheat", "rice", "soybean"
    resistant_to: list[str]    # herbicide common names or MOA
    moa_class:    str          # ACCase / ALS / PSII / Synthetic auxin
    distribution: str          # district/region description
    severity:     float        # 0–1 (fraction of fields affected estimate)


@dataclass
class DiseasePressure:
    disease_key:  str          # matches keys in diseases.py / stress_responses.py
    crop:         str
    risk_level:   float        # 0–1 (0 = rare, 1 = annual epidemic)
    season:       str          # kharif / rabi / both
    notes:        str = ""


@dataclass
class InsectPressure:
    pest_name:    str
    crop:         str
    risk_level:   float
    season:       str
    notes:        str = ""


@dataclass
class SoilFertilityProfile:
    # typical ranges for dominant soil types in the state
    ph_range:             tuple[float, float]
    ec_ds_m_range:        tuple[float, float]
    organic_matter_pct:   float      # typical value
    nitrogen_status:      str        # "low" | "medium" | "high"
    phosphorus_status:    str
    potassium_status:     str
    zinc_deficient_pct:   float      # % of cultivated area deficient
    boron_deficient_pct:  float
    sulphur_deficient_pct: float
    iron_deficient_pct:   float
    dominant_texture:     str
    dominant_soil_type:   str        # e.g. "Alluvial", "Black cotton", "Red laterite"
    notes:                str = ""


@dataclass
class IrrigationWaterProfile:
    typical_ec_ds_m:       float
    ec_range:              tuple[float, float]
    ph_range:              tuple[float, float]
    sar_range:             tuple[float, float]   # sodium adsorption ratio
    primary_source:        str                   # canal / tube-well / tank / rain-fed
    quality_class:         str                   # C1-C4 × S1-S4 (USDA)
    common_contaminants:   list[str]
    fluoride_risk:         float                 # 0–1
    arsenic_risk:          float
    nitrate_risk:          float
    notes:                 str = ""


@dataclass
class StateIntelligence:
    state: str
    region: str                  # "NW India", "Eastern India", etc.
    primary_crops: list[str]
    weed_hr_cases: list[WeedResistanceCase]
    disease_pressure: list[DiseasePressure]
    insect_pressure: list[InsectPressure]
    soil_fertility: SoilFertilityProfile
    irrigation_water: IrrigationWaterProfile
    agronomic_notes: str = ""


# ──────────────────────────────────────────────────────────────────────────────
#  STATE DATA
# ──────────────────────────────────────────────────────────────────────────────

LOCATION_INTELLIGENCE: dict[str, StateIntelligence] = {

    # ════════════════════════════════════════════════════════════════════
    "Punjab": StateIntelligence(
        state="Punjab", region="NW India",
        primary_crops=["wheat", "rice", "maize", "potato"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon", "clodinafop", "sulfosulfuron",
                 "fenoxaprop", "pinoxaden", "mesosulfuron+iodosulfuron",
                 "metribuzin"],
                "PSII / ACCase / ALS",
                "7.5 M ha wheat area; worst HR hotspot globally (Soni et al. 2023)",
                severity=0.85,
            ),
            WeedResistanceCase(
                "Polypogon monspeliensis", "wheat",
                ["sulfosulfuron", "mesosulfuron", "pyroxasulam"],
                "ALS",
                "Emerging; Malwa and Doaba belts",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.70, "rabi",
                "Puccinia striiformis — annual risk in Majha & Doaba; "
                "new virulent races post-2016"),
            DiseasePressure("wheat_leaf_rust",     "wheat", 0.65, "rabi",
                "Puccinia triticina — most common rust in Punjab"),
            DiseasePressure("wheat_stem_rust",     "wheat", 0.40, "rabi",
                "Ug99 and derivatives detected"),
            DiseasePressure("karnal_bunt",         "wheat", 0.50, "rabi",
                "Tilletia indica — Punjab and Haryana are highest risk zones"),
            DiseasePressure("rice_blast",          "rice",  0.45, "kharif",
                "Magnaporthe oryzae — leaf + neck blast"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.60, "kharif",
                "Rhizoctonia solani — elevated risk in dense transplanted rice"),
            DiseasePressure("rice_bacterial_blight","rice", 0.40, "kharif"),
        ],

        insect_pressure=[
            InsectPressure("wheat_aphid",          "wheat", 0.55, "rabi",
                "Sitobion avenae — secondary pest, sucking"),
            InsectPressure("brown_planthopper",    "rice",  0.50, "kharif",
                "Nilaparvata lugens — hopperburn risk"),
            InsectPressure("yellow_stem_borer",    "rice",  0.55, "kharif",
                "Scirpophaga incertulas — dead heart + white ear"),
            InsectPressure("termite",              "wheat", 0.35, "rabi",
                "Direct drilling fields"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.6, 8.6),
            ec_ds_m_range=(0.20, 0.80),
            organic_matter_pct=0.65,
            nitrogen_status="medium-high",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.52,    # ICRIER: alkaline soils → Zn unavailable
            boron_deficient_pct=0.28,
            sulphur_deficient_pct=0.35,
            iron_deficient_pct=0.20,
            dominant_texture="sandy loam to loam",
            dominant_soil_type="Indo-Gangetic Alluvial (Entisols/Inceptisols)",
            notes="NPK ratio heavily skewed N:P:K = 18:5:1 (2023 data). "
                  "Intensive rice-wheat — depleting K and Zn. Low OM (0.5–0.8 %).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.35,
            ec_range=(0.15, 1.20),
            ph_range=(7.4, 8.2),
            sar_range=(2.0, 8.0),
            primary_source="Canal + tube-well (mixed)",
            quality_class="C2-S1 to C3-S2",
            common_contaminants=["nitrate", "fluoride"],
            fluoride_risk=0.30,
            arsenic_risk=0.10,
            nitrate_risk=0.45,
            notes="Canal water (C2-S1) is excellent. Tube-well quality varies; "
                  "nitrate contamination from fertilizer leaching common.",
        ),
        agronomic_notes="World's highest wheat/rice productivity but facing "
                         "severe groundwater depletion, HR weeds, and soil "
                         "health degradation from intensive monoculture.",
    ),

    # ════════════════════════════════════════════════════════════════════
    "Haryana": StateIntelligence(
        state="Haryana", region="NW India",
        primary_crops=["wheat", "rice", "mustard", "cotton"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon", "clodinafop", "sulfosulfuron", "metribuzin",
                 "fenoxaprop", "pinoxaden"],
                "PSII / ACCase / ALS",
                "First HR case globally (isoproturon, 1991). "
                "Spread to 2.5 M ha wheat area (Chhokar et al. 2021)",
                severity=0.88,
            ),
            WeedResistanceCase(
                "Rumex dentatus", "wheat",
                ["metsulfuron", "mesosulfuron+iodosulfuron",
                 "pyroxsulam", "halauxifen+florasulam"],
                "ALS + Synthetic auxin",
                "Multiple-HR broadleaf weed — Karnal, Kaithal, Hisar districts",
                severity=0.40,
            ),
        ],

        disease_pressure=[
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.72, "rabi",
                "Very high risk — close to origin of new virulent races"),
            DiseasePressure("wheat_leaf_rust",     "wheat", 0.68, "rabi"),
            DiseasePressure("karnal_bunt",         "wheat", 0.55, "rabi",
                "T. indica — highest incidence zone in India"),
            DiseasePressure("fusarium_head_blight","wheat", 0.40, "rabi",
                "F. graminearum — warm humid anthesis"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.65, "kharif"),
            DiseasePressure("rice_bacterial_blight","rice", 0.45, "kharif"),
            DiseasePressure("alternaria_blight",   "mustard", 0.60, "rabi"),
            DiseasePressure("white_rust",          "mustard", 0.50, "rabi"),
        ],

        insect_pressure=[
            InsectPressure("mustard_aphid",     "mustard", 0.70, "rabi",
                "Lipaphis erysimi — primary insect constraint on mustard"),
            InsectPressure("cotton_bollworm",   "cotton",  0.65, "kharif",
                "Helicoverpa armigera + Pectinophora gossypiella"),
            InsectPressure("whitefly",          "cotton",  0.60, "kharif",
                "Bemisia tabaci — CLCuV vector"),
            InsectPressure("wheat_aphid",       "wheat",   0.50, "rabi"),
            InsectPressure("brown_planthopper", "rice",    0.45, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.8, 8.8),
            ec_ds_m_range=(0.25, 2.50),   # saline patches in Rohtak, Jhajjar
            organic_matter_pct=0.55,
            nitrogen_status="medium",
            phosphorus_status="low-medium",
            potassium_status="medium",
            zinc_deficient_pct=0.55,
            boron_deficient_pct=0.32,
            sulphur_deficient_pct=0.40,
            iron_deficient_pct=0.22,
            dominant_texture="sandy loam to clay loam",
            dominant_soil_type="Indo-Gangetic Alluvial; saline-sodic patches",
            notes="10 % of area has salinity/sodicity issues (Rohtak, Jhajjar, Hisar). "
                  "NPK ratio 16:4:1 — severe N excess. OM very low (0.4–0.7 %). "
                  "Zn deficiency universal in alkaline soils.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.55,
            ec_range=(0.20, 3.50),
            ph_range=(7.5, 8.5),
            sar_range=(3.0, 15.0),
            primary_source="Tube-well dominated",
            quality_class="C2-S1 to C4-S3",
            common_contaminants=["nitrate", "fluoride", "sodium"],
            fluoride_risk=0.55,   # high fluoride in southern Haryana
            arsenic_risk=0.12,
            nitrate_risk=0.50,
            notes="Southern Haryana (Mahendragarh, Rewari) — high fluoride "
                  "in groundwater (>1.5 mg/L). Saline tube-wells in Rohtak, "
                  "Hisar, Bhiwani — require mixing with canal water.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Uttar Pradesh": StateIntelligence(
        state="Uttar Pradesh", region="NW-Eastern India",
        primary_crops=["wheat", "rice", "sugarcane", "maize", "potato"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon", "clodinafop", "fenoxaprop"],
                "PSII / ACCase",
                "Western UP (Meerut, Muzaffarnagar, Saharanpur)",
                severity=0.65,
            ),
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Eastern UP rice belt (Gorakhpur, Azamgarh)",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.65, "rabi"),
            DiseasePressure("wheat_leaf_rust",     "wheat", 0.60, "rabi"),
            DiseasePressure("rice_blast",          "rice",  0.60, "kharif",
                "Eastern UP / Terai — high blast risk"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.65, "kharif"),
            DiseasePressure("rice_bacterial_blight","rice", 0.50, "kharif"),
            DiseasePressure("late_blight",         "potato",0.70, "rabi",
                "Agra/Farrukhabad potato belt — Phytophthora infestans epidemic risk"),
        ],

        insect_pressure=[
            InsectPressure("yellow_stem_borer",  "rice",     0.60, "kharif"),
            InsectPressure("brown_planthopper",  "rice",     0.50, "kharif"),
            InsectPressure("leaf_folder",        "rice",     0.45, "kharif"),
            InsectPressure("wheat_termite",      "wheat",    0.40, "rabi",
                "Sandy / light-textured soils of Bundelkhand"),
            InsectPressure("sugarcane_pyrilla",  "sugarcane",0.45, "kharif"),
            InsectPressure("potato_aphid",       "potato",   0.55, "rabi",
                "PLRV/PVY vector"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.2, 8.4),
            ec_ds_m_range=(0.15, 0.60),
            organic_matter_pct=0.52,
            nitrogen_status="low-medium",
            phosphorus_status="low",
            potassium_status="low-medium",
            zinc_deficient_pct=0.48,
            boron_deficient_pct=0.30,
            sulphur_deficient_pct=0.38,
            iron_deficient_pct=0.18,
            dominant_texture="sandy loam to loam",
            dominant_soil_type="Alluvial (Entisols/Inceptisols)",
            notes="Large spatial variability — Tarai soils fertile; "
                  "Bundelkhand soils degraded. P and Zn deficiencies widespread. "
                  "Low OM (0.3–0.6 %).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.40,
            ec_range=(0.15, 1.0),
            ph_range=(7.2, 8.0),
            sar_range=(1.5, 6.0),
            primary_source="Canal + tube-well",
            quality_class="C2-S1",
            common_contaminants=["nitrate", "arsenic (Terai)"],
            fluoride_risk=0.20,
            arsenic_risk=0.35,   # Terai region — Gandak, Ghaghara alluvium
            nitrate_risk=0.40,
            notes="Arsenic contamination in Terai districts (Ballia, Ghazipur) "
                  "from alluvial groundwater. Canal irrigation generally good quality.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Madhya Pradesh": StateIntelligence(
        state="Madhya Pradesh", region="Central India",
        primary_crops=["wheat", "soybean", "chickpea", "maize", "cotton"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa colona", "soybean",
                ["imazethapyr"],
                "ALS",
                "Major soybean belt — Indore, Dewas, Ujjain divisions "
                "(Chander et al. 2019)",
                severity=0.50,
            ),
            WeedResistanceCase(
                "Commelina communis", "soybean",
                ["imazethapyr"],
                "ALS",
                "Co-occurs with E. colona resistance",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("soybean_yellow_mosaic", "soybean", 0.65, "kharif",
                "YMV — primary disease threat in MP soybean belt"),
            DiseasePressure("charcoal_rot",          "soybean", 0.55, "kharif",
                "Macrophomina phaseolina — hot+dry late season"),
            DiseasePressure("soybean_rust",          "soybean", 0.40, "kharif",
                "Phakopsora pachyrhizi — late kharif risk"),
            DiseasePressure("chickpea_wilt",         "chickpea",0.60, "rabi",
                "Fusarium wilt — endemic in heavy black soils"),
            DiseasePressure("chickpea_ascochyta",    "chickpea",0.45, "rabi",
                "Ascochyta rabiei — cool-moist conditions"),
            DiseasePressure("wheat_yellow_rust",     "wheat",   0.45, "rabi",
                "Moderate risk — northern MP Gwalior / Chambal"),
        ],

        insect_pressure=[
            InsectPressure("soybean_girdle_beetle", "soybean",  0.55, "kharif",
                "Obereopsis brevis — most damaging insect in MP soybean"),
            InsectPressure("soybean_leaf_roller",   "soybean",  0.45, "kharif"),
            InsectPressure("chickpea_pod_borer",    "chickpea", 0.70, "rabi",
                "Helicoverpa armigera — primary economic pest of chickpea"),
            InsectPressure("cotton_bollworm",       "cotton",   0.60, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.0, 8.5),
            ec_ds_m_range=(0.20, 0.50),
            organic_matter_pct=0.75,
            nitrogen_status="medium",
            phosphorus_status="low",
            potassium_status="medium-high",
            zinc_deficient_pct=0.40,
            boron_deficient_pct=0.25,
            sulphur_deficient_pct=0.45,
            iron_deficient_pct=0.15,
            dominant_texture="clay to clay loam",
            dominant_soil_type="Vertisols (Black cotton soils) + mixed red soils",
            notes="Vertisols naturally rich in K but P-deficient. "
                  "Cracking clays — waterlogging risk in kharif. "
                  "S deficiency increasing as soybean area expands. "
                  "Agriculture.Institute 2025: MP NPK ratio 12:3:1.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.30,
            ec_range=(0.15, 0.80),
            ph_range=(7.0, 8.0),
            sar_range=(1.0, 5.0),
            primary_source="Tank + canal + tube-well",
            quality_class="C1-S1 to C2-S1",
            common_contaminants=["fluoride (Bundelkhand)", "nitrate"],
            fluoride_risk=0.45,   # Bundelkhand region
            arsenic_risk=0.05,
            nitrate_risk=0.30,
            notes="Generally good quality canal water. Fluoride elevated "
                  "in Bundelkhand granite aquifers.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Maharashtra": StateIntelligence(
        state="Maharashtra", region="Western/Peninsular India",
        primary_crops=["soybean", "cotton", "sugarcane", "wheat", "chickpea",
                       "tomato"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa colona", "soybean",
                ["imazethapyr"],
                "ALS",
                "Vidarbha & Marathwada soybean belt",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("soybean_yellow_mosaic", "soybean", 0.70, "kharif"),
            DiseasePressure("charcoal_rot",          "soybean", 0.60, "kharif",
                "Hot + dry late-season — Vidarbha"),
            DiseasePressure("cotton_clcv",           "cotton",  0.65, "kharif",
                "Cotton Leaf Curl Virus — whitefly mediated"),
            DiseasePressure("chickpea_wilt",         "chickpea",0.55, "rabi"),
            DiseasePressure("sclerotinia",           "soybean", 0.35, "kharif",
                "Sclerotinia stem rot — cool + moist late kharif"),
            DiseasePressure("bacterial_wilt",        "tomato",  0.60, "kharif",
                "Ralstonia solanacearum — high in coastal areas"),
        ],

        insect_pressure=[
            InsectPressure("cotton_bollworm",     "cotton",  0.70, "kharif",
                "Helicoverpa + pink bollworm. Bt resistance emerging."),
            InsectPressure("whitefly",            "cotton",  0.65, "kharif",
                "Bemisia tabaci — CLCV vector + direct damage"),
            InsectPressure("soybean_thrips",      "soybean", 0.40, "kharif"),
            InsectPressure("chickpea_pod_borer",  "chickpea",0.68, "rabi"),
            InsectPressure("sugarcane_pyrilla",   "sugarcane",0.45, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.8, 8.2),
            ec_ds_m_range=(0.15, 0.60),
            organic_matter_pct=0.70,
            nitrogen_status="medium",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.42,
            boron_deficient_pct=0.30,
            sulphur_deficient_pct=0.50,
            iron_deficient_pct=0.15,
            dominant_texture="heavy clay",
            dominant_soil_type="Vertisols (Black cotton) + Alfisols",
            notes="P severely deficient in black soils (low P sorption site "
                  "saturation). S deficiency increasing. "
                  "NPK ratio 2023–24: Maharashtra 9:3:1.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.35,
            ec_range=(0.10, 0.90),
            ph_range=(7.0, 8.0),
            sar_range=(1.0, 4.0),
            primary_source="Dam + canal + tank",
            quality_class="C1-S1 to C2-S1",
            common_contaminants=["fluoride", "nitrate"],
            fluoride_risk=0.35,
            arsenic_risk=0.05,
            nitrate_risk=0.35,
            notes="Generally good canal water from major dams. "
                  "Fluoride in basaltic aquifers.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Rajasthan": StateIntelligence(
        state="Rajasthan", region="NW Arid India",
        primary_crops=["wheat", "mustard", "chickpea", "soybean", "cotton"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon", "clodinafop"],
                "PSII / ACCase",
                "Kota, Baran, Bundi — Hadoti region",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("wheat_leaf_rust",   "wheat",   0.50, "rabi",
                "Moderate risk — P. triticina"),
            DiseasePressure("wheat_yellow_rust", "wheat",   0.45, "rabi"),
            DiseasePressure("alternaria_blight", "mustard", 0.65, "rabi",
                "Primary disease of mustard in Rajasthan"),
            DiseasePressure("white_rust",        "mustard", 0.55, "rabi",
                "Albugo candida — cool-moist pockets of eastern Rajasthan"),
            DiseasePressure("chickpea_wilt",     "chickpea",0.55, "rabi"),
            DiseasePressure("chickpea_bgm",      "chickpea",0.40, "rabi",
                "Botrytis grey mould — foggy winters"),
        ],

        insect_pressure=[
            InsectPressure("mustard_aphid",      "mustard", 0.75, "rabi",
                "Lipaphis erysimi — most destructive insect pest of mustard"),
            InsectPressure("painted_bug",        "mustard", 0.45, "rabi",
                "Bagrada hilaris — seedling attack"),
            InsectPressure("chickpea_pod_borer", "chickpea",0.65, "rabi"),
            InsectPressure("locusts",            "wheat",   0.30, "rabi",
                "Desert locust (Schistocerca gregaria) — episodic"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.5, 9.0),
            ec_ds_m_range=(0.20, 5.00),  # saline soils common
            organic_matter_pct=0.35,      # very low OC in arid soils
            nitrogen_status="low",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.50,
            boron_deficient_pct=0.28,
            sulphur_deficient_pct=0.42,
            iron_deficient_pct=0.12,
            dominant_texture="sandy loam to sandy",
            dominant_soil_type="Aridisols + saline-alkaline patches",
            notes="Very low OM (< 0.5 %) — dominant constraint. "
                  "Salinity/sodicity in canal-command areas (Indira Gandhi Canal). "
                  "Severe wind erosion — soil organic matter mining. "
                  "P, Zn, N all low.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.70,
            ec_range=(0.30, 5.00),
            ph_range=(7.5, 9.0),
            sar_range=(4.0, 25.0),  # high SAR in saline tracts
            primary_source="Canal (Indira Gandhi) + tube-well",
            quality_class="C2-S1 to C4-S4",
            common_contaminants=["fluoride", "sodium", "nitrate"],
            fluoride_risk=0.65,   # highest fluoride risk state
            arsenic_risk=0.10,
            nitrate_risk=0.30,
            notes="Fluoride levels up to 20 mg/L in Barmer, Jalore, Jodhpur. "
                  "Indira Gandhi Canal water is good quality but supply irregular. "
                  "Saline tube-wells in western Rajasthan — caution needed.",
        ),
        agronomic_notes="Drought and heat are dominant constraints. "
                         "Most of western Rajasthan is purely rainfed/kharif dependent.",
    ),

    # ════════════════════════════════════════════════════════════════════
    "Bihar": StateIntelligence(
        state="Bihar", region="Eastern India",
        primary_crops=["rice", "wheat", "maize", "chickpea", "potato",
                       "mustard"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Rice belt in north Bihar (Sitamarhi, Muzaffarpur)",
                severity=0.30,
            ),
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon"],
                "PSII",
                "Kosi and Gandak command areas",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.70, "kharif",
                "Very high blast risk — Terai and eastern districts"),
            DiseasePressure("rice_bacterial_blight","rice", 0.65, "kharif",
                "Flood damage entry — Kosi floods annual"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.60, "kharif"),
            DiseasePressure("wheat_leaf_rust",     "wheat", 0.55, "rabi"),
            DiseasePressure("late_blight",         "potato",0.72, "rabi",
                "P. infestans — winter fog + cool conditions"),
        ],

        insect_pressure=[
            InsectPressure("yellow_stem_borer",  "rice",  0.65, "kharif"),
            InsectPressure("brown_planthopper",  "rice",  0.55, "kharif"),
            InsectPressure("leaf_folder",        "rice",  0.50, "kharif"),
            InsectPressure("chickpea_pod_borer", "chickpea", 0.65, "rabi"),
            InsectPressure("potato_aphid",       "potato", 0.55, "rabi"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.5, 8.2),
            ec_ds_m_range=(0.10, 0.50),
            organic_matter_pct=0.55,
            nitrogen_status="low",
            phosphorus_status="low",
            potassium_status="low",
            zinc_deficient_pct=0.45,
            boron_deficient_pct=0.35,
            sulphur_deficient_pct=0.40,
            iron_deficient_pct=0.20,
            dominant_texture="sandy loam to loam",
            dominant_soil_type="New Alluvium (Entisols) + some Inceptisols",
            notes="Kosi fan — very sandy, low fertility. "
                  "N, P, K all deficient. Boron critical for mustard. "
                  "Waterlogging in low-lying areas during kharif.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.30,
            ec_range=(0.10, 0.60),
            ph_range=(6.8, 7.8),
            sar_range=(1.0, 4.0),
            primary_source="Canal + tube-well + rivers",
            quality_class="C1-S1 to C2-S1",
            common_contaminants=["arsenic", "iron"],
            fluoride_risk=0.10,
            arsenic_risk=0.55,  # Ganga alluvium arsenic — serious health risk
            nitrate_risk=0.25,
            notes="Arsenic contamination in Bhojpur, Buxar, Patna, Vaishali — "
                  "serious groundwater concern (CGWB data). "
                  "High iron in tube-well water — clogging drip systems.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Chhattisgarh": StateIntelligence(
        state="Chhattisgarh", region="Central India",
        primary_crops=["rice", "maize", "wheat", "soybean", "chickpea"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Dhamtari, Raigarh districts "
                "(Choudhary et al. 2023 Weed Technology)",
                severity=0.40,
            ),
            WeedResistanceCase(
                "Cyperus difformis", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Rice fields of Raipur and Durg divisions",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.72, "kharif",
                "Very high — tribal/upland rice — blast endemic zone"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.55, "kharif"),
            DiseasePressure("rice_bacterial_blight","rice", 0.50, "kharif"),
            DiseasePressure("maize_blsb",          "maize", 0.55, "kharif",
                "Warm-humid conditions — Rhizoctonia endemic"),
            DiseasePressure("maize_downy_mildew",  "maize", 0.45, "kharif"),
        ],

        insect_pressure=[
            InsectPressure("yellow_stem_borer",   "rice",  0.65, "kharif"),
            InsectPressure("brown_planthopper",   "rice",  0.50, "kharif"),
            InsectPressure("gall_midge",          "rice",  0.55, "kharif",
                "Orseolia oryzae — endemic in eastern bastar"),
            InsectPressure("fall_armyworm",       "maize", 0.60, "kharif",
                "Spodoptera frugiperda — invasive; rapid spread since 2018"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.0, 7.5),
            ec_ds_m_range=(0.10, 0.30),
            organic_matter_pct=0.80,
            nitrogen_status="low-medium",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.35,
            boron_deficient_pct=0.40,
            sulphur_deficient_pct=0.35,
            iron_deficient_pct=0.25,
            dominant_texture="sandy loam to clay loam",
            dominant_soil_type="Red and Yellow soils (Alfisols/Ultisols) + "
                                "Black cotton soils (plains)",
            notes="Slightly acidic soils in uplands — P fixation problem. "
                  "Boron deficiency critical for rice. "
                  "Lower plains Vertisols with P deficiency.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.20,
            ec_range=(0.10, 0.40),
            ph_range=(6.5, 7.5),
            sar_range=(0.5, 3.0),
            primary_source="Tank + canal (Mahanadi system)",
            quality_class="C1-S1",
            common_contaminants=["iron"],
            fluoride_risk=0.10,
            arsenic_risk=0.05,
            nitrate_risk=0.15,
            notes="Generally excellent water quality. High Fe in some "
                  "tube-well areas — reduces Mn, Zn availability.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Andhra Pradesh": StateIntelligence(
        state="Andhra Pradesh", region="Peninsular India",
        primary_crops=["rice", "maize", "cotton", "chilli", "groundnut",
                       "tomato"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Krishna, Godavari deltas — intensive rice system",
                severity=0.40,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.65, "kharif"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.70, "kharif",
                "Very high in delta rice — dense canopy, humid"),
            DiseasePressure("rice_bacterial_blight","rice", 0.60, "kharif",
                "Cyclone-related flooding entry"),
            DiseasePressure("maize_blsb",          "maize", 0.50, "kharif",
                "Humid coastal conditions"),
            DiseasePressure("bacterial_wilt",      "tomato",0.65, "kharif",
                "Ralstonia solanacearum — endemic in warm soils"),
            DiseasePressure("late_blight",         "tomato",0.55, "rabi"),
        ],

        insect_pressure=[
            InsectPressure("yellow_stem_borer",  "rice",   0.65, "kharif"),
            InsectPressure("brown_planthopper",  "rice",   0.60, "kharif"),
            InsectPressure("gall_midge",         "rice",   0.45, "kharif"),
            InsectPressure("cotton_bollworm",    "cotton", 0.65, "kharif"),
            InsectPressure("fall_armyworm",      "maize",  0.60, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 7.8),
            ec_ds_m_range=(0.10, 0.50),
            organic_matter_pct=0.60,
            nitrogen_status="low-medium",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.38,
            boron_deficient_pct=0.28,
            sulphur_deficient_pct=0.42,
            iron_deficient_pct=0.18,
            dominant_texture="clay to sandy loam",
            dominant_soil_type="Red sandy soils + Alluvial deltas + Black soils",
            notes="Coastal delta soils are fertile alluvial. Upland red soils "
                  "very low fertility. P deficiency widespread.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.45,
            ec_range=(0.20, 1.50),
            ph_range=(7.0, 8.0),
            sar_range=(1.5, 6.0),
            primary_source="Canal (Krishna/Godavari) + bore-well",
            quality_class="C2-S1 to C3-S2",
            common_contaminants=["nitrate", "fluoride", "TDS"],
            fluoride_risk=0.40,
            arsenic_risk=0.08,
            nitrate_risk=0.45,
            notes="Krishna canal water good quality. Southern coastal bore-wells "
                  "saline/hard. Fluoride elevated in Nellore, Prakasam districts.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Karnataka": StateIntelligence(
        state="Karnataka", region="Peninsular India",
        primary_crops=["rice", "maize", "ragi", "cotton", "soybean",
                       "chickpea"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Coastal / Malnad rice areas (Shivamogga, Hassan)",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.68, "kharif",
                "Coastal Karnataka — very high blast pressure"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.60, "kharif"),
            DiseasePressure("maize_blsb",          "maize", 0.55, "kharif"),
            DiseasePressure("maize_downy_mildew",  "maize", 0.60, "kharif",
                "Sclerophthora sorghi — Kolar, Tumkur"),
            DiseasePressure("chickpea_wilt",       "chickpea",0.50, "rabi"),
            DiseasePressure("soybean_yellow_mosaic","soybean",0.55, "kharif"),
        ],

        insect_pressure=[
            InsectPressure("brown_planthopper",  "rice",   0.55, "kharif"),
            InsectPressure("yellow_stem_borer",  "rice",   0.50, "kharif"),
            InsectPressure("fall_armyworm",      "maize",  0.65, "kharif",
                "FAW — highly destructive in maize Karnataka since 2018"),
            InsectPressure("chickpea_pod_borer", "chickpea",0.60, "rabi"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 7.5),
            ec_ds_m_range=(0.10, 0.40),
            organic_matter_pct=0.70,
            nitrogen_status="low",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.40,
            boron_deficient_pct=0.32,
            sulphur_deficient_pct=0.40,
            iron_deficient_pct=0.22,
            dominant_texture="red to clay loam",
            dominant_soil_type="Red loam (Alfisols) + Black cotton (N Karnataka)",
            notes="Red soils very low P and N. Acidic in coorg/coastal zones. "
                  "Black cotton soils in north Karnataka better fertility.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.38,
            ec_range=(0.15, 1.20),
            ph_range=(7.0, 8.2),
            sar_range=(1.5, 5.0),
            primary_source="Tank + canal + bore-well",
            quality_class="C1-S1 to C2-S1",
            common_contaminants=["fluoride", "nitrate"],
            fluoride_risk=0.45,   # hard rock aquifers
            arsenic_risk=0.05,
            nitrate_risk=0.35,
            notes="Tank-fed water generally excellent. Hard rock bore-wells "
                  "in Deccan have elevated fluoride (Tumkur, Chitradurga).",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "West Bengal": StateIntelligence(
        state="West Bengal", region="Eastern India",
        primary_crops=["rice", "potato", "wheat", "maize", "jute"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Burdwan, Nadia, Hooghly — intensive boro rice",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.60, "kharif"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.65, "kharif"),
            DiseasePressure("rice_false_smut",     "rice",  0.40, "kharif",
                "Ustilaginoidea virens — humid harvest"),
            DiseasePressure("late_blight",         "potato",0.78, "rabi",
                "Highest late blight risk in India — Jalpaiguri, Hooghly, "
                "Burdwan; Phytophthora infestans epidemic in cool-moist winters"),
            DiseasePressure("rice_bacterial_blight","rice", 0.55, "kharif",
                "Cyclone entry via damaged leaves"),
        ],

        insect_pressure=[
            InsectPressure("brown_planthopper",  "rice",   0.60, "kharif"),
            InsectPressure("yellow_stem_borer",  "rice",   0.55, "kharif"),
            InsectPressure("leaf_folder",        "rice",   0.50, "kharif"),
            InsectPressure("potato_aphid",       "potato", 0.65, "rabi",
                "PLRV vector — critical for seed potato production"),
            InsectPressure("potato_tuber_moth",  "potato", 0.45, "rabi"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 7.5),
            ec_ds_m_range=(0.10, 0.40),
            organic_matter_pct=1.20,      # higher OM than most states
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="low-medium",
            zinc_deficient_pct=0.35,
            boron_deficient_pct=0.38,
            sulphur_deficient_pct=0.30,
            iron_deficient_pct=0.20,
            dominant_texture="loam to clay loam",
            dominant_soil_type="New Alluvium (Inceptisols) + Laterite (W Bengal)",
            notes="Generally better fertility than Deccan. Intensively cultivated. "
                  "K being depleted under triple cropping. "
                  "Lateral soils (Birbhum, Bankura) are low fertility.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.25,
            ec_range=(0.10, 0.50),
            ph_range=(6.5, 7.8),
            sar_range=(1.0, 3.0),
            primary_source="Canal + tube-well + river",
            quality_class="C1-S1",
            common_contaminants=["arsenic", "iron"],
            fluoride_risk=0.10,
            arsenic_risk=0.70,   # highest arsenic state — Ganga delta aquifer
            nitrate_risk=0.20,
            notes="CRITICAL: Arsenic contamination in tube-well water — "
                  "Murshidabad, Malda, North/South 24 Parganas. "
                  "WHO limit 10 μg/L frequently exceeded. "
                  "High Fe (>1 mg/L) common in shallow tube-wells.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Odisha": StateIntelligence(
        state="Odisha", region="Eastern India",
        primary_crops=["rice", "maize", "chickpea", "mustard", "groundnut"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Coastal plains — Cuttack, Jagatsinghpur, Kendrapara",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.75, "kharif",
                "Highest blast risk state in India — M. oryzae endemic"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.60, "kharif"),
            DiseasePressure("rice_bacterial_blight","rice", 0.55, "kharif",
                "Cyclone-induced — Odisha coast highly vulnerable"),
            DiseasePressure("maize_blsb",          "maize", 0.50, "kharif"),
        ],

        insect_pressure=[
            InsectPressure("gall_midge",         "rice",  0.65, "kharif",
                "Orseolia oryzae — endemic in coastal Odisha"),
            InsectPressure("yellow_stem_borer",  "rice",  0.60, "kharif"),
            InsectPressure("brown_planthopper",  "rice",  0.55, "kharif"),
            InsectPressure("fall_armyworm",      "maize", 0.55, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.0, 7.0),
            ec_ds_m_range=(0.10, 0.30),
            organic_matter_pct=0.75,
            nitrogen_status="low",
            phosphorus_status="low",
            potassium_status="low",
            zinc_deficient_pct=0.38,
            boron_deficient_pct=0.45,
            sulphur_deficient_pct=0.35,
            iron_deficient_pct=0.28,
            dominant_texture="sandy loam to clay",
            dominant_soil_type="Red laterite (upland) + Coastal alluvium",
            notes="Acidic red laterite soils — P fixation. "
                  "Boron deficiency critical in rice. "
                  "Low fertility tribal uplands (60 % of state area).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.20,
            ec_range=(0.10, 0.40),
            ph_range=(6.5, 7.8),
            sar_range=(0.5, 3.0),
            primary_source="Canal (Mahanadi/Brahmani) + tank",
            quality_class="C1-S1",
            common_contaminants=["iron", "fluoride (coastal)"],
            fluoride_risk=0.20,
            arsenic_risk=0.10,
            nitrate_risk=0.15,
            notes="Canal water generally good. "
                  "Coastal saline intrusion in low-lying areas.",
        ),
    ),

    # ════════════════════════════════════════════════════════════════════
    "Assam": StateIntelligence(
        state="Assam", region="NE India",
        primary_crops=["rice", "maize", "mustard", "jute", "tea"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli", "rice",
                ["bispyribac-sodium"],
                "ALS",
                "Upper Brahmaputra valley",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("rice_blast",          "rice",  0.75, "kharif",
                "Very high blast risk — humid tropical conditions"),
            DiseasePressure("rice_sheath_blight",  "rice",  0.65, "kharif"),
            DiseasePressure("rice_bacterial_blight","rice", 0.60, "kharif",
                "Flood damage + bacterial entry — Brahmaputra floods"),
            DiseasePressure("maize_downy_mildew",  "maize", 0.55, "kharif"),
        ],

        insect_pressure=[
            InsectPressure("yellow_stem_borer",  "rice",  0.70, "kharif",
                "Primary rice pest in Assam — very high pressure"),
            InsectPressure("brown_planthopper",  "rice",  0.60, "kharif"),
            InsectPressure("gall_midge",         "rice",  0.55, "kharif"),
            InsectPressure("leaf_folder",        "rice",  0.50, "kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(4.5, 6.5),   # very acidic
            ec_ds_m_range=(0.05, 0.20),
            organic_matter_pct=2.50,  # high OM under humid tropics
            nitrogen_status="medium-high",
            phosphorus_status="low",  # P fixed in acid soils
            potassium_status="low",
            zinc_deficient_pct=0.25,
            boron_deficient_pct=0.40,
            sulphur_deficient_pct=0.30,
            iron_deficient_pct=0.10,  # high Fe in acid soils
            dominant_texture="loam to clay loam",
            dominant_soil_type="Acidic Alluvium (Inceptisols) + Red laterite",
            notes="Highly acidic soils — pH 4.5–5.5 common. "
                  "Molybdenum deficiency (critical for legumes). "
                  "Al toxicity limits crop establishment. "
                  "High OM from tropical vegetation but P/K low. "
                  "Agriculture.Institute 2025: NE India — Mo and Al toxicity.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.12,
            ec_range=(0.05, 0.25),
            ph_range=(6.0, 7.2),
            sar_range=(0.3, 2.0),
            primary_source="River + rainfall-dependent",
            quality_class="C1-S1",
            common_contaminants=["iron", "aluminium"],
            fluoride_risk=0.05,
            arsenic_risk=0.20,  # Brahmaputra basin arsenic
            nitrate_risk=0.10,
            notes="Generally soft, low-EC water. High Fe and Al from "
                  "acidic laterite soils. Arsenic in alluvial aquifers.",
        ),
        agronomic_notes="Highly acidic soils — lime application critical. "
                         "Flooding risk from Brahmaputra — Sub1 varieties needed.",
    ),

    # ════════════════════════════════════════════════════════════════════
    "Gujarat": StateIntelligence(
        state="Gujarat", region="Western India",
        primary_crops=["cotton", "wheat", "groundnut", "sugarcane", "maize",
                       "chickpea"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Phalaris minor", "wheat",
                ["isoproturon"],
                "PSII",
                "North Gujarat wheat belt",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("cotton_clcv",         "cotton", 0.70, "kharif",
                "Cotton Leaf Curl Virus — most devastating cotton disease"),
            DiseasePressure("alternaria_blight",   "wheat",  0.35, "rabi"),
            DiseasePressure("sclerotinia",         "mustard",0.30, "rabi",
                "Sclerotinia sclerotiorum — occasional"),
            DiseasePressure("charcoal_rot",        "groundnut",0.45,"kharif",
                "Macrophomina — dry late season"),
        ],

        insect_pressure=[
            InsectPressure("cotton_bollworm",     "cotton",  0.70, "kharif"),
            InsectPressure("whitefly",            "cotton",  0.65, "kharif",
                "Bemisia tabaci — CLCV + direct"),
            InsectPressure("pink_bollworm",       "cotton",  0.55, "kharif",
                "Pectinophora gossypiella — Bt resistance confirmed"),
            InsectPressure("groundnut_leafminer", "groundnut",0.45,"kharif"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.2, 8.8),
            ec_ds_m_range=(0.20, 2.00),
            organic_matter_pct=0.55,
            nitrogen_status="low-medium",
            phosphorus_status="low",
            potassium_status="medium",
            zinc_deficient_pct=0.45,
            boron_deficient_pct=0.28,
            sulphur_deficient_pct=0.38,
            iron_deficient_pct=0.12,
            dominant_texture="clay to sandy",
            dominant_soil_type="Vertisols + Aridisols + Saline soils (coastal)",
            notes="Coastal saline soils in Saurashtra. "
                  "Alkaline soils limit micronutrient availability. "
                  "P deficiency universal. Low OM.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.65,
            ec_range=(0.25, 4.00),
            ph_range=(7.5, 8.8),
            sar_range=(3.0, 20.0),
            primary_source="Canal (Narmada) + tube-well",
            quality_class="C2-S1 to C4-S3",
            common_contaminants=["fluoride", "sodium", "boron"],
            fluoride_risk=0.55,
            arsenic_risk=0.08,
            nitrate_risk=0.30,
            notes="Coastal Saurashtra tube-wells saline (EC > 2 dS/m). "
                  "Fluoride very high in Sabarkantha, Gandhinagar. "
                  "Narmada canal water excellent quality.",
        ),
    ),
}


# ──────────────────────────────────────────────────────────────────────────────
#  ACCESSOR FUNCTIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_state_intel(state: str) -> StateIntelligence | None:
    return LOCATION_INTELLIGENCE.get(state)


def list_states() -> list[str]:
    return sorted(LOCATION_INTELLIGENCE.keys())


def get_weed_hr_factor(state: str, crop: str) -> float:
    """
    Returns a 0–1 herbicide resistance factor for the given state + crop.
    0 = no HR weeds  /  1 = severe HR weed problem.
    Used in the weed_penalty() function.
    """
    intel = LOCATION_INTELLIGENCE.get(state)
    if not intel:
        return 0.0
    relevant = [c.severity for c in intel.weed_hr_cases
                if c.crop_system == crop]
    return max(relevant, default=0.0)


def get_disease_risk(state: str, crop: str) -> dict[str, float]:
    """
    Returns {disease_key: risk_level} for a state + crop combination.
    risk_level is already pre-scaled 0–1.
    """
    intel = LOCATION_INTELLIGENCE.get(state)
    if not intel:
        return {}
    return {d.disease_key: d.risk_level
            for d in intel.disease_pressure if d.crop == crop}


def get_insect_risk(state: str, crop: str) -> dict[str, float]:
    intel = LOCATION_INTELLIGENCE.get(state)
    if not intel:
        return {}
    return {i.pest_name: i.risk_level
            for i in intel.insect_pressure if i.crop == crop}


def get_soil_profile(state: str) -> SoilFertilityProfile | None:
    intel = LOCATION_INTELLIGENCE.get(state)
    return intel.soil_fertility if intel else None


def get_water_profile(state: str) -> IrrigationWaterProfile | None:
    intel = LOCATION_INTELLIGENCE.get(state)
    return intel.irrigation_water if intel else None
