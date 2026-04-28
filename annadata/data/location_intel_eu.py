"""
EU / European Location Intelligence Database — Germany first.

Literature sources
──────────────────────────────────────────────────────────────────────────
Soil:
  Kühn et al. (2012) Soil Tillage Res.: soil organic carbon German agricultural soils
  Steinmann & Dobers (2013) Precision Agric.: spatial soil variability North Germany
  Sieling et al. (2003) Eur J Agron: yield response + soil status N Germany
  Thünen Atlas (2023): agricultural land-use and soil organic carbon maps Germany
  UBA (German Environment Agency, 2022): soil monitoring programme data
  BGR (Federal Institute for Geosciences) BUEK-200 soil map Germany

Disease / Pest:
  JKI (Julius Kühn-Institut) Crop Health Monitoring Reports 2020–2023
  Fones & Gurr (2015) Mol Plant Pathol: Septoria tritici blotch — yield losses 5–50 %
  Bearchell et al. (2005) PNAS: UK/Germany yellow rust 1843–2003
  Murray et al. (2012) Eur J Plant Path: climate drivers Phoma stem canker
  Schoeny & Lucas (1999) Phytopathology: Sclerotinia oilseed rape
  Hausladen & Leiminger (2017) JfK: potato late blight epidemics Bavaria
  Donahoo et al. (EPPO 2022): Cercospora leaf spot sugar beet EU

Weed / Herbicide resistance:
  Fischer et al. (2015) WEED Research: Alopecurus myosuroides resistance Germany
  Heap I. (2024) International Herbicide-Resistant Weed Database — Germany entries
  Beffa et al. (2012) Pest Biochem Physiol: ACCase resistance Alopecurus
  Kuck & Meissner (2018, JfK): Galium aparine survey N Germany
  Balgheim (2023, Julius Kühn-Institut): HR monitoring wheat Germany

Water quality:
  EEA (2022) European waters report — nitrate contamination
  BMUB (2021) Nitrates Action Programme Germany: groundwater nitrate levels
  DWA (German Water Association) guidelines
──────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations
from .location_intel import (
    StateIntelligence, WeedResistanceCase, DiseasePressure,
    InsectPressure, SoilFertilityProfile, IrrigationWaterProfile,
)

# ─────────────────────────────────────────────────────────────────────────────
#  GERMANY — 6 major agricultural regions
# ─────────────────────────────────────────────────────────────────────────────

EU_LOCATION_INTELLIGENCE: dict[str, StateIntelligence] = {

    # ═══════════════════════════════════════════════════════════════════════
    "germany_saxony_anhalt": StateIntelligence(
        state="Saxony-Anhalt (Magdeburger Börde)",
        region="Central Germany",
        primary_crops=["wheat", "barley", "sugarbeet", "rapeseed", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop", "clodinafop", "tralkoxydim",       # ACCase
                 "mesosulfuron+iodosulfuron", "pyroxasulam"],      # ALS
                "ACCase / ALS",
                "Detected in river valleys; lower prevalence than NW Germany "
                "due to drier climate (Fischer et al. 2015)",
                severity=0.30,
            ),
            WeedResistanceCase(
                "Bromus sterilis (sterile brome)",
                "wheat",
                ["mesosulfuron+iodosulfuron"],
                "ALS",
                "Emerging problem in Chernozem zone; Heap 2024",
                severity=0.20,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch", "wheat", 0.70, "both",
                "Zymoseptoria tritici — most important wheat disease Germany; "
                "yield loss 20–35 % untreated in high-pressure years "
                "(Fones & Gurr 2015 Mol Plant Pathol)"),
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.55, "rabi",
                "Puccinia striiformis — resurging since 2014; new races Warrior/Kranich; "
                "Börde warm springs increase risk (Bearchell et al. 2005)"),
            DiseasePressure("wheat_leaf_rust",     "wheat", 0.50, "both",
                "Puccinia triticina — moderate annual risk"),
            DiseasePressure("fusarium_head_blight","wheat", 0.45, "both",
                "Fusarium graminearum dominant; DON mycotoxin risk; wet May-June"),
            DiseasePressure("phoma_stem_canker",   "rapeseed", 0.65, "both",
                "Leptosphaeria maculans — major stem canker, 5–30 % loss; "
                "most rapeseed area in Germany treated (Murray et al. 2012)"),
            DiseasePressure("sclerotinia_rapeseed","rapeseed", 0.55, "both",
                "Sclerotinia sclerotiorum — stem rot; risk highest in wet flowering "
                "(Schoeny & Lucas 1999)"),
            DiseasePressure("cercospora_leaf_spot","sugarbeet", 0.60, "kharif",
                "Cercospora beticola — major issue in Börde; high humidity June-Aug "
                "(Donahoo et al. EPPO 2022); yield loss up to 50 %"),
        ],

        insect_pressure=[
            InsectPressure("cereal_aphids", "wheat", 0.55, "both",
                "Sitobion avenae + Metopolophium dirhodum — BYDV vector; "
                "warm autumns increase autumn infection (JKI 2022)"),
            InsectPressure("pollen_beetle", "rapeseed", 0.65, "both",
                "Meligethes aeneus — pyrethroid resistance widespread; "
                "early flowering rape at highest risk (JKI monitoring 2021)"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.60, "both",
                "Psylliodes chrysocephala — larval stem mining, yield loss 10–30 %; "
                "neonicotinoid ban (2018) increased pressure significantly"),
            InsectPressure("beet_aphid", "sugarbeet", 0.50, "both",
                "Myzus persicae — primary BYD virus vector in sugar beet; "
                "neonicotinoid seed treatment ban increases uncontrolled spread"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.8, 7.5),
            ec_ds_m_range=(0.15, 0.40),
            organic_matter_pct=3.20,   # Chernozem: high OM (Kühn et al. 2012)
            nitrogen_status="high",
            phosphorus_status="medium-high",
            potassium_status="high",
            zinc_deficient_pct=0.12,
            boron_deficient_pct=0.08,
            sulphur_deficient_pct=0.25,  # atmospheric S deposition decline post-1990
            iron_deficient_pct=0.05,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Chernozem (Schwarzerde) — highest quality arable soil in Germany",
            notes="Magdeburger Börde: 90+ soil quality index (Ackerzahl). "
                  "Continental climate (520 mm/yr). Drought stress increasing under climate change. "
                  "Long-term N surplus → high residual NO3 in subsoil. "
                  "S deficiency emerged after clean-air legislation (Sieling et al. 2003).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.50,
            ec_range=(0.30, 0.80),
            ph_range=(7.0, 7.8),
            sar_range=(0.5, 2.0),
            primary_source="Groundwater (mostly rain-fed; some supplementary irrigation)",
            quality_class="C2-S1 (good quality, low salinity)",
            common_contaminants=["nitrate"],
            fluoride_risk=0.05,
            arsenic_risk=0.02,
            nitrate_risk=0.55,  # EEA 2022: Börde groundwater NO3 often 40-90 mg/L
            notes="Primarily rainfed. Supplementary irrigation from groundwater. "
                  "Nitrate contamination (BMUB 2021): 35–50 % of monitoring sites > 50 mg/L.",
        ),

        agronomic_notes=(
            "Most productive arable region in Germany (Ackerzahl ~90). "
            "Continental climate: warm/dry summers risk increasing drought stress. "
            "Key BODIUM model application site: Chernozem soil structure + C dynamics. "
            "References: ZALF research platform; Thünen Institute Bernburg; "
            "DFG Priority Programme 1685 'Ecosystem Nutrition' (Saxony-Anhalt sites)."
        ),
    ),

    # ═══════════════════════════════════════════════════════════════════════
    "germany_bavaria": StateIntelligence(
        state="Bavaria (Bayern)",
        region="South Germany",
        primary_crops=["wheat", "barley", "maize", "sugarbeet", "potato", "hops"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop", "mesosulfuron+iodosulfuron"],
                "ACCase / ALS",
                "Southern Bavaria river basins; Heap 2024; medium pressure",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "pyroxasulam", "florasulam"],
                "ALS",
                "Widespread in cereals; ALS-resistant biotypes confirmed in Franconia "
                "(Fischer et al. 2015)",
                severity=0.40,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch", "wheat", 0.75, "both",
                "Z. tritici — highest risk of any German region due to Atlantic influence; "
                "leaf wetness periods >20 h common (Fones & Gurr 2015)"),
            DiseasePressure("fusarium_head_blight","wheat", 0.55, "both",
                "F. graminearum + F. culmorum; wet May critical; Bavarian data JKI 2022"),
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.45, "rabi",
                "Increasing since 2014; new race Kranich prominent in S Germany"),
            DiseasePressure("wheat_powdery_mildew","wheat", 0.40, "both",
                "Blumeria graminis — significant in high-input cereals"),
            DiseasePressure("phoma_stem_canker",   "rapeseed", 0.60, "both",
                "Leptosphaeria maculans — mild winters favour overwintering; "
                "25–30 % loss potential in susceptible varieties"),
            DiseasePressure("potato_late_blight",  "potato",  0.70, "kharif",
                "Phytophthora infestans — major risk in wet Bavarian summers; "
                "yield loss 30–70 % untreated (Hausladen & Leiminger 2017 JfK)"),
            DiseasePressure("cercospora_leaf_spot","sugarbeet", 0.55, "kharif",
                "C. beticola — risk in SE Bavaria; humid July-August"),
        ],

        insect_pressure=[
            InsectPressure("cereal_aphids",     "wheat",    0.50, "both",
                "Sitobion avenae; BYDV vector pressure moderate"),
            InsectPressure("pollen_beetle",     "rapeseed", 0.65, "both",
                "Meligethes aeneus — pyrethroid resistance; JKI monitoring"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.55, "both",
                "Psylliodes chrysocephala — increased since neonicotinoid ban 2018"),
            InsectPressure("colorado_potato_beetle", "potato", 0.60, "kharif",
                "Leptinotarsa decemlineata — defoliation risk; insecticide resistance "
                "developing in S Bavaria"),
            InsectPressure("wireworm",          "potato",   0.40, "both",
                "Agriotes spp. — significant in grassland-converted fields"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.3, 7.2),
            ec_ds_m_range=(0.15, 0.50),
            organic_matter_pct=2.80,
            nitrogen_status="medium-high",
            phosphorus_status="medium-high",
            potassium_status="medium",
            zinc_deficient_pct=0.10,
            boron_deficient_pct=0.15,
            sulphur_deficient_pct=0.22,
            iron_deficient_pct=0.06,
            dominant_texture="loam",
            dominant_soil_type="Luvisol (Parabraunerde) — dominant type in Bavaria",
            notes="Diverse soils: Luvisols in central plateau, Cambisols in Alpine foothills, "
                  "alluvial soils in Danube valley. High OM due to Atlantic precipitation "
                  "(Kühn et al. 2012). Periodic drought stress in continental eastern Bavaria.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.35,
            ec_range=(0.20, 0.60),
            ph_range=(6.8, 7.5),
            sar_range=(0.3, 1.5),
            primary_source="Rain-fed (800–1200 mm/yr alpine margins); some groundwater",
            quality_class="C1-S1 (excellent quality)",
            common_contaminants=["nitrate (hotspots near Augsburg/Ingolstadt)"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.35,
            notes="Generally high rainfall reduces irrigation need. "
                  "Alpine groundwater high quality; lowland some NO3 hotspots.",
        ),

        agronomic_notes=(
            "Bavaria largest German federal state (1.3 M ha arable). "
            "Atlantic-continental climate gradient: W Bavaria wetter, E Bavaria drier. "
            "Strong hop and specialty crop tradition. "
            "LfL Bayern (Bavarian State Research Centre) key research institution — "
            "good model validation dataset potential."
        ),
    ),

    # ═══════════════════════════════════════════════════════════════════════
    "germany_lower_saxony": StateIntelligence(
        state="Lower Saxony (Niedersachsen)",
        region="North Germany",
        primary_crops=["wheat", "potato", "sugarbeet", "rapeseed", "maize", "barley"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",       # ACCase
                 "mesosulfuron+iodosulfuron", "pyroxasulam",         # ALS
                 "flupyrsulfuron", "sulfosulfuron"],
                "ACCase + ALS (dual resistance)",
                "Highest density in Hanover-Braunschweig area, Leine valley; "
                "up to 500 seeds/m² in resistant fields (Fischer et al. 2015 WEED Res)",
                severity=0.55,
            ),
            WeedResistanceCase(
                "Galium aparine (cleavers)",
                "wheat",
                ["mecoprop-P", "fluroxypyr"],
                "Synthetic auxin",
                "Common broad-leaf weed in cereals; partial resistance documented; "
                "Kuck & Meissner 2018 JfK survey",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "florasulam", "pyroxasulam"],
                "ALS",
                "High prevalence in northern Lower Saxony (Heap 2024)",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch", "wheat", 0.80, "both",
                "Z. tritici — highest risk in Germany; Atlantic climate with long leaf "
                "wetness periods 600–900 mm/yr precipitation; yield loss 25–45 % "
                "untreated in epidemic years (Fones & Gurr 2015)"),
            DiseasePressure("wheat_yellow_rust",   "wheat", 0.50, "both",
                "P. striiformis — maritime climate favours rust; new races post-2014"),
            DiseasePressure("fusarium_head_blight","wheat", 0.50, "both",
                "F. graminearum — wet May/June common; DON >1.25 mg/kg risk"),
            DiseasePressure("wheat_eyespot",       "wheat", 0.45, "both",
                "Oculimacula yallundae/acuformis — eyespot/lodging; cool-wet springs"),
            DiseasePressure("phoma_stem_canker",   "rapeseed", 0.70, "both",
                "L. maculans — highest risk in Germany; Atlantic climate, mild winters; "
                "yield loss up to 30 % in susceptible varieties (Murray et al. 2012)"),
            DiseasePressure("sclerotinia_rapeseed","rapeseed", 0.65, "both",
                "S. sclerotiorum — wet flowering period; major economic loss"),
            DiseasePressure("potato_late_blight",  "potato",  0.80, "kharif",
                "Ph. infestans — primary potato disease NW Germany; wet climate; "
                "yield loss 30–80 % untreated; metalaxyl resistance of mefenoxam "
                "documented in some populations (Hausladen & Leiminger 2017)"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",     "rapeseed", 0.70, "both",
                "M. aeneus — pyrethroid resistance very high in northern Germany; "
                "monitoring threshold often exceeded in March-April"),
            InsectPressure("cabbage_stem_flea_beetle","rapeseed", 0.70, "both",
                "Psylliodes chrysocephala — most severe pressure in NW Germany; "
                "post-neonicotinoid ban (2018) population explosion reported"),
            InsectPressure("cereal_aphids",     "wheat",    0.55, "both",
                "S. avenae — BYDV vector; warm autumn infections critical"),
            InsectPressure("colorado_potato_beetle","potato", 0.65, "kharif",
                "L. decemlineata — routine pest; resistance to organophosphates"),
            InsectPressure("cabbage_root_fly",  "rapeseed", 0.40, "both",
                "Delia radicum — root damage at establishment"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.8, 6.8),
            ec_ds_m_range=(0.15, 0.45),
            organic_matter_pct=2.90,
            nitrogen_status="medium-high",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.12,
            boron_deficient_pct=0.18,
            sulphur_deficient_pct=0.30,
            iron_deficient_pct=0.08,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Luvisol / Cambisol (Parabraunerde/Braunerde); "
                               "alluvial Gleysols in river valleys",
            notes="Diverse landscape: Geest (sandy heathland) → Börde (loess). "
                  "Sandy Geest soils: low P retention, leaching risk. "
                  "Loess Börde soils (Hildesheim, Braunschweig): highest yields. "
                  "S deficiency critical after 1990 clean-air reductions (Sieling 2003).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.45,
            ec_range=(0.25, 0.80),
            ph_range=(6.8, 7.6),
            sar_range=(0.5, 2.0),
            primary_source="Groundwater (potato irrigation common), rain-fed cereals",
            quality_class="C2-S1 (good)",
            common_contaminants=["nitrate"],
            fluoride_risk=0.04,
            arsenic_risk=0.03,
            nitrate_risk=0.60,  # EEA 2022: many Lower Saxony groundwater sites >50 mg/L NO3
            notes="Atlantic climate: 650–900 mm/yr. Supplementary potato irrigation common "
                  "June-August. Groundwater nitrate pressure (BMUB 2021) — intensive potato "
                  "regions Hannover/Wolfenbüttel/Hildesheim exceed EU nitrate thresholds.",
        ),

        agronomic_notes=(
            "Germany's main potato and vegetable production state (30% national potato). "
            "Atlantic climate: high Septoria and Phoma risk; black-grass resistance hotspot. "
            "Key research: University of Göttingen, Thünen Institute Brunswick. "
            "Relevant for BODIUM: Atlantic Luvisol/Cambisol soil dynamics research; "
            "LTE (Long-Term Experiment) at Rotthalmünster and Hannover for model validation."
        ),
    ),

    # ═══════════════════════════════════════════════════════════════════════
    "germany_nrw": StateIntelligence(
        state="North Rhine-Westphalia (NRW)",
        region="West Germany",
        primary_crops=["wheat", "sugarbeet", "rapeseed", "potato", "barley", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden", "cycloxydim",  # ACCase
                 "mesosulfuron+iodosulfuron", "pyroxasulam", "florasulam",   # ALS
                 "flupyrsulfuron"],
                "ACCase + ALS + metabolic resistance (triple resistance)",
                "Most severe HR region in Germany; Rhine plain, Cologne Bay; "
                "Fischer et al. (2015): >70 % fields with resistant biotypes; Heap 2024; "
                "Balgheim (2023 JfK): metabolic resistance detected — no registered herbicide "
                "fully controls some biotypes",
                severity=0.75,
            ),
            WeedResistanceCase(
                "Avena fatua (wild oats)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "ACCase resistance confirmed in Rhine region; Heap 2024",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Galium aparine (cleavers)",
                "wheat",
                ["mecoprop-P", "fluroxypyr", "MCPA"],
                "Synthetic auxin",
                "Widespread; Kuck & Meissner 2018; difficult to control with auxin herbicides",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat", 0.85, "both",
                "Z. tritici — highest incidence Germany; Cologne/Rhine lowlands; "
                "high-humidity Atlantic climate; yield loss 30–50 % in untreated crops "
                "(Fones & Gurr 2015); fungicide spend >100 €/ha routine"),
            DiseasePressure("wheat_yellow_rust",  "wheat", 0.55, "both",
                "New race Warrior/Kranich — epidemic years 2014, 2018; "
                "higher risk than 5-yr avg pre-2010"),
            DiseasePressure("wheat_eyespot",      "wheat", 0.55, "both",
                "O. yallundae/acuformis — lodging risk; wet Atlantic winters"),
            DiseasePressure("fusarium_head_blight","wheat", 0.50, "both",
                "Wet May-June conditions common; DON contamination risk"),
            DiseasePressure("phoma_stem_canker",  "rapeseed", 0.70, "both",
                "L. maculans — consistently high risk; mild wet winters; "
                "Murray et al. 2012"),
            DiseasePressure("sclerotinia_rapeseed","rapeseed",0.65, "both",
                "Very wet climate — repeated protective fungicide applications needed"),
            DiseasePressure("cercospora_leaf_spot","sugarbeet",0.65, "kharif",
                "C. beticola — warm humid July-August Rhine lowlands; Donahoo EPPO 2022"),
            DiseasePressure("rhizoctonia_root_rot","sugarbeet",0.40, "kharif",
                "R. solani — wet soils risk; especially after maize"),
        ],

        insect_pressure=[
            InsectPressure("cereal_aphids",     "wheat",    0.60, "both",
                "S. avenae + R. padi — BYDV vector pressure high; mild winters"),
            InsectPressure("pollen_beetle",     "rapeseed", 0.75, "both",
                "M. aeneus — worst in W Germany; pyrethroid resistance near-universal; "
                "JKI 2022: resistance index >1000 in Cologne area"),
            InsectPressure("cabbage_stem_flea_beetle","rapeseed",0.70,"both",
                "P. chrysocephala — post-neonicotinoid ban; most problematic in NRW"),
            InsectPressure("beet_aphid",        "sugarbeet",0.55, "kharif",
                "M. persicae — BYD virus vector; neonicotinoid seed treatment ban "
                "since 2021 — increased uncontrolled spread"),
            InsectPressure("colorado_potato_beetle","potato",0.55, "kharif",
                "L. decemlineata — routine control needed"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.2, 7.0),
            ec_ds_m_range=(0.20, 0.60),
            organic_matter_pct=2.50,
            nitrogen_status="high",
            phosphorus_status="medium-high",
            potassium_status="medium-high",
            zinc_deficient_pct=0.08,
            boron_deficient_pct=0.12,
            sulphur_deficient_pct=0.28,
            iron_deficient_pct=0.06,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Luvisol (Parabraunerde) — loess plains; some alluvial soils",
            notes="Cologne Bay loess — highly productive. Rhine alluvium very fertile. "
                  "Heavy N surplus from intensive livestock → groundwater NO3 issue. "
                  "Nitrates Action Programme compliance monitoring ongoing (BMUB 2021).",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.55,
            ec_range=(0.30, 1.00),
            ph_range=(7.0, 7.8),
            sar_range=(0.5, 2.5),
            primary_source="Rain-fed primarily (800–1000 mm/yr); Rhine water for some horticulture",
            quality_class="C2-S1 (good)",
            common_contaminants=["nitrate", "pesticide residues"],
            fluoride_risk=0.04,
            arsenic_risk=0.02,
            nitrate_risk=0.65,
            notes="Most intensive livestock density in Germany → severe groundwater NO3. "
                  "Rhine tributaries: some pesticide loading from horticulture.",
        ),

        agronomic_notes=(
            "NRW: most severe Alopecurus HR in Germany (metabolic + target-site resistance). "
            "Key BODIUM relevance: Atlantic Luvisol soils, intensive cropping, "
            "soil structure degradation from heavy machinery. "
            "Research: University of Bonn, Forschungszentrum Jülich, "
            "Landwirtschaftskammer NRW field trial network."
        ),
    ),

    # ═══════════════════════════════════════════════════════════════════════
    "germany_mecklenburg": StateIntelligence(
        state="Mecklenburg-Vorpommern (MV)",
        region="Northeast Germany",
        primary_crops=["wheat", "rapeseed", "rye", "barley", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "mesosulfuron+iodosulfuron"],
                "ACCase / ALS",
                "Lower density than W Germany; expanding from SW; Heap 2024",
                severity=0.25,
            ),
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "pyroxasulam", "florasulam"],
                "ALS",
                "Most prevalent HR grass weed in MV and Brandenburg; "
                "Fischer et al. 2015; widespread coastal influence",
                severity=0.50,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat", 0.70, "both",
                "Z. tritici — moderate-high; Baltic coast moisture; JKI monitoring"),
            DiseasePressure("wheat_yellow_rust",  "wheat", 0.45, "both",
                "Cool maritime climate; new races increasing; JKI 2022"),
            DiseasePressure("fusarium_head_blight","wheat", 0.40, "both",
                "F. graminearum — moderate risk; wet May variable"),
            DiseasePressure("phoma_stem_canker",  "rapeseed", 0.60, "both",
                "L. maculans — major oilseed rape region; consistent risk "
                "(Murray et al. 2012)"),
            DiseasePressure("sclerotinia_rapeseed","rapeseed", 0.55, "both",
                "S. sclerotiorum — wet Baltic spring; economic threshold exceeded ~60 % years"),
            DiseasePressure("barley_net_blotch",  "barley", 0.50, "both",
                "Pyrenophora teres — common in spring/winter barley MV"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",     "rapeseed", 0.65, "both",
                "M. aeneus — pyrethroid resistance high; major MV rapeseed threat"),
            InsectPressure("cabbage_stem_flea_beetle","rapeseed",0.65,"both",
                "P. chrysocephala — post-neonicotinoid issues as elsewhere"),
            InsectPressure("cereal_aphids",     "wheat",    0.45, "both",
                "Moderate BYDV vector pressure"),
            InsectPressure("slug",              "rapeseed", 0.45, "both",
                "Deroceras reticulatum — wet Baltic autumns; establishment damage"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.0, 7.0),
            ec_ds_m_range=(0.15, 0.40),
            organic_matter_pct=2.60,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.14,
            boron_deficient_pct=0.20,
            sulphur_deficient_pct=0.32,
            iron_deficient_pct=0.08,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Luvisol / Cambisol; glacial till with lake sediments",
            notes="Post-glacial soils: variable texture. Profitable large-scale farms (>1000 ha). "
                  "Lower OM than Börde; S deficiency common post-1990 (Sieling 2003). "
                  "Increasing drought risk: Baltic lowlands vulnerable to dry summers.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.40,
            ec_range=(0.20, 0.65),
            ph_range=(6.8, 7.5),
            sar_range=(0.3, 1.5),
            primary_source="Rain-fed (550–700 mm/yr); groundwater for some specialty crops",
            quality_class="C2-S1 (good quality)",
            common_contaminants=["nitrate (moderate)"],
            fluoride_risk=0.04,
            arsenic_risk=0.02,
            nitrate_risk=0.40,
            notes="Baltic maritime influence; moderate precipitation. Less NO3 pressure than W Germany.",
        ),

        agronomic_notes=(
            "Largest average farm size in Germany (>200 ha). "
            "Major oilseed rape and cereal producer. "
            "Key BODIUM relevance: post-reunification land-use change, large-scale "
            "mechanisation effects on soil structure. "
            "Research: University of Rostock, Leibniz Institute (ZALF) Müncheberg — "
            "ZALF Brandenburg/MV border long-term experiments relevant to BODIUM validation."
        ),
    ),

    # ═══════════════════════════════════════════════════════════════════════
    "germany_brandenburg": StateIntelligence(
        state="Brandenburg",
        region="Northeast Germany",
        primary_crops=["rye", "potato", "maize", "rapeseed", "wheat"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "rye",
                ["mesosulfuron+iodosulfuron", "pyroxasulam", "florasulam",
                 "clodinafop-P"],
                "ALS + ACCase",
                "Most HR-affected state in Germany for Apera; "
                "Fischer et al. 2015: > 60 % fields positive in Brandenburg wheat/rye",
                severity=0.65,
            ),
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron"],
                "ALS",
                "ALS resistance in maize rotation areas; Heap 2024",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat", 0.60, "both",
                "Moderate risk; continental climate drier; Z. tritici lower than W Germany"),
            DiseasePressure("rhizoctonia_root_rot", "potato",  0.55, "kharif",
                "R. solani — stem canker and black scurf; common in sandy soils; "
                "cool wet springs increase risk"),
            DiseasePressure("potato_late_blight",  "potato",  0.65, "kharif",
                "Ph. infestans — major issue in Brandenburg potato areas; "
                "occasional epidemic years (Hausladen & Leiminger 2017)"),
            DiseasePressure("phoma_stem_canker",  "rapeseed", 0.55, "both",
                "L. maculans — moderate risk; drier climate reduces severity vs W Germany"),
            DiseasePressure("barley_net_blotch",  "barley",  0.45, "both",
                "P. teres f. teres — common in spring barley Brandenburg"),
            DiseasePressure("fusarium_head_blight","wheat",  0.35, "both",
                "Lower risk than W Germany; drier flowering period typical"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",       "rapeseed", 0.60, "both",
                "M. aeneus — pyrethroid resistance high; standard problem in Brandenburg"),
            InsectPressure("colorado_potato_beetle","potato", 0.70, "kharif",
                "L. decemlineata — most problematic pest in Brandenburg potato; "
                "some resistance to older insecticide classes"),
            InsectPressure("wireworm",            "potato",  0.55, "kharif",
                "Agriotes spp. — serious problem post-grassland conversion; "
                "no chemical seed treatment allowed → difficult control"),
            InsectPressure("cabbage_stem_flea_beetle","rapeseed",0.60,"both",
                "P. chrysocephala — serious since neonicotinoid ban"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 6.5),
            ec_ds_m_range=(0.10, 0.35),
            organic_matter_pct=1.80,   # lowest in Germany; sandy Arenosol/Podzol
            nitrogen_status="low-medium",
            phosphorus_status="low-medium",
            potassium_status="low",
            zinc_deficient_pct=0.22,
            boron_deficient_pct=0.25,
            sulphur_deficient_pct=0.38,
            iron_deficient_pct=0.05,
            dominant_texture="sandy to sandy loam",
            dominant_soil_type="Arenosol / Podzol — diluvial (glacial outwash) sandy soils; "
                               "some Luvisols in river valleys",
            notes="Lowest soil quality in Germany (Ackerzahl 25–40). "
                  "High leaching risk: N, K, Mg losses common. "
                  "Drought stress increasing critically: 2018/2019 deficits -200 to -250 mm. "
                  "Key BODIUM site: ZALF Müncheberg long-term experiment (started 1937). "
                  "Kühn et al. 2012: rapid SOC loss post-reunification under intensive management.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.35,
            ec_range=(0.15, 0.60),
            ph_range=(6.5, 7.5),
            sar_range=(0.3, 1.5),
            primary_source="Groundwater (irrigation critical for potato, vegetables)",
            quality_class="C1-C2, S1 (generally good, some Fe/Mn issues)",
            common_contaminants=["iron", "manganese", "nitrate (moderate)"],
            fluoride_risk=0.05,
            arsenic_risk=0.03,
            nitrate_risk=0.40,
            notes="Irrigation essential for potato in dry years (2018: -200 mm deficit). "
                  "Sandy soils: high irrigation demand. "
                  "Some groundwater Fe/Mn clogging of drippers.",
        ),

        agronomic_notes=(
            "Brandenburg: most drought-stressed agricultural region in Germany. "
            "Structural change: large cooperative farms post-reunification. "
            "KEY BODIUM RELEVANCE: ZALF Müncheberg — home institution of BODIUM project team "
            "(König et al. 2023 EJSS). Long-term experiment data (1937–present) used for "
            "BODIUM calibration. Sandy soil SOC dynamics, microbial biomass turnover, "
            "soil structure recovery after tillage regime changes — core BODIUM research questions."
        ),
    ),
}


# ─────────────────────────────────────────────────────────────────────────────
#  FRANCE — 3 major agricultural regions
# ─────────────────────────────────────────────────────────────────────────────

EU_LOCATION_INTELLIGENCE.update({

    "france_paris_basin": StateIntelligence(
        state="France — Paris Basin (Île-de-France / Centre / Champagne)",
        region="Northern France",
        primary_crops=["wheat", "rapeseed", "sugarbeet", "maize", "barley"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam"],
                "ACCase + ALS",
                "Expanding north of Loire; metabolic resistance confirmed in Seine-et-Marne "
                "and Eure-et-Loir; Heap 2024",
                severity=0.45,
            ),
            WeedResistanceCase(
                "Avena fatua (wild oats)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "ACCase resistance in intensive cereal areas; Heap 2024",
                severity=0.30,
            ),
            WeedResistanceCase(
                "Papaver rhoeas (common poppy)",
                "wheat",
                ["mecoprop-P", "florasulam", "tribenuron-methyl"],
                "ALS + Synthetic auxin",
                "Widespread ALS resistance in Paris Basin cereals; INRAE survey 2022",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch", "wheat", 0.75, "both",
                "Z. tritici — dominant wheat disease; oceanic influence; "
                "yield loss 20–45 % untreated; fungicide spend routinely 3 applications"),
            DiseasePressure("fusarium_head_blight",  "wheat",    0.45, "both",
                "F. graminearum — DON risk increasing; wet May-June; Terres Inovia data"),
            DiseasePressure("wheat_yellow_rust",     "wheat",    0.45, "rabi",
                "P. striiformis — new aggressive races; Paris Basin warm springs"),
            DiseasePressure("pyrenophora_tritici",   "wheat",    0.35, "both",
                "P. tritici-repentis (tan spot) — expanding under no-till practices"),
            DiseasePressure("fusarium_crown_rot",    "wheat",    0.30, "both",
                "F. culmorum / pseudograminearum — crown rot in continuous cereals"),
            DiseasePressure("phoma_stem_canker",     "rapeseed", 0.65, "both",
                "L. maculans — primary rapeseed disease; routine T1/T2 fungicide; "
                "Murray et al. 2012"),
            DiseasePressure("sclerotinia_rapeseed",  "rapeseed", 0.55, "both",
                "S. sclerotiorum — wet flowering; INRAE monitoring"),
            DiseasePressure("cercospora_leaf_spot",  "sugarbeet",0.55, "kharif",
                "C. beticola — humid July-August; IT crop monitoring"),
            DiseasePressure("beet_yellows_virus",    "sugarbeet",0.50, "kharif",
                "BMYV/BYV — neonicotinoid seed treatment banned France 2018; "
                "aphid-vectored; major economic losses 2020/2021"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.70, "both",
                "M. aeneus — pyrethroid resistance near-universal; INRAE monitoring"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.65, "both",
                "P. chrysocephala — post-neonicotinoid ban pressure increase"),
            InsectPressure("cereal_aphids",            "wheat",    0.55, "both",
                "S. avenae + R. padi — BYDV vector; warm autumns increase risk"),
            InsectPressure("beet_aphid",               "sugarbeet",0.60, "kharif",
                "M. persicae — BYD virus primary vector; neonicotinoid ban 2018 → "
                "severe outbreaks 2020–2021 in Île-de-France beet zone"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.8, 7.5),
            ec_ds_m_range=(0.18, 0.35),
            organic_matter_pct=2.20,
            nitrogen_status="high",
            phosphorus_status="medium-high",
            potassium_status="medium-high",
            zinc_deficient_pct=0.10,
            boron_deficient_pct=0.12,
            sulphur_deficient_pct=0.22,
            iron_deficient_pct=0.05,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Luvisol / Cambisol (sols lessivés) — deep loess over chalk",
            notes="Paris Basin: most productive arable region in France (~450 mm/yr). "
                  "Loess-derived Luvisols; chalk subsoil. "
                  "N surplus from intensive cropping; moderate P build-up. "
                  "S deficiency emerging post clean-air legislation. "
                  "Key research: INRAE Versailles-Grignon, Terres Inovia.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.25,
            ec_range=(0.15, 0.45),
            ph_range=(7.0, 7.8),
            sar_range=(0.3, 1.5),
            primary_source="Primarily rain-fed (550–700 mm/yr); Seine groundwater some areas",
            quality_class="C1-S1 (excellent quality)",
            common_contaminants=["nitrate", "pesticide residues (Seine basin)"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.45,
            notes="Intensive arable → nitrate leaching; Seine tributaries show pesticide loading. "
                  "Generally sufficient rainfall; supplemental irrigation uncommon for cereals.",
        ),

        agronomic_notes=(
            "Paris Basin: ~5 M ha arable, Europe's most productive cereal zone. "
            "Wheat yields 7–9 t/ha attainable. Beet yellows virus post-neonicotinoid ban "
            "is acute challenge. Key INRAE sites: Versailles-Grignon, Laon, Reims. "
            "Relevant for EU Food Security resilience modelling."
        ),
    ),

    "france_brittany": StateIntelligence(
        state="France — Brittany / Normandy (Bretagne / Normandie)",
        region="NW France",
        primary_crops=["wheat", "barley", "rapeseed", "potato", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam", "flupyrsulfuron"],
                "ACCase + ALS + metabolic resistance",
                "Highest HR burden in France; Atlantic climate enables year-round germination; "
                "metabolic resistance confirmed Calvados/Eure (INRAE 2022); Heap 2024",
                severity=0.60,
            ),
            WeedResistanceCase(
                "Galium aparine (cleavers)",
                "wheat",
                ["mecoprop-P", "fluroxypyr"],
                "Synthetic auxin",
                "Very common broad-leaf; partial resistance documented in Normandy",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch", "wheat",    0.80, "both",
                "Z. tritici — highest risk in France; Atlantic climate 700–900 mm/yr; "
                ">30 h leaf wetness/week common; yield loss 30–50 % untreated"),
            DiseasePressure("phoma_stem_canker",       "rapeseed", 0.70, "both",
                "L. maculans — consistent high risk; mild wet winters"),
            DiseasePressure("sclerotinia_rapeseed",    "rapeseed", 0.65, "both",
                "S. sclerotiorum — high risk; wet flowering period"),
            DiseasePressure("potato_late_blight",      "potato",   0.80, "kharif",
                "Ph. infestans — primary potato disease; wet Brittany summers; "
                "yield loss 40–80 % untreated"),
            DiseasePressure("ramularia_leaf_spot",     "barley",   0.40, "both",
                "R. collo-cygni — cool-humid Atlantic climate; increasing on spring barley"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.70, "both",
                "M. aeneus — very high; pyrethroid resistance universal in Normandy"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.70, "both",
                "P. chrysocephala — most severe pressure in France; neonicotinoid ban impact"),
            InsectPressure("colorado_potato_beetle",   "potato",   0.55, "kharif",
                "L. decemlineata — routine control; insecticide resistance developing"),
            InsectPressure("cereal_aphids",            "wheat",    0.55, "both",
                "S. avenae — BYDV vector; mild Atlantic winters increase overwintering"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.8, 6.8),
            ec_ds_m_range=(0.15, 0.40),
            organic_matter_pct=3.00,
            nitrogen_status="medium-high",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.12,
            boron_deficient_pct=0.20,
            sulphur_deficient_pct=0.28,
            iron_deficient_pct=0.06,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Brunisol / Cambisol — weathered schist + loess pockets",
            notes="Atlantic climate: 700–900 mm/yr. Higher OM than Paris Basin. "
                  "Acid sandy soils in Landes region. Intensive livestock → N/P surpluses. "
                  "Brittany: major pig/poultry density → groundwater nitrate pressure.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.22,
            ec_range=(0.12, 0.40),
            ph_range=(6.5, 7.5),
            sar_range=(0.2, 1.2),
            primary_source="Rain-fed (700–900 mm/yr); some river/groundwater for potato",
            quality_class="C1-S1 (excellent)",
            common_contaminants=["nitrate (intense livestock zone)"],
            fluoride_risk=0.02,
            arsenic_risk=0.02,
            nitrate_risk=0.55,
            notes="Brittany has highest agricultural N loading in France; "
                  "coastal groundwater frequently exceeds 50 mg/L NO3.",
        ),

        agronomic_notes=(
            "Brittany/Normandy: Atlantic cereal + livestock region. "
            "Black-grass HR is the number-one agronomic challenge. "
            "Key research: INRAE Rennes, Terres Inovia Ouest; "
            "Chambre d'Agriculture Normandie herbicide resistance monitoring."
        ),
    ),

    "france_southwest": StateIntelligence(
        state="France — South-West (Aquitaine / Midi-Pyrénées)",
        region="SW France",
        primary_crops=["maize", "sunflower", "grapes", "wheat", "soybean"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron", "mesotrione"],
                "ALS + HPPD",
                "ALS + HPPD resistance in intensively maize-grown Landes/Gers; Heap 2024",
                severity=0.40,
            ),
            WeedResistanceCase(
                "Setaria viridis (green foxtail)",
                "maize",
                ["nicosulfuron"],
                "ALS",
                "ALS resistance emerging; INRAE Toulouse survey 2021",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("grape_downy_mildew",  "grapes",    0.75, "both",
                "P. viticola — primary vine disease; wet springs in Bordeaux region; "
                "yield loss 20–100 % in epidemic years unprotected"),
            DiseasePressure("grape_powdery_mildew","grapes",    0.65, "both",
                "E. necator — warm + moderate humidity; routine 8–12 sprays in Bordeaux"),
            DiseasePressure("sclerotinia",         "sunflower", 0.55, "both",
                "S. sclerotiorum (head rot + stem rot) — major sunflower disease SW France"),
            DiseasePressure("maize_turcicum",      "maize",     0.40, "kharif",
                "E. turcicum — Northern Leaf Blight; humid Pyrenean foothills"),
            DiseasePressure("septoria_tritici_blotch","wheat",  0.60, "both",
                "Z. tritici — moderate risk in drier SE; higher in Atlantic NW of region"),
        ],

        insect_pressure=[
            InsectPressure("corn_rootworm",    "maize",    0.40, "kharif",
                "Diabrotica virgifera — invasive in SW France since 2015; "
                "crop rotation disruption in maize monocultures"),
            InsectPressure("cereal_aphids",    "wheat",    0.45, "both",
                "S. avenae — moderate pressure; warmer climate"),
            InsectPressure("pollen_beetle",    "rapeseed", 0.60, "both",
                "M. aeneus — pyrethroid resistance high"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.0, 7.5),
            ec_ds_m_range=(0.15, 0.50),
            organic_matter_pct=2.40,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.14,
            boron_deficient_pct=0.16,
            sulphur_deficient_pct=0.20,
            iron_deficient_pct=0.08,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Luvisol / Arenosol (Landes pine sand) — diverse; "
                               "alluvial Fluvisol in Garonne valley",
            notes="Diverse landscape: Atlantic Landes pine (Arenosol) → Garonne alluvium → "
                  "Gers calcareous hillslopes. Maize monoculture in Landes → soil compaction. "
                  "Bordeaux vineyards: Luvisol/Cambisol on gravels.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.30,
            ec_range=(0.15, 0.65),
            ph_range=(6.5, 7.8),
            sar_range=(0.3, 1.8),
            primary_source="Garonne/Adour river irrigation for maize; rain-fed wheat/grapes",
            quality_class="C1-C2, S1 (good quality)",
            common_contaminants=["nitrate (maize zone)", "pesticide residues (wine zone)"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.38,
            notes="Garonne irrigation enables maize yields 10–12 t/ha. "
                  "Wine zone: copper-based fungicides → soil copper accumulation concern.",
        ),

        agronomic_notes=(
            "SW France: Europe's most important wine (Bordeaux/Gascony) + maize/sunflower region. "
            "Corn rootworm (Diabrotica) invasive since ~2010 — major rotation challenge. "
            "Key research: INRAE Bordeaux, INRAE Toulouse; IFV (Institut Français de la Vigne)."
        ),
    ),

    # ─────────────────────────────────────────────────────────────────────────
    #  POLAND — 3 major agricultural regions
    # ─────────────────────────────────────────────────────────────────────────

    "poland_greater_poland": StateIntelligence(
        state="Poland — Greater Poland (Wielkopolska)",
        region="West-Central Poland",
        primary_crops=["rapeseed", "wheat", "sugarbeet", "potato", "barley", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "pyroxasulam", "florasulam",
                 "clodinafop-P"],
                "ALS + ACCase",
                "Most prevalent HR grass weed in Poland; >50 % fields affected Wielkopolska; "
                "Adamczewski & Kierzek (2019) Prog Plant Prot",
                severity=0.55,
            ),
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "fenoxaprop-P"],
                "ALS + ACCase",
                "Expanding from W Germany border; Heap 2024; moderate severity",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat",    0.65, "both",
                "Z. tritici — major wheat disease; continental-Atlantic transition climate"),
            DiseasePressure("fusarium_head_blight",   "wheat",    0.50, "both",
                "F. graminearum — DON contamination risk; wet May-June common"),
            DiseasePressure("phoma_stem_canker",       "rapeseed", 0.60, "both",
                "L. maculans — major rapeseed disease in Poland; IUNG Puławy monitoring"),
            DiseasePressure("sclerotinia_rapeseed",    "rapeseed", 0.55, "both",
                "S. sclerotiorum — economic threshold exceeded >50 % years"),
            DiseasePressure("potato_late_blight",      "potato",   0.70, "kharif",
                "Ph. infestans — primary potato disease; wet summers frequent; "
                "Poland: 3rd largest potato producer in EU"),
            DiseasePressure("cercospora_leaf_spot",    "sugarbeet",0.55, "kharif",
                "C. beticola — common in warm humid July-August"),
            DiseasePressure("clubroot",                "rapeseed", 0.40, "both",
                "P. brassicae — expanding with rapeseed area increase; "
                "soil pH < 6.5 in some sandy areas increases risk"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.65, "both",
                "M. aeneus — pyrethroid resistance widespread Poland; IOR-PIB monitoring"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.60, "both",
                "P. chrysocephala — increasing post-neonicotinoid restrictions"),
            InsectPressure("colorado_potato_beetle",   "potato",   0.70, "kharif",
                "L. decemlineata — most important potato pest Poland; "
                "resistance to imidacloprid developing"),
            InsectPressure("cereal_aphids",            "wheat",    0.50, "both",
                "S. avenae — BYDV vector pressure moderate"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.0, 7.2),
            ec_ds_m_range=(0.15, 0.38),
            organic_matter_pct=2.00,
            nitrogen_status="medium-high",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.18,
            boron_deficient_pct=0.22,
            sulphur_deficient_pct=0.28,
            iron_deficient_pct=0.06,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Luvisol / Cambisol (brown earths on loess and glacial till)",
            notes="Wielkopolska: most productive arable region Poland. "
                  "Continental climate (550 mm/yr). Loess-belt soils highest quality. "
                  "S deficiency widespread; Zn deficiency on calcareous soils. "
                  "Key research: IUNG Puławy, IOR-PIB Poznań.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.28,
            ec_range=(0.15, 0.50),
            ph_range=(6.8, 7.8),
            sar_range=(0.3, 1.5),
            primary_source="Mostly rain-fed; some groundwater irrigation for potato/vegetable",
            quality_class="C1-C2, S1 (good quality)",
            common_contaminants=["nitrate"],
            fluoride_risk=0.04,
            arsenic_risk=0.02,
            nitrate_risk=0.42,
            notes="Groundwater quality generally good; some NO3 in intensive livestock areas.",
        ),

        agronomic_notes=(
            "Wielkopolska: Poland's agri-industrial heartland. "
            "Largest rapeseed and sugarbeet acreage in Poland. "
            "Apera spica-venti HR is primary weed management challenge. "
            "Key institutions: IUNG Puławy (soil-plant nutrition), IOR-PIB Poznań (pest monitoring)."
        ),
    ),

    "poland_masovia": StateIntelligence(
        state="Poland — Masovia (Mazowsze) around Warsaw",
        region="Central Poland",
        primary_crops=["wheat", "rye", "rapeseed", "potato", "maize"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "florasulam", "pyroxasulam"],
                "ALS",
                "Widespread in cereal-dominated Masovia; Heap 2024",
                severity=0.50,
            ),
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron"],
                "ALS",
                "ALS resistance in maize rotations near Warsaw; Heap 2024",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat",    0.60, "both",
                "Z. tritici — moderate risk; continental climate drier than W Poland"),
            DiseasePressure("fusarium_head_blight",   "wheat",    0.45, "both",
                "F. graminearum — risk in wet May/June years"),
            DiseasePressure("potato_late_blight",      "potato",   0.65, "kharif",
                "Ph. infestans — major risk; Masovia significant potato area"),
            DiseasePressure("aphanomyces_root_rot",    "wheat",    0.30, "both",
                "Aphanomyces euteiches — pea/legume root rot; rotation problem "
                "with legume break crops; IUNG Puławy"),
            DiseasePressure("phoma_stem_canker",       "rapeseed", 0.55, "both",
                "L. maculans — moderate risk; annual spraying standard"),
        ],

        insect_pressure=[
            InsectPressure("colorado_potato_beetle",   "potato",   0.65, "kharif",
                "L. decemlineata — major threat; insecticide resistance common"),
            InsectPressure("cereal_aphids",            "wheat",    0.50, "both",
                "S. avenae — BYDV vector; warm autumns increase risk"),
            InsectPressure("pollen_beetle",            "rapeseed", 0.60, "both",
                "M. aeneus — standard rapeseed threat"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 6.8),
            ec_ds_m_range=(0.12, 0.35),
            organic_matter_pct=1.80,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="low-medium",
            zinc_deficient_pct=0.20,
            boron_deficient_pct=0.25,
            sulphur_deficient_pct=0.30,
            iron_deficient_pct=0.06,
            dominant_texture="sandy loam to loam",
            dominant_soil_type="Cambisol / Arenosol — glacial outwash plains, lighter soils",
            notes="Masovia: lighter sandy soils than Wielkopolska; lower OM. "
                  "Acid pH → Zn/B deficiency common. Vistula alluvials more productive.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.22,
            ec_range=(0.12, 0.42),
            ph_range=(6.5, 7.5),
            sar_range=(0.2, 1.2),
            primary_source="Rain-fed (500–550 mm/yr); Vistula groundwater some areas",
            quality_class="C1-S1 (good quality)",
            common_contaminants=["nitrate (moderate)"],
            fluoride_risk=0.04,
            arsenic_risk=0.02,
            nitrate_risk=0.35,
            notes="Lower precipitation than W Poland; drought stress increasing. "
                  "Supplemental irrigation for potato recommended in dry years.",
        ),

        agronomic_notes=(
            "Masovia: major rye and potato region. Warsaw peri-urban horticulture expanding. "
            "Sandy soils limit potential; acidification ongoing challenge. "
            "Key institutions: Warsaw University of Life Sciences (SGGW), IUNG Puławy."
        ),
    ),

    "poland_pomerania": StateIntelligence(
        state="Poland — West Pomerania (Zachodniopomorskie)",
        region="NW Poland",
        primary_crops=["rapeseed", "wheat", "barley", "maize", "rye"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Apera spica-venti (loose silky-bent grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron", "florasulam", "pyroxasulam",
                 "clodinafop-P"],
                "ALS + ACCase",
                "Most severe Apera pressure in Poland; Baltic maritime influence "
                "favours early germination; Heap 2024",
                severity=0.60,
            ),
            WeedResistanceCase(
                "Viola arvensis (field pansy)",
                "wheat",
                ["tribenuron-methyl", "florasulam"],
                "ALS",
                "ALS resistance widespread in Pomeranian cereal belt; Heap 2024",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("phoma_stem_canker",    "rapeseed", 0.65, "both",
                "L. maculans — highest rapeseed disease risk in Poland; "
                "mild Baltic winters; Murray et al. 2012"),
            DiseasePressure("sclerotinia_rapeseed", "rapeseed", 0.60, "both",
                "S. sclerotiorum — wet spring flowering; economic threshold routinely exceeded"),
            DiseasePressure("clubroot",             "rapeseed", 0.50, "both",
                "P. brassicae — significant risk; acid sandy soils and wet conditions; "
                "increasing with rapeseed intensification; resistant varieties key"),
            DiseasePressure("septoria_tritici_blotch","wheat",  0.65, "both",
                "Z. tritici — Atlantic-influenced NW Poland; higher than central Poland"),
            DiseasePressure("barley_net_blotch",    "barley",  0.50, "both",
                "P. teres — common in spring/winter barley; wet Baltic springs"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.65, "both",
                "M. aeneus — pyrethroid resistance; standard Baltic coast problem"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.65, "both",
                "P. chrysocephala — post-neonicotinoid ban; major issue"),
            InsectPressure("slug",                     "rapeseed", 0.45, "both",
                "Deroceras reticulatum — wet Baltic autumns; establishment damage"),
            InsectPressure("cereal_aphids",            "wheat",    0.45, "both",
                "Moderate BYDV vector pressure; Baltic maritime region"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.8, 6.8),
            ec_ds_m_range=(0.12, 0.35),
            organic_matter_pct=2.20,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.16,
            boron_deficient_pct=0.22,
            sulphur_deficient_pct=0.30,
            iron_deficient_pct=0.07,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Luvisol / Cambisol — glacial till; post-glacial moraines",
            notes="Baltic maritime climate: 550–650 mm/yr. Large farm structure "
                  "(>500 ha post-reunification). Clubroot-susceptible acid patches common.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.25,
            ec_range=(0.12, 0.45),
            ph_range=(6.5, 7.5),
            sar_range=(0.2, 1.2),
            primary_source="Rain-fed; Baltic maritime precipitation adequate",
            quality_class="C1-S1 (good quality)",
            common_contaminants=["nitrate (moderate)"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.38,
            notes="Generally adequate rainfall; supplemental irrigation uncommon except vegetables.",
        ),

        agronomic_notes=(
            "W. Pomerania: large-scale arable farms; major rapeseed region. "
            "Clubroot (P. brassicae) now key constraint on rapeseed expansion. "
            "Key research: ZUT Szczecin, IUNG Puławy field stations."
        ),
    ),

    # ─────────────────────────────────────────────────────────────────────────
    #  UK — 3 major agricultural regions
    # ─────────────────────────────────────────────────────────────────────────

    "uk_east_anglia": StateIntelligence(
        state="UK — East Anglia (Norfolk / Suffolk / Cambridgeshire)",
        region="Eastern England",
        primary_crops=["wheat", "barley", "rapeseed", "potato", "sugarbeet"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam", "flupyrsulfuron"],
                "ACCase + ALS + metabolic (triple resistance)",
                "England's most severe HR region; metabolic resistance dominant mechanism; "
                "ADAS/Rothamsted: >70 % of Norfolk/Suffolk fields with resistant biotypes "
                "(Hull et al. 2014 Weed Res); Heap 2024",
                severity=0.65,
            ),
            WeedResistanceCase(
                "Avena sterilis / fatua (wild oats)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "ACCase resistance established in E. Anglia; Heap 2024",
                severity=0.40,
            ),
            WeedResistanceCase(
                "Stellaria media (common chickweed)",
                "wheat",
                ["mecoprop-P", "fluroxypyr", "tribenuron-methyl"],
                "Synthetic auxin + ALS",
                "ALS resistance documented; secondary weed; Heap 2024",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat",    0.80, "both",
                "Z. tritici — primary wheat disease; maritime climate; "
                "yield loss 25–50 % untreated; fungicide spend 3–4 applications standard"),
            DiseasePressure("wheat_yellow_rust",      "wheat",    0.50, "rabi",
                "P. striiformis — new aggressive races Warrior/Kranich 2011–; "
                "epidemic years 2014, 2018; E. Anglia warm springs"),
            DiseasePressure("phoma_stem_canker",      "rapeseed", 0.65, "both",
                "L. maculans — major disease; Atlantic climate; ADAS Terrington data"),
            DiseasePressure("ramularia_leaf_spot",    "barley",   0.45, "both",
                "R. collo-cygni — increasingly important on winter/spring barley; "
                "SRUC/ADAS monitoring; latent in seed"),
            DiseasePressure("potato_late_blight",     "potato",   0.75, "kharif",
                "Ph. infestans — primary potato disease; UK: major potato acreage; "
                "Norfolk/Lincs key potato zones; 6–15 fungicide applications/season"),
            DiseasePressure("beet_yellows_virus",     "sugarbeet",0.50, "kharif",
                "BMYV/BYV — neonicotinoid seed treatment ban UK 2018; "
                "aphid-vectored; major yield losses in warm/dry aphid years"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.65, "both",
                "M. aeneus — pyrethroid resistance near-universal in England; ADAS data"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.70, "both",
                "P. chrysocephala — worst in England post-neonicotinoid ban; "
                "crop failures reported in poor autumns 2019–2022"),
            InsectPressure("cereal_aphids",            "wheat",    0.55, "both",
                "S. avenae — BYDV vector; mild Atlantic winters increase risk"),
            InsectPressure("beet_aphid",               "sugarbeet",0.55, "kharif",
                "M. persicae — BYD vector; major since neonicotinoid ban"),
            InsectPressure("colorado_potato_beetle",   "potato",   0.30, "kharif",
                "L. decemlineata — present but less severe than continent; "
                "watch for spread"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.5, 7.8),
            ec_ds_m_range=(0.15, 0.45),
            organic_matter_pct=3.00,
            nitrogen_status="medium-high",
            phosphorus_status="medium-high",
            potassium_status="medium",
            zinc_deficient_pct=0.08,
            boron_deficient_pct=0.14,
            sulphur_deficient_pct=0.22,
            iron_deficient_pct=0.05,
            dominant_texture="loam to clay",
            dominant_soil_type="Luvisol on chalk / Cambisol (Broads peat marginal); "
                               "alluvial soils in Fens",
            notes="East Anglian chalks: pH buffered high; high K from clay subsoil. "
                  "Fenland peat soils: very high OM but subsiding. "
                  "AHDB/Rothamsted Broadbalk: key long-term soil dataset. "
                  "S deficiency emerged post-1990 clean-air; now routine application.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.30,
            ec_range=(0.20, 0.60),
            ph_range=(6.8, 7.8),
            sar_range=(0.3, 1.5),
            primary_source="Rain-fed cereals; groundwater/river abstraction for potato/veg",
            quality_class="C2-S1 (good quality)",
            common_contaminants=["nitrate"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.50,
            notes="East Anglia: 600 mm/yr; potato irrigation essential summer "
                  "(Jul-Aug deficits). Groundwater levels declining in Chalk aquifer.",
        ),

        agronomic_notes=(
            "East Anglia: UK's most productive arable region (wheat 8–10 t/ha attainable). "
            "Black-grass metabolic HR is most acute management challenge. "
            "Key research: Rothamsted Research, NIAB Cambridge, ADAS Boxworth. "
            "Broadbalk Experiment (1843–present) — world's longest-running agronomy trial."
        ),
    ),

    "uk_east_midlands": StateIntelligence(
        state="UK — East Midlands (Lincolnshire / Nottinghamshire / Leicestershire)",
        region="Central England",
        primary_crops=["wheat", "barley", "rapeseed", "potato", "vegetables"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam"],
                "ACCase + ALS + metabolic",
                "Severe; Lincs/Notts heavy clay soils favour autumn germination; "
                "Heap 2024; ADAS East Midlands HR network",
                severity=0.55,
            ),
            WeedResistanceCase(
                "Galium aparine (cleavers)",
                "wheat",
                ["mecoprop-P", "fluroxypyr"],
                "Synthetic auxin",
                "Widespread; difficult to control with auxin herbicides",
                severity=0.35,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat",    0.75, "both",
                "Z. tritici — primary threat; continental-Atlantic transition"),
            DiseasePressure("phoma_stem_canker",      "rapeseed", 0.65, "both",
                "L. maculans — consistent risk; key Lincs rapeseed belt"),
            DiseasePressure("fusarium_head_blight",   "wheat",    0.45, "both",
                "F. graminearum — wet May-June; DON risk in Trent valley"),
            DiseasePressure("potato_late_blight",     "potato",   0.70, "kharif",
                "Ph. infestans — Lincs major potato county; wet summers critical"),
            DiseasePressure("wheat_eyespot",          "wheat",    0.40, "both",
                "Oculimacula yallundae/acuformis — cool-wet springs; lodging risk"),
        ],

        insect_pressure=[
            InsectPressure("pollen_beetle",            "rapeseed", 0.60, "both",
                "M. aeneus — pyrethroid resistance; standard Midlands issue"),
            InsectPressure("cabbage_stem_flea_beetle", "rapeseed", 0.65, "both",
                "P. chrysocephala — severe on autumn-sown rapeseed"),
            InsectPressure("cereal_aphids",            "wheat",    0.50, "both",
                "S. avenae — BYDV vector risk moderate"),
            InsectPressure("colorado_potato_beetle",   "potato",   0.35, "kharif",
                "L. decemlineata — present Lincs; routine control needed"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.8, 7.8),
            ec_ds_m_range=(0.18, 0.55),
            organic_matter_pct=2.50,
            nitrogen_status="medium-high",
            phosphorus_status="medium",
            potassium_status="medium-high",
            zinc_deficient_pct=0.10,
            boron_deficient_pct=0.16,
            sulphur_deficient_pct=0.24,
            iron_deficient_pct=0.06,
            dominant_texture="clay to clay loam",
            dominant_soil_type="Luvisol / Cambisol on Jurassic limestone and boulder clay",
            notes="Heavy Midlands clays: high water retention — waterlogging risk. "
                  "Wolds chalk: free-draining, high pH. Fenland alluvials in Lincs. "
                  "Strong K from clay minerals; P historically built-up.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.35,
            ec_range=(0.20, 0.65),
            ph_range=(7.0, 7.8),
            sar_range=(0.3, 1.8),
            primary_source="Rain-fed; groundwater/borehole for potato irrigation Lincs",
            quality_class="C2-S1 (good quality)",
            common_contaminants=["nitrate"],
            fluoride_risk=0.03,
            arsenic_risk=0.02,
            nitrate_risk=0.45,
            notes="Lincs: intensive potato → groundwater N drawdown. "
                  "600–650 mm/yr; summer irrigation essential for potato.",
        ),

        agronomic_notes=(
            "East Midlands: major potato + vegetable production. "
            "Black-grass on heavy clays is critical management issue. "
            "Key institutions: AHDB Cereals & Oilseeds, NIAB, Cranfield University soil team."
        ),
    ),

    "uk_scotland": StateIntelligence(
        state="UK — Scotland (Angus / Fife / Perth & Kinross — main arable belt)",
        region="Eastern Scotland",
        primary_crops=["barley", "wheat", "rapeseed", "potato", "oats"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Avena fatua (wild oats)",
                "barley",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "ACCase resistance documented in Scottish cereal belt; Heap 2024",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Alopecurus myosuroides (black-grass)",
                "wheat",
                ["mesosulfuron+iodosulfuron"],
                "ALS",
                "Emerging from S England; lower density than English regions; Heap 2024",
                severity=0.20,
            ),
        ],

        disease_pressure=[
            DiseasePressure("ramularia_leaf_spot",    "barley",   0.65, "both",
                "R. collo-cygni — Scotland has highest barley ramularia burden in EU; "
                "cool-humid maritime climate optimal; yield loss 10–25 % "
                "(Walters et al. 2008 Eur J Plant Path); latent seed infection"),
            DiseasePressure("septoria_tritici_blotch","wheat",    0.70, "both",
                "Z. tritici — maritime Scotland; similar risk to England; JHI monitoring"),
            DiseasePressure("barley_net_blotch",      "barley",   0.55, "both",
                "P. teres — common on spring and winter barley Scotland"),
            DiseasePressure("sclerotinia_rapeseed",   "rapeseed", 0.50, "both",
                "S. sclerotiorum — wet cool flowering periods common"),
            DiseasePressure("potato_late_blight",     "potato",   0.70, "kharif",
                "Ph. infestans — Perthshire potato belt; cool-wet summer conditions ideal"),
        ],

        insect_pressure=[
            InsectPressure("cereal_aphids",            "barley",   0.45, "both",
                "S. avenae — BYDV vector; mild maritime autumns"),
            InsectPressure("pollen_beetle",            "rapeseed", 0.55, "both",
                "M. aeneus — pyrethroid resistance; standard problem"),
            InsectPressure("wireworm",                 "potato",   0.40, "both",
                "Agriotes spp. — grassland-converted fields; no seed treatment "
                "permitted → difficult control Scotland"),
            InsectPressure("slug",                     "rapeseed", 0.50, "both",
                "Deroceras reticulatum — wet maritime autumns; establishment damage"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.8, 6.5),
            ec_ds_m_range=(0.12, 0.35),
            organic_matter_pct=4.00,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.10,
            boron_deficient_pct=0.18,
            sulphur_deficient_pct=0.28,
            iron_deficient_pct=0.05,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Brown Earth / Inceptisol — on Devonian and Silurian parent material",
            notes="Cool maritime climate: 700–900 mm/yr in arable belt. High OM from cool conditions. "
                  "Naturally acidic soils → liming routine. SRUC Dundee key research station. "
                  "Barley malting quality premium: Scotland malt exports 200 k t/yr.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.18,
            ec_range=(0.10, 0.35),
            ph_range=(6.5, 7.5),
            sar_range=(0.2, 1.0),
            primary_source="Rain-fed (high rainfall); Tay/Dee rivers for potato irrigation",
            quality_class="C1-S1 (excellent quality)",
            common_contaminants=["nitrate (low-moderate)"],
            fluoride_risk=0.02,
            arsenic_risk=0.02,
            nitrate_risk=0.25,
            notes="Scottish rain-fed agriculture: supplemental irrigation rare. "
                  "Rivers Tay, Forth, Dee used for potato irrigation in dry years.",
        ),

        agronomic_notes=(
            "Scotland: premium malting barley region (key for Scotch Whisky). "
            "Ramularia leaf spot is defining disease management challenge. "
            "Key research: James Hutton Institute (JHI) Dundee/Aberdeen — "
            "world leader in potato and barley disease research."
        ),
    ),

    # ─────────────────────────────────────────────────────────────────────────
    #  NETHERLANDS — 2 major agricultural regions
    # ─────────────────────────────────────────────────────────────────────────

    "netherlands_clay_polders": StateIntelligence(
        state="Netherlands — Clay Polders (Holland / Zeeland / Flevoland)",
        region="Western Netherlands",
        primary_crops=["potato", "onion", "sugarbeet", "wheat", "flower_bulbs"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Chenopodium album (fat-hen)",
                "sugarbeet",
                ["phenmedipham", "desmedipham"],
                "PSII",
                "PSII resistance in beet areas; Heap 2024",
                severity=0.30,
            ),
            WeedResistanceCase(
                "Matricaria inodora (scentless mayweed)",
                "wheat",
                ["tribenuron-methyl", "metsulfuron-methyl"],
                "ALS",
                "ALS resistance documented Netherlands; Heap 2024",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("potato_late_blight",      "potato",   0.90, "kharif",
                "Ph. infestans — most intensively monitored in EU; Netherlands has "
                "~150,000 ha potato; humid polder climate; 12–20 fungicide applications "
                "per season; yield loss 50–100 % unprotected (WUR, Naktuinbouw)"),
            DiseasePressure("nematode_potato",          "potato",   0.55, "kharif",
                "Globodera pallida/rostochiensis — potato cyst nematode; "
                "persistent soil reservoir; EU quarantine pest; "
                "population densities can cause 20–80 % yield loss"),
            DiseasePressure("fusarium_dry_rot_potato",  "potato",   0.45, "kharif",
                "Fusarium sulphureum/solani — dry rot; seed-borne; storage losses "
                "compounding field losses"),
            DiseasePressure("cercospora_leaf_spot",     "sugarbeet",0.50, "kharif",
                "C. beticola — risk in warm July-August polder climate"),
            DiseasePressure("beet_yellows_virus",       "sugarbeet",0.50, "kharif",
                "BMYV/BYV — neonicotinoid ban Netherlands; aphid-vectored"),
            DiseasePressure("septoria_tritici_blotch",  "wheat",    0.70, "both",
                "Z. tritici — maritime Netherlands; high risk; WUR Wageningen data"),
        ],

        insect_pressure=[
            InsectPressure("beet_aphid",               "sugarbeet",0.55, "kharif",
                "M. persicae — BYD virus; neonicotinoid ban impact severe Netherlands"),
            InsectPressure("colorado_potato_beetle",   "potato",   0.55, "kharif",
                "L. decemlineata — routine; insecticide resistance developing"),
            InsectPressure("cereal_aphids",            "wheat",    0.45, "both",
                "S. avenae — BYDV vector; maritime winters"),
            InsectPressure("thrips_tabaci",            "onion",    0.50, "kharif",
                "Thrips tabaci — primary onion pest Netherlands; "
                "insecticide resistance widespread; WUR Naktuinbouw"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.0, 7.8),
            ec_ds_m_range=(0.30, 1.20),
            organic_matter_pct=3.50,
            nitrogen_status="high",
            phosphorus_status="high",
            potassium_status="medium-high",
            zinc_deficient_pct=0.06,
            boron_deficient_pct=0.12,
            sulphur_deficient_pct=0.15,
            iron_deficient_pct=0.04,
            dominant_texture="clay",
            dominant_soil_type="Marine clay Poldervaaggrond / Drechtvaaggrond — "
                               "reclaimed from sea; high OM, pH-buffered by CaCO3",
            notes="Dutch polder clays: 25–60 % clay content; naturally high fertility. "
                  "EC elevated due to residual marine salts in some polders. "
                  "Phosphate-saturated (P-sat) soils: Dutch manure legislation critical. "
                  "Nematode densities build rapidly in susceptible potato rotations. "
                  "Key research: WUR Wageningen, Naktuinbouw, Dacom.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.80,
            ec_range=(0.40, 2.50),
            ph_range=(7.0, 7.8),
            sar_range=(1.0, 5.0),
            primary_source="Canal water (polders) + groundwater; salinity intrusion risk",
            quality_class="C2-C3, S1-S2 (moderate; salinity risk in coastal polders)",
            common_contaminants=["chloride (seawater intrusion)", "sodium"],
            fluoride_risk=0.02,
            arsenic_risk=0.02,
            nitrate_risk=0.40,
            notes="Polder canal water: EC can reach 1.5–3.0 dS/m near coast in dry summers. "
                  "Seawater intrusion a growing climate change risk. "
                  "Drip irrigation expands in vegetables to manage EC.",
        ),

        agronomic_notes=(
            "Netherlands clay polders: world's most intensive horticulture zone. "
            "Late blight and nematodes are the primary yield constraints in potato. "
            "BYD virus post-neonicotinoid ban is acute beet challenge. "
            "Key research: WUR Plant Sciences Group, Naktuinbouw, ILVO collaboration."
        ),
    ),

    "netherlands_sandy_east": StateIntelligence(
        state="Netherlands — Sandy East (Overijssel / Gelderland / Noord-Brabant)",
        region="Eastern Netherlands",
        primary_crops=["maize", "potato", "vegetables", "onion", "flower_bulbs"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron"],
                "ALS",
                "ALS resistance in sandy maize belt E. Netherlands; Heap 2024",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Galinsoga parviflora (gallant soldier)",
                "vegetables",
                ["tribenuron-methyl"],
                "ALS",
                "Emerging problem in horticultural crops; ALS resistance documented",
                severity=0.25,
            ),
        ],

        disease_pressure=[
            DiseasePressure("potato_late_blight",     "potato",   0.80, "kharif",
                "Ph. infestans — slightly lower than polder region but still primary risk"),
            DiseasePressure("nematode_potato",         "potato",   0.65, "kharif",
                "Globodera pallida/rostochiensis — worse on sandy soils; "
                "high population build-up in continuous potato; WUR data"),
            DiseasePressure("fusarium_dry_rot_potato", "potato",   0.40, "kharif",
                "F. sulphureum — seed-borne; storage and field losses"),
            DiseasePressure("maize_blsb",              "maize",    0.35, "kharif",
                "R. solani — Rhizoctonia root and stalk rot; wet sandy soil maize"),
        ],

        insect_pressure=[
            InsectPressure("colorado_potato_beetle",   "potato",   0.65, "kharif",
                "L. decemlineata — major threat; insecticide resistance common"),
            InsectPressure("thrips_tabaci",            "onion",    0.50, "kharif",
                "T. tabaci — insecticide resistance widespread; WUR Naktuinbouw"),
            InsectPressure("wireworm",                 "potato",   0.40, "both",
                "Agriotes spp. — significant post-grassland conversion; "
                "chemical treatment restrictions increasing"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(5.5, 6.5),
            ec_ds_m_range=(0.15, 0.50),
            organic_matter_pct=3.00,
            nitrogen_status="high",
            phosphorus_status="high",
            potassium_status="medium",
            zinc_deficient_pct=0.14,
            boron_deficient_pct=0.16,
            sulphur_deficient_pct=0.20,
            iron_deficient_pct=0.05,
            dominant_texture="sandy",
            dominant_soil_type="Arenosol / Podzol — Pleistocene coversand; "
                               "high P-saturation from decades of manure application",
            notes="Sandy E. Netherlands: high livestock density → P-saturated soils. "
                  "Manure Act targets reducing P surplus. High nematode risk on sandy soils. "
                  "Acid tendency: liming every 3–5 years standard.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.30,
            ec_range=(0.15, 0.60),
            ph_range=(6.0, 7.2),
            sar_range=(0.2, 1.2),
            primary_source="Groundwater (shallow; high water table); rain-fed cereals",
            quality_class="C1-C2, S1 (good quality)",
            common_contaminants=["nitrate", "phosphate (P-saturated subsoil leaching)"],
            fluoride_risk=0.02,
            arsenic_risk=0.02,
            nitrate_risk=0.55,
            notes="Sandy soils: high N leaching → groundwater NO3 often 50–100 mg/L. "
                  "P-saturated subsoils leach P to surface water → eutrophication.",
        ),

        agronomic_notes=(
            "E. Netherlands: most intensive livestock (pigs/chickens) in EU per km². "
            "Manure N/P regulation critical for crop management. "
            "Nematode management is primary potato production constraint. "
            "Key research: WUR Wageningen, Dacom plant monitoring, Naktuinbouw."
        ),
    ),

    # ─────────────────────────────────────────────────────────────────────────
    #  ITALY — 3 major agricultural regions
    # ─────────────────────────────────────────────────────────────────────────

    "italy_po_valley": StateIntelligence(
        state="Italy — Po Valley (Pianura Padana; Emilia-Romagna / Lombardy / Veneto)",
        region="North Italy",
        primary_crops=["wheat", "maize", "soybean", "sugarbeet", "rice"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron", "rimsulfuron",
                 "mesotrione"],
                "ALS + HPPD",
                "Most HR species in Italian maize; >30 % fields with multi-resistance; "
                "Heap 2024; Tranel & Wright (2002) WEED Sci",
                severity=0.55,
            ),
            WeedResistanceCase(
                "Lolium multiflorum (Italian ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "mesosulfuron+iodosulfuron"],
                "ACCase + ALS",
                "Expanding in Po Valley cereals; Heap 2024; CREA Bologna data",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Echinochloa oryzicola / crus-galli",
                "rice",
                ["bispyribac-sodium", "cyhalofop-butyl"],
                "ALS + ACCase",
                "Major problem in Vercelli/Pavia rice belt; Heap 2024",
                severity=0.50,
            ),
        ],

        disease_pressure=[
            DiseasePressure("fusarium_head_blight",   "wheat",    0.55, "both",
                "F. graminearum — DON contamination critical issue; Po Valley wet May; "
                "highest DON contamination rates in EU (EFSA 2017)"),
            DiseasePressure("septoria_tritici_blotch","wheat",    0.60, "both",
                "Z. tritici — moderate risk; N Italian climate"),
            DiseasePressure("maize_blsb",             "maize",    0.50, "kharif",
                "R. solani — warm humid Po Valley summer; yield loss up to 60 %"),
            DiseasePressure("maize_turcicum",         "maize",    0.40, "kharif",
                "E. turcicum — Northern Leaf Blight; Alpine foothills humidity"),
            DiseasePressure("beet_yellows_virus",     "sugarbeet",0.45, "kharif",
                "BMYV/BYV — aphid-vectored; Italy significant beet zone"),
            DiseasePressure("rice_blast",             "rice",     0.50, "kharif",
                "M. oryzae — Vercelli/Pavia rice belt; warm humid paddy conditions"),
        ],

        insect_pressure=[
            InsectPressure("corn_rootworm",  "maize",    0.55, "kharif",
                "D. virgifera — Diabrotica rootworm; invasive Italy from 1998; "
                "major constraint on maize monocultures in Po plain"),
            InsectPressure("beet_aphid",     "sugarbeet",0.50, "kharif",
                "M. persicae — BYD vector; neonicotinoid restrictions Italy"),
            InsectPressure("cereal_aphids",  "wheat",    0.45, "both",
                "S. avenae — BYDV vector; moderate pressure"),
            InsectPressure("rice_planthopper","rice",    0.35, "kharif",
                "Laodelphax striatellus — vector of rice stripe virus; Po paddy"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.0, 8.0),
            ec_ds_m_range=(0.20, 0.70),
            organic_matter_pct=2.00,
            nitrogen_status="medium-high",
            phosphorus_status="medium-high",
            potassium_status="medium",
            zinc_deficient_pct=0.14,
            boron_deficient_pct=0.18,
            sulphur_deficient_pct=0.18,
            iron_deficient_pct=0.10,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Cambic Fluvisol / Entisol — alluvial Po sediments; "
                               "calcareous, free-draining terraces + wet lowlands",
            notes="Po Valley: most productive arable in Italy. "
                  "Calcareous soils → Fe deficiency (lime-induced chlorosis) in sensitive crops. "
                  "Intensive maize/soybean; N surplus in livestock provinces (Emilia-R). "
                  "Key research: CREA Bologna, University of Bologna, Politecnico di Milano.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.45,
            ec_range=(0.25, 0.90),
            ph_range=(7.0, 7.8),
            sar_range=(0.5, 2.5),
            primary_source="Po River + Alpine glacier meltwater (canals); groundwater",
            quality_class="C2-S1 (good quality)",
            common_contaminants=["nitrate", "pesticide residues"],
            fluoride_risk=0.03,
            arsenic_risk=0.03,
            nitrate_risk=0.45,
            notes="Po water: good quality but seasonal variation. "
                  "Maize irrigation June-August essential (~300 mm). "
                  "Groundwater nitrate hotspots near intensive livestock Emilia-Romagna.",
        ),

        agronomic_notes=(
            "Po Valley: Italy's agri-industrial heartland (60 % of Italian arable production). "
            "Diabrotica rootworm invasive management is primary maize constraint. "
            "Fusarium DON contamination in wheat is a food-safety and trade issue. "
            "Key research: CREA Bologna, SANA organic sector; rice: Ente Nazionale Risi (Pavia)."
        ),
    ),

    "italy_apulia": StateIntelligence(
        state="Italy — Apulia (Puglia — SE heel of Italy)",
        region="South Italy",
        primary_crops=["wheat", "olive", "grapes", "sunflower", "vegetables"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Lolium rigidum (rigid ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron"],
                "ACCase + ALS",
                "Most important HR weed S. Italy; multi-resistance confirmed Apulia; "
                "Heap 2024; Ciani et al. (2019) Weed Res",
                severity=0.45,
            ),
            WeedResistanceCase(
                "Avena sterilis (winter wild oat)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "cycloxydim"],
                "ACCase",
                "Widespread ACCase resistance in dry Mediterranean wheat belt; Heap 2024",
                severity=0.40,
            ),
        ],

        disease_pressure=[
            DiseasePressure("xylella_fastidiosa",   "grapes",   0.80, "both",
                "X. fastidiosa subsp. pauca — catastrophic olive quick decline; "
                "21+ million olive trees dead or dying Apulia since 2013; "
                "EFSA 2019: existential threat to Puglia olive economy"),
            DiseasePressure("septoria_tritici_blotch","wheat",  0.45, "both",
                "Z. tritici — moderate risk; drier Mediterranean climate"),
            DiseasePressure("fusarium_head_blight",  "wheat",  0.40, "both",
                "F. graminearum — risk in wet spring years; DON concern durum"),
            DiseasePressure("tuta_absoluta",         "tomato",  0.60, "kharif",
                "Tuta absoluta — primary tomato pest S. Italy; year-round in "
                "greenhouse Apulia; CREA Bari data"),
            DiseasePressure("grape_downy_mildew",    "grapes",  0.55, "both",
                "P. viticola — moderate risk; Mediterranean dry climate reduces "
                "severity vs Atlantic France but wet springs can trigger epidemics"),
        ],

        insect_pressure=[
            InsectPressure("tuta_absoluta",     "tomato",  0.65, "kharif",
                "T. absoluta — invasive from S. America since 2006; "
                "open-field + greenhouse; insecticide resistance developing"),
            InsectPressure("bactrocera_oleae",  "grapes",  0.60, "kharif",
                "B. oleae — olive fruit fly; primary insect pest olive; "
                "damage + secondary infections; resistance to organophosphates"),
            InsectPressure("cereal_aphids",     "wheat",   0.40, "both",
                "S. avenae — BYDV vector; mild Mediterranean winters"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.5, 8.5),
            ec_ds_m_range=(0.25, 1.20),
            organic_matter_pct=1.20,
            nitrogen_status="low-medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.20,
            boron_deficient_pct=0.18,
            sulphur_deficient_pct=0.15,
            iron_deficient_pct=0.22,
            dominant_texture="clay to clay loam",
            dominant_soil_type="Vertisol / Alfisol — calcareous murge plateau; "
                               "deep Vertic clay ('terra rossa') on limestone",
            notes="Apulia: severely calcareous soils — pH 7.5–8.5; Fe/Mn chlorosis common. "
                  "Low OM from dry Mediterranean climate. "
                  "Drought primary constraint: 450–600 mm/yr concentrated Oct-Apr. "
                  "Xylella fastidiosa: most acute plant disease crisis in modern EU history. "
                  "Key research: CREA Bari, University of Bari, CNR-IPSP.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=1.20,
            ec_range=(0.60, 3.50),
            ph_range=(7.2, 8.2),
            sar_range=(2.0, 8.0),
            primary_source="Groundwater (overexploited); desalination emerging; some rain-fed olive",
            quality_class="C3-S2 (saline; use with caution for sensitive crops)",
            common_contaminants=["chloride", "sodium", "nitrate (intensive veg zones)"],
            fluoride_risk=0.05,
            arsenic_risk=0.04,
            nitrate_risk=0.50,
            notes="Apulian aquifer overexploited — seawater intrusion advancing inland. "
                  "EC of irrigation water 1–4 dS/m common near coast. "
                  "Olive: mostly rainfed (drought tolerant); vegetable irrigation essential.",
        ),

        agronomic_notes=(
            "Apulia: global olive oil capital (35 % of Italian olive production). "
            "Xylella fastidiosa devastation has destroyed 21 M+ trees; "
            "no cure — containment + resistant variety introduction only strategy. "
            "Key research: CREA Bari, University of Foggia, CNR Bari. "
            "Tuta absoluta requires integrated resistance management."
        ),
    ),

    "italy_tuscany": StateIntelligence(
        state="Italy — Tuscany / Umbria / Marche (Central Italy hill region)",
        region="Central Italy",
        primary_crops=["grapes", "olive", "wheat", "sunflower", "barley"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Lolium multiflorum (Italian ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "mesosulfuron+iodosulfuron"],
                "ACCase + ALS",
                "HR ryegrass in central Italian cereal belt; Heap 2024",
                severity=0.35,
            ),
            WeedResistanceCase(
                "Avena sterilis (winter wild oat)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "Widespread in Tuscan cereal belt; Heap 2024",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("grape_downy_mildew",  "grapes",  0.70, "both",
                "P. viticola — primary vine disease; spring rain and summer humidity; "
                "8–12 fungicide treatments per season standard in Chianti/Brunello zones"),
            DiseasePressure("grape_powdery_mildew","grapes",  0.65, "both",
                "E. necator — hot/dry summers favour; routine sprays essential"),
            DiseasePressure("wheat_yellow_rust",   "wheat",   0.40, "rabi",
                "P. striiformis — sporadic epidemics in Marche/Umbria wheat belt"),
            DiseasePressure("fusarium_head_blight","wheat",   0.40, "both",
                "F. graminearum — risk in wet spring; DON concern for durum"),
            DiseasePressure("xylella_fastidiosa",  "olive",   0.40, "both",
                "X. fastidiosa — risk zone moving north; monitoring ongoing Tuscany/Umbria"),
        ],

        insect_pressure=[
            InsectPressure("bactrocera_oleae", "olive",  0.65, "kharif",
                "B. oleae — olive fruit fly; primary pest across Tuscany olive belt; "
                "organophosphate resistance developing"),
            InsectPressure("cereal_aphids",    "wheat",  0.40, "both",
                "S. avenae — BYDV vector; moderate continental climate"),
            InsectPressure("grape_leafhopper", "grapes", 0.40, "kharif",
                "Empoasca vitis — leafhopper; heat-loving; secondary vine pest Tuscany"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.5, 8.0),
            ec_ds_m_range=(0.20, 0.80),
            organic_matter_pct=2.00,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.14,
            boron_deficient_pct=0.16,
            sulphur_deficient_pct=0.18,
            iron_deficient_pct=0.14,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Luvisol / Vertisol — galestro + alberese limestone-clay hillslopes; "
                               "alluvial Arno valley soils",
            notes="Diverse Tuscan geology: galestro (sandy schist) + alberese (calcareous clay) "
                  "underlie iconic wine regions (Chianti, Brunello). "
                  "Olive belt: stony clay loams; Fe chlorosis on calcareous. "
                  "Key research: CREA Firenze, SANU Pisa, CNR-IPSP.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.55,
            ec_range=(0.30, 1.20),
            ph_range=(7.0, 8.0),
            sar_range=(0.5, 3.0),
            primary_source="Arno/Tiber river systems; groundwater for vineyard drip",
            quality_class="C2-S1 (good; some saline pockets coastal Tuscan plain)",
            common_contaminants=["nitrate", "copper (vineyard runoff)"],
            fluoride_risk=0.04,
            arsenic_risk=0.03,
            nitrate_risk=0.38,
            notes="Vineyard water management: drip irrigation expanding premium zone. "
                  "Copper accumulation in vineyard soils (historic Bordeaux-mixture use) "
                  "is environmental concern under EU Green Deal.",
        ),

        agronomic_notes=(
            "Tuscany: world's most iconic wine landscape (Chianti, Brunello, Vino Nobile). "
            "Olive fruit fly B. oleae primary constraint; "
            "Xylella advancing risk requires monitoring. "
            "Key research: CREA Firenze, University of Florence Agronomy Dept. "
            "DOCG wine zones → strict agronomic rules limiting inputs."
        ),
    ),

    # ─────────────────────────────────────────────────────────────────────────
    #  SPAIN — 3 major agricultural regions
    # ─────────────────────────────────────────────────────────────────────────

    "spain_castile_leon": StateIntelligence(
        state="Spain — Castile and León (Castilla y León — Meseta Norte)",
        region="North-Central Spain",
        primary_crops=["wheat", "barley", "sugarbeet", "sunflower", "legumes"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Lolium rigidum (rigid ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam"],
                "ACCase + ALS + metabolic",
                "Most important HR weed Spain; confirmed across Castile-León; "
                "Heap 2024; Torra et al. (2017) Weed Sci",
                severity=0.50,
            ),
            WeedResistanceCase(
                "Avena sterilis (wild oat)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "cycloxydim", "pinoxaden"],
                "ACCase",
                "Severe ACCase resistance; major cereal weed Spain; Heap 2024",
                severity=0.45,
            ),
            WeedResistanceCase(
                "Papaver rhoeas (common poppy)",
                "wheat",
                ["tribenuron-methyl", "florasulam", "metsulfuron-methyl"],
                "ALS",
                "ALS resistance widespread Spain; Heap 2024; primary broadleaf problem",
                severity=0.40,
            ),
        ],

        disease_pressure=[
            DiseasePressure("septoria_tritici_blotch","wheat",  0.55, "both",
                "Z. tritici — moderate risk; drier continental Meseta; "
                "risk increases in wetter NW Castile"),
            DiseasePressure("wheat_yellow_rust",      "wheat",  0.40, "rabi",
                "P. striiformis — sporadic epidemics; Cantabrian fringe wetter"),
            DiseasePressure("fusarium_head_blight",   "wheat",  0.35, "both",
                "F. graminearum — risk in wet spring years; DON monitoring AESAN"),
            DiseasePressure("barley_net_blotch",      "barley", 0.40, "both",
                "P. teres — common in spring barley Castile-León; moderate humidity"),
            DiseasePressure("sclerotinia",            "sunflower",0.45, "kharif",
                "S. sclerotiorum (head + stem) — primary sunflower disease; "
                "Spain largest sunflower producer in EU"),
        ],

        insect_pressure=[
            InsectPressure("cereal_aphids",      "wheat",   0.55, "both",
                "S. avenae + Diuraphis noxia — major cereal pests; "
                "D. noxia (Russian wheat aphid) present and expanding"),
            InsectPressure("zabrus_beetle",      "wheat",   0.35, "both",
                "Zabrus tenebrioides — cereal ground beetle; larval root feeding; "
                "NW Spain Meseta endemic; insecticide resistance emerging"),
            InsectPressure("pollen_beetle",      "rapeseed",0.55, "both",
                "M. aeneus — pyrethroid resistance; moderate rapeseed area"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(6.5, 8.5),
            ec_ds_m_range=(0.20, 0.80),
            organic_matter_pct=1.20,
            nitrogen_status="low-medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.22,
            boron_deficient_pct=0.18,
            sulphur_deficient_pct=0.20,
            iron_deficient_pct=0.16,
            dominant_texture="loam to sandy loam",
            dominant_soil_type="Cambisol / Regosol — Meseta plateau on Cretaceous limestone "
                               "and Tertiary sediments; widespread calcareous",
            notes="Castile-León: ~4 M ha arable, Spain's largest cereal region. "
                  "DROUGHT is primary constraint: 350–500 mm/yr, concentrated Nov-Apr. "
                  "Low OM from hot dry summers limiting decomposition. "
                  "Fe/Mn deficiency on calcareous soils. "
                  "Key research: INIA Madrid, CSIC, University of Valladolid.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.50,
            ec_range=(0.25, 1.50),
            ph_range=(7.2, 8.3),
            sar_range=(0.5, 3.5),
            primary_source="Duero / Ebro tributaries for irrigated zones; dryland dominant",
            quality_class="C2-C3, S1-S2 (moderate; higher EC in southern plateau)",
            common_contaminants=["nitrate (irrigated beet/veg zones)", "sodium (SE plateau)"],
            fluoride_risk=0.04,
            arsenic_risk=0.03,
            nitrate_risk=0.40,
            notes="Most Castile-León is DRYLAND (secano); irrigated sugarbeet/maize in Duero valley. "
                  "Climate change reducing snowmelt recharge to Duero basin — "
                  "irrigation water availability decreasing. Drought stress is the "
                  "number-one yield-limiting factor.",
        ),

        agronomic_notes=(
            "Castile-León: Spain's grain belt (wheat + barley > 2 M ha). "
            "Herbicide resistance (Lolium + Avena + Papaver) is primary agronomic challenge. "
            "Drought management through variety selection and sowing date is critical. "
            "Key research: INIA Madrid, ITACYL Valladolid; IVIA soil monitoring."
        ),
    ),

    "spain_andalusia": StateIntelligence(
        state="Spain — Andalusia (Andalucía — southern Spain)",
        region="South Spain",
        primary_crops=["olive", "wheat", "barley", "sunflower", "cotton", "vegetables"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Lolium rigidum (rigid ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "pinoxaden",
                 "mesosulfuron+iodosulfuron", "pyroxasulam", "flupyrsulfuron"],
                "ACCase + ALS + metabolic (worst in Spain)",
                "Guadalquivir valley and Cadiz province: most severe Lolium HR in Spain; "
                "metabolic resistance confirmed; Torra et al. 2017; Heap 2024",
                severity=0.65,
            ),
            WeedResistanceCase(
                "Avena sterilis (winter wild oat)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P"],
                "ACCase",
                "Severe resistance; dominant weed in Seville/Cordoba wheat; Heap 2024",
                severity=0.50,
            ),
            WeedResistanceCase(
                "Phalaris minor (little canary grass)",
                "wheat",
                ["clodinafop-P", "fenoxaprop-P"],
                "ACCase",
                "Spread from IGP; ACCase resistance documented Andalusia; Heap 2024",
                severity=0.30,
            ),
        ],

        disease_pressure=[
            DiseasePressure("xylella_fastidiosa", "olive",  0.55, "both",
                "X. fastidiosa — risk zone; not yet epidemic in Andalusia (Apulia vector) "
                "but EFSA risk maps: Seville/Cordoba in expansion zone; CSIC monitoring"),
            DiseasePressure("septoria_tritici_blotch","wheat",0.50,"both",
                "Z. tritici — moderate; Mediterranean dry summer limits severity"),
            DiseasePressure("barley_net_blotch",  "barley", 0.45, "both",
                "P. teres — primary barley disease Andalusia"),
            DiseasePressure("tuta_absoluta",      "tomato", 0.65, "kharif",
                "T. absoluta — most important tomato pest; year-round Almeria greenhouses; "
                "insecticide resistance to pyrethroids and others widespread"),
            DiseasePressure("grape_downy_mildew", "grapes", 0.50, "both",
                "P. viticola — Sherry + Malaga vine zone; humid spring risk"),
        ],

        insect_pressure=[
            InsectPressure("bactrocera_oleae",   "olive",    0.70, "kharif",
                "B. oleae — primary olive pest; 300 M+ olive trees Andalusia; "
                "population explosion in warm autumn; insecticide resistance"),
            InsectPressure("tuta_absoluta",      "tomato",   0.70, "kharif",
                "T. absoluta — Almeria greenhouse industry (~30,000 ha); "
                "resistance management critical"),
            InsectPressure("cereal_aphids",      "wheat",    0.50, "both",
                "S. avenae + D. noxia — mild winters allow year-round pressure"),
            InsectPressure("rhynchophorus_ferrugineus","grapes",0.40,"kharif",
                "R. ferrugineus (red palm weevil) — palm crops; quarantine pest Andalusia"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.0, 8.8),
            ec_ds_m_range=(0.30, 2.50),
            organic_matter_pct=0.80,
            nitrogen_status="low-medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.25,
            boron_deficient_pct=0.20,
            sulphur_deficient_pct=0.15,
            iron_deficient_pct=0.28,
            dominant_texture="clay to clay loam",
            dominant_soil_type="Vertisol / Luvisol — Guadalquivir alluvial + calcareous "
                               "Betic hillslopes; Almeria: Aridisol/sandy",
            notes="Andalusia: driest agricultural region in EU (200–600 mm/yr). "
                  "Very low OM from semi-arid conditions. "
                  "Fe chlorosis widespread on calcareous (pH 8+) soils. "
                  "Almeria intensive horticulture: plastic greenhouse on poor sandy soils. "
                  "Key research: IFAPA (Junta Andalucía), CSIC Sevilla.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=1.50,
            ec_range=(0.60, 4.50),
            ph_range=(7.2, 8.5),
            sar_range=(1.5, 10.0),
            primary_source="Guadalquivir reservoirs; desalination (Almeria); groundwater (often saline)",
            quality_class="C3-C4, S2-S3 (marginal to unsuitable without management)",
            common_contaminants=["chloride", "sodium", "nitrate (Almeria veg zone)"],
            fluoride_risk=0.05,
            arsenic_risk=0.04,
            nitrate_risk=0.55,
            notes="Water scarcity: primary constraint on Andalusian agriculture. "
                  "Aquifer overexploitation widespread; Doñana wetland under threat. "
                  "Desalinated water: EC 0.3–1.5 dS/m; essential for Almeria greenhouse. "
                  "Climate change scenarios: -20 to -30 % precipitation by 2050.",
        ),

        agronomic_notes=(
            "Andalusia: world's largest olive oil region (25 % global production). "
            "Almeria 'sea of plastic' — largest greenhouse complex on Earth. "
            "Water scarcity and Xylella advance are existential threats. "
            "Key research: IFAPA (Junta de Andalucía), CSIC-IRNAS Sevilla, UPM Madrid."
        ),
    ),

    "spain_aragon": StateIntelligence(
        state="Spain — Aragon (Aragón — Ebro Valley)",
        region="NE Spain",
        primary_crops=["maize", "wheat", "barley", "alfalfa", "sugarbeet", "vegetables"],

        weed_hr_cases=[
            WeedResistanceCase(
                "Echinochloa crus-galli (barnyard grass)",
                "maize",
                ["nicosulfuron", "foramsulfuron", "rimsulfuron"],
                "ALS",
                "ALS resistance in intensively irrigated maize Ebro valley; Heap 2024",
                severity=0.40,
            ),
            WeedResistanceCase(
                "Lolium rigidum (rigid ryegrass)",
                "wheat",
                ["fenoxaprop-P", "clodinafop-P", "mesosulfuron+iodosulfuron"],
                "ACCase + ALS",
                "ACCase resistance widespread irrigated wheat-maize rotations; Heap 2024",
                severity=0.45,
            ),
        ],

        disease_pressure=[
            DiseasePressure("maize_blsb",             "maize",    0.45, "kharif",
                "R. solani — Rhizoctonia in irrigated maize; hot humid Ebro summer"),
            DiseasePressure("septoria_tritici_blotch", "wheat",    0.50, "both",
                "Z. tritici — moderate; semi-arid continental climate"),
            DiseasePressure("beet_yellows_virus",      "sugarbeet",0.40, "kharif",
                "BMYV/BYV — aphid-vectored; Ebro beet zone"),
            DiseasePressure("fusarium_head_blight",    "wheat",    0.35, "both",
                "F. graminearum — risk in wet spring years Prepyrénées"),
            DiseasePressure("sclerotinia",             "sunflower",0.40, "kharif",
                "S. sclerotiorum — irrigated sunflower; humid periods at flowering"),
        ],

        insect_pressure=[
            InsectPressure("corn_rootworm", "maize",   0.55, "kharif",
                "D. virgifera — western corn rootworm; serious Ebro Valley "
                "maize monocultures since 2010; crop rotation essential"),
            InsectPressure("cereal_aphids", "wheat",   0.45, "both",
                "S. avenae — BYDV vector; semi-continental Ebro"),
            InsectPressure("beet_aphid",    "sugarbeet",0.45, "kharif",
                "M. persicae — BYD vector; warm Ebro summers"),
        ],

        soil_fertility=SoilFertilityProfile(
            ph_range=(7.5, 8.5),
            ec_ds_m_range=(0.30, 2.00),
            organic_matter_pct=1.50,
            nitrogen_status="medium",
            phosphorus_status="medium",
            potassium_status="medium",
            zinc_deficient_pct=0.18,
            boron_deficient_pct=0.16,
            sulphur_deficient_pct=0.18,
            iron_deficient_pct=0.20,
            dominant_texture="loam to clay loam",
            dominant_soil_type="Cambic Fluvisol / Calcisol — Ebro alluvium + Mesozoic "
                               "limestone hillslopes; some gypsiferous Regosols",
            notes="Ebro basin: intensively irrigated cereal zone. "
                  "Gypsiferous soils in Bardenas: moderate salinity. "
                  "Fe chlorosis on calcareous. "
                  "Key research: CITA Aragón, University of Zaragoza.",
        ),

        irrigation_water=IrrigationWaterProfile(
            typical_ec_ds_m=0.90,
            ec_range=(0.40, 2.50),
            ph_range=(7.5, 8.3),
            sar_range=(1.0, 5.0),
            primary_source="Ebro River irrigation canals (major Pyrenean snowmelt source)",
            quality_class="C2-C3, S1-S2 (good-moderate quality)",
            common_contaminants=["nitrate", "sodium (downstream reaches)"],
            fluoride_risk=0.04,
            arsenic_risk=0.03,
            nitrate_risk=0.40,
            notes="Ebro canal water: EC generally 0.3–1.2 dS/m; good for most crops. "
                  "Climate change: Pyrenean snowmelt timing shifting — "
                  "April-June peak advancing, summer flows declining.",
        ),

        agronomic_notes=(
            "Aragón/Ebro: Spain's most intensively irrigated region. "
            "Diabrotica rootworm expanding with maize monoculture. "
            "Herbicide resistance (Lolium + Echinochloa) primary management challenge. "
            "Key research: CITA Aragón (Centro de Investigación y Tecnología Agroalimentaria)."
        ),
    ),

})


def get_eu_region_intel(region_key: str):
    """Return EU location intelligence for a region key."""
    return EU_LOCATION_INTELLIGENCE.get(region_key)


def list_eu_regions() -> list[str]:
    return list(EU_LOCATION_INTELLIGENCE.keys())
