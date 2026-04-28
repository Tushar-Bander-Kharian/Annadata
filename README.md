# Annadata v2 — Crop Yield Potential Simulator

Annadata is a deterministic, physics-based crop yield simulator that combines agronomic stress modelling with LLM-powered agronomist agents. Version 2 adds a full browser UI, ICAR variety database, quantitative biotic stress engine, India state-wise location intelligence, and comprehensive EU regional intelligence covering 7 countries.

```
┌────────────────────────────────────────────────────┐
│               ANNADATA  v2                         │
│       Crop Yield Potential Simulator               │
│  Browser UI · Variety DB · Global Location Intel  │
└────────────────────────────────────────────────────┘
```

---

## What's New in v2 (Latest)

| Feature | v1 | v2 |
|---|---|---|
| Interface | Terminal CLI | Browser UI + CLI |
| Stress factors | 6 abiotic | 6 abiotic + biotic (disease/weed/insect) |
| Varieties | Generic | 30+ ICAR/CIMMYT named varieties |
| Location intelligence | — | 14 Indian states + 7 EU countries (23 EU regions) |
| Disease model | — | Environment × disease interaction (T × RH) |
| EU disease keys | — | 40+ Europe-specific disease/pest/weed keys |
| LLM report context | India only | Location-aware (India vs EU) |
| Monte Carlo | — | N=5–500 runs, yield distribution + sensitivity |

---

## Running the Browser UI

### Step 1 — Install dependencies
```bash
pip install flask flask-cors httpx rich anthropic
```

### Step 2 — Start Ollama (in a separate terminal)
```bash
ollama pull aya-expanse:8b
ollama serve
```

### Step 3 — Start the web server
```bash
# Windows CMD
set ANNADATA_BACKEND=ollama
set ANNADATA_MODEL=aya-expanse:8b
python -m annadata.web.app

# macOS / Linux
export ANNADATA_BACKEND=ollama
export ANNADATA_MODEL=aya-expanse:8b
python -m annadata.web.app
```

### Step 4 — Open browser
```
http://localhost:5000
```

---

## Browser UI Walkthrough

**1. Setup** — Select crop, named variety, sowing date, location, LLM backend

**2. Location Intel** — Select state/region to auto-load confirmed HR weed cases, disease pressure by crop, insect/pest pressure, soil fertility status, irrigation water quality

**3. Stress Controls** — Abiotic sliders (Heat, Drought, Waterlogging, Salinity, Cold) + Biotic (weed, insect, per-disease severity)

**4. Soil & Fertility** — Texture, pH, EC, N, P, K, OM, Zn; irrigation water EC/pH/method

**5. Results** — Simulated yield vs potential, yield gap %, limiting factors ranked, weekly stress charts, agronomic alerts

**6. AI Agronomist** — Streaming LLM advisory (Season Summary → Constraints → Recommendations). Auto-detects India vs EU context.

**7. Variety Cards** — Browse ICAR/CIMMYT varieties with stress tolerance modifiers and disease resistance genes

---

## Running the Terminal Version

```bash
set ANNADATA_BACKEND=ollama
set ANNADATA_MODEL=aya-expanse:8b
python -m annadata.main
```

---

## Supported LLM Backends

### Ollama (local — recommended)
```bash
ollama pull aya-expanse:8b     # multilingual
ollama pull qwen2.5:7b         # fast
set ANNADATA_BACKEND=ollama
set ANNADATA_MODEL=aya-expanse:8b
```

### Claude (Anthropic)
```bash
set ANNADATA_BACKEND=claude
set ANTHROPIC_API_KEY=sk-ant-...
set ANNADATA_MODEL=claude-sonnet-4-6
```

### Grok (xAI)
```bash
set ANNADATA_BACKEND=grok
set GROK_API_KEY=xai-...
set ANNADATA_MODEL=grok-3-mini
```

---

## Location Intelligence Coverage

### India — 14 States
Punjab · Haryana · Uttar Pradesh · Madhya Pradesh · Maharashtra · Rajasthan · Bihar · Chhattisgarh · Andhra Pradesh · Karnataka · West Bengal · Odisha · Assam · Gujarat

### Europe — 7 Countries, 23 Regions

| Country | Regions | Key crops |
|---------|---------|-----------|
| **Germany** | Saxony-Anhalt, Bavaria, Lower Saxony, NRW, Mecklenburg, Brandenburg | Wheat, rapeseed, sugarbeet, potato, barley |
| **France** | Paris Basin, Brittany/Normandy, South-West | Wheat, maize, rapeseed, grapes, sunflower |
| **Poland** | Greater Poland, Masovia, West Pomerania | Rapeseed, wheat, potato, sugarbeet |
| **UK** | East Anglia, East Midlands, Scotland | Wheat, barley, rapeseed, potato |
| **Netherlands** | Clay Polders, Sandy East | Potato, onion, vegetables, maize |
| **Italy** | Po Valley, Apulia, Tuscany | Wheat, maize, olive, grapes, tomato |
| **Spain** | Castile-León, Andalusia, Aragon | Wheat, barley, olive, sunflower, maize |

Each region includes:
- Confirmed **herbicide resistance** cases (species, mechanism, severity 0–1)
- **Disease pressure** by crop (risk level 0–1, season, literature citations)
- **Insect/pest pressure** profiles
- **Soil fertility** status (pH, EC, OM, NPK, micronutrient deficiency %)
- **Irrigation water quality** (EC, SAR, contamination risks)
- **Agronomic notes** with key research institutions

---

## Disease & Pest Key Coverage

### India crops
wheat yellow/leaf/stem rust, Septoria, Fusarium head blight, karnal bunt, rice blast, sheath blight, bacterial blight, maize BLSB, turcicum, soybean YMV, chickpea wilt, Alternaria blight, late blight, bacterial wilt, BPH, BYDV...

### Europe-specific keys (added v2)
`septoria_tritici_blotch` · `phoma_stem_canker` · `sclerotinia_rapeseed` · `cercospora_leaf_spot` · `beet_yellows_virus` · `barley_net_blotch` · `barley_yellow_dwarf` · `wheat_eyespot` · `wheat_powdery_mildew` · `rapeseed_light_leaf_spot` · `potato_late_blight` · `rhizoctonia_root_rot` · `grape_downy_mildew` · `grape_powdery_mildew` · `xylella_fastidiosa` · `tuta_absoluta` · `clubroot` · `ramularia_leaf_spot` · `nematode_potato` · `fusarium_dry_rot_potato` · `fusarium_crown_rot` · `pyrenophora_tritici` · `aphanomyces_root_rot`

---

## Supported Crops & Varieties

| Crop | Varieties |
|---|---|
| Wheat | HD-2967, HD-3385, DBW-187, DBW-303, PBW-343, K-307, HD-3226, Raj-4120 |
| Rice | Pusa 44, MTU 1010, Sahbhagi Dhan, Swarna Sub1, DRR Dhan 44, Pusa Basmati 1121 |
| Maize | DHM 117, HQPM 1, Vivek QPM 9, NK 6240 |
| Soybean | JS 335, MACS 1407, NRC 7 |
| Chickpea | JG 11, KAK 2, Pusa 256, JAKI 9218 |
| Mustard | RH 749, NRCHB 101, Pusa Tarak |
| Tomato | Pusa Ruby, Arka Vikas |
| Potato | Kufri Jyoti, Kufri Bahar, Kufri Pushkar |

**40+ additional crops** in simulation engine: barley, sunflower, rapeseed, sugarcane, bajra, jowar, groundnut, lentil, pigeonpea, onion, okra, brinjal, cauliflower, cabbage, pea, carrot, garlic, spinach, cumin, coriander, chilli, turmeric, ginger, mango, banana, citrus, grapes, guava, pomegranate, papaya, watermelon, marigold, chrysanthemum

---

## Stress Model

Each factor returns **[0.0 – 1.0]** where 1.0 = optimal, 0.0 = crop failure.

| Factor | Basis |
|---|---|
| Temperature | Trapezoidal response curve (crop-specific thresholds) |
| Water | Supply ÷ ET₀ × Kc weekly water balance |
| Salinity | FAO-29 linear yield loss above EC threshold |
| Soil pH | Trapezoidal response (crop-specific optimal range) |
| Nutrients | Liebig's Law of the Minimum (N, P, K, Zn) |
| Solar Radiation | Fraction of optimal 140 MJ/m²/week |
| Disease | Sigmoid penalty × variety resistance × environment modifier (T × RH) |
| Weeds | Sigmoid penalty × herbicide resistance factor from location intel |
| Insects | Sigmoid penalty |

**Combined** = Temperature × Water × Salinity × pH × Nutrients × Radiation × Biotic

---

## Regional Soil Presets (61 total)

Presets covering India (Punjab, UP/Bihar, Central, South), Germany (6 regions), France (3), Poland (3), UK (3), Netherlands (2), Italy (3), Spain (3), plus East Asia, SE Asia, Africa, Latin America, North America, Central Asia/Mid-East, Australia.

Soil parameters: texture, pH (CaCl₂ method for EU), EC (dS/m), N/P/K (kg/ha), organic matter %. Sources: BGR, INRAE, JRC ESDAC, FAO HWSD, ICAR, SoilGrids 250m.

---

## Project Structure

```
annadata/
├── config.py              # crop database (40+ crops), soil textures, 61 regional presets
├── main.py                # terminal CLI entry point
├── llm.py                 # LLM backend (Grok / Claude / Ollama)
│
├── data/
│   ├── varieties.py           # ICAR/CIMMYT variety database (30+ varieties)
│   ├── stress_responses.py    # quantitative stress-yield response curves (70+ disease keys)
│   ├── location_intel.py      # India state-wise intelligence (14 states)
│   └── location_intel_eu.py   # EU regional intelligence (7 countries, 23 regions)
│
├── web/
│   ├── app.py             # Flask REST API + SSE streaming
│   └── templates/
│       └── index.html     # browser SPA
│
├── engine/
│   ├── stress.py          # abiotic stress factor functions
│   └── simulator.py       # week-by-week simulation loop
│
├── agents/
│   ├── stage_analyst.py   # LLM stage assessment agent
│   └── agronomist.py      # LLM final report agent (location-aware: India/EU)
│
├── climate/
│   ├── geocoder.py        # city name → lat/lon (Open-Meteo)
│   └── fetcher.py         # historical climate archive (Open-Meteo, free, no key)
│
└── models/
    ├── inputs.py          # CropVariety, SoilState, WaterQuality, StressOverrides
    ├── climate.py         # WeeklyClimate, SeasonClimate
    └── state.py           # WeeklyStress, SimulationResult
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/crops` | GET | All crops with base parameters |
| `/api/varieties/<crop>` | GET | Named varieties + stress modifiers |
| `/api/states` | GET | Available states/regions for location intel |
| `/api/location-intel/<state>/<crop>` | GET | Regional HR weeds, diseases, insects, soil, water |
| `/api/soil-presets` | GET | All 61 regional soil presets grouped |
| `/api/regions` | GET | Region selector groups for UI |
| `/api/cities/<region_key>` | GET | Major agricultural cities per region |
| `/api/disease-list/<crop>` | GET | Disease keys relevant to crop with max penalties |
| `/api/simulate` | POST | Single simulation run → yield + weekly stress |
| `/api/simulate-multi` | POST | Monte Carlo (N runs) → yield distribution + sensitivity |
| `/api/llm-report` | POST | Streaming LLM agronomist report (SSE) |

---

## Data Sources

| Data | Source |
|---|---|
| Historical weather | Open-Meteo Archive API (free, no key required) |
| Variety data | ICAR Annual Reports 2022–2024, DWR, NRRI, PAU |
| Drought yield loss | Daryanto et al. 2016/2017 meta-analysis |
| Heat stress | Zachariah et al. 2021 GRL; Frontiers 2023 |
| Disease yield loss | Savary et al. 2016 Food Security; Ficke 2016 |
| EU disease data | JKI (Germany), INRAE (France), IUNG (Poland), ADAS/Rothamsted (UK), WUR (NL), CREA (Italy), INIA-CSIC (Spain) |
| Weed HR cases | Heap I. (2024) International HR Weed Database; Fischer et al. 2015; Torra et al. 2017 |
| EU soil data | BGR BUEK-200, JRC ESDAC, Thünen Atlas 2023, UBA monitoring |
| India soil fertility | Agriculture.Institute 2025; ICRIER; NBSS&LUP state surveys |
| Salinity response | FAO Irrigation & Drainage Paper No. 29 |

---

## License

Research and educational use. Crop parameters derived from FAO and ICAR literature. Regional intelligence data from peer-reviewed sources (cited inline in source files).
