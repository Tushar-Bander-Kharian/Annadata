# Annadata v2 — Crop Yield Potential Simulator

Annadata is a deterministic, physics-based crop yield simulator that combines agronomic stress modelling with LLM-powered agronomist agents. Version 2 adds a full browser UI, ICAR variety database, quantitative biotic stress engine, and India state-wise location intelligence.

```
┌────────────────────────────────────────────────────┐
│               ANNADATA  v2                         │
│       Crop Yield Potential Simulator               │
│       + Browser UI + Variety DB + Location Intel   │
└────────────────────────────────────────────────────┘
```

---

## What's New in v2

| Feature | v1 | v2 |
|---|---|---|
| Interface | Terminal CLI | Browser UI + CLI |
| Stress factors | 6 abiotic | 6 abiotic + biotic (disease/weed/insect) |
| Varieties | Generic | 30+ ICAR/CIMMYT named varieties |
| Location intelligence | — | 12 Indian states (HR weeds, diseases, soil, water) |
| Nutrient stress | NPK from soil | NPK + Zn sliders + Liebig's Law |
| Disease model | — | Environment × disease interaction (T × RH) |
| LLM backends | Grok / Claude / Ollama | Same — now accessible from browser |

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

The UI has 7 panels accessible from the left sidebar:

**1. Setup**
- Select crop and named ICAR/CIMMYT variety
- Set sowing date and location
- Choose LLM backend (Ollama / Claude / Grok)

**2. Location Intel**
- Select your state to auto-load:
  - Confirmed herbicide resistance cases (species, MOA, severity)
  - Disease pressure by crop and season
  - Insect/pest pressure
  - Soil fertility status (NPK, Zn, B deficiencies)
  - Irrigation water quality (EC, fluoride, arsenic, nitrate risks)
- Soil and water fields auto-fill from state data

**3. Stress Controls**
- Abiotic sliders: Heat, Drought, Waterlogging, Salinity, Cold
- Biotic sliders: Weed competition, Insect pressure
- Per-disease severity sliders (auto-populated from location intel)
- Disease severity modulated by real-time weather (T × RH interaction)

**4. Soil & Fertility**
- Soil texture, pH, EC, N, P, K, organic matter
- Nutrient deficiency override sliders (N, P, K, Zn)
- Irrigation water EC, pH, method

**5. Results**
- Simulated yield vs potential yield
- Yield gap percentage
- Limiting factors ranked by impact
- Weekly combined stress factor chart
- Factor component breakdown chart
- Agronomic alerts

**6. AI Agronomist**
- Streams a structured advisory report from your chosen LLM
- Covers: Season Summary, Primary Constraints, Field Observations, Recommendations

**7. Variety Cards**
- Browse all ICAR/CIMMYT varieties by crop
- View stress tolerance modifiers, disease resistance genes, release info

---

## Running the Original Terminal Version

```bash
set ANNADATA_BACKEND=ollama
set ANNADATA_MODEL=aya-expanse:8b
python -m annadata.main
```

---

## Supported LLM Backends

### Ollama (local — recommended)
```bash
# Pull any model
ollama pull aya-expanse:8b     # multilingual, good for Indian farming context
ollama pull qwen2.5:7b         # fast, good quality
ollama pull llama3.2:3b        # fastest, smaller

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

---

## Location Intelligence — States Covered

Punjab · Haryana · Uttar Pradesh · Madhya Pradesh · Maharashtra · Rajasthan · Bihar · Chhattisgarh · Andhra Pradesh · Karnataka · West Bengal · Odisha · Assam · Gujarat

Each state includes confirmed herbicide resistance cases, disease/insect pressure profiles, soil fertility status, and irrigation water quality data from peer-reviewed sources.

---

## Stress Model

Each factor returns **[0.0 – 1.0]** where 1.0 = optimal, 0.0 = crop failure.

| Factor | Basis |
|---|---|
| Temperature | Trapezoidal response curve |
| Water | Supply ÷ ET₀ × Kc water balance |
| Salinity | FAO-29 linear yield loss above EC threshold |
| Soil pH | Trapezoidal response |
| Nutrients | Liebig's Law of the Minimum (N, P, K, Zn) |
| Solar Radiation | Fraction of optimal 140 MJ/m² |
| Disease | Sigmoid penalty × variety resistance × environment modifier (T × RH) |
| Weeds | Sigmoid penalty × herbicide resistance factor from location intel |
| Insects | Sigmoid penalty |

**Combined** = Temperature × Water × Salinity × pH × Nutrients × Radiation × Biotic

---

## Project Structure

```
annadata/
├── config.py              # crop database, soil textures, presets
├── main.py                # terminal CLI entry point
├── llm.py                 # LLM backend (Grok / Claude / Ollama)
│
├── data/
│   ├── varieties.py       # ICAR/CIMMYT variety database (30+ varieties)
│   ├── stress_responses.py # quantitative stress-yield response curves
│   └── location_intel.py  # India state-wise intelligence (14 states)
│
├── web/
│   ├── app.py             # Flask web application
│   └── templates/
│       └── index.html     # browser UI
│
├── engine/
│   ├── stress.py          # original 6 abiotic stress factor functions
│   └── simulator.py       # week-by-week simulation loop (v2 updated)
│
├── agents/
│   ├── stage_analyst.py   # LLM stage assessment agent
│   └── agronomist.py      # LLM final report agent
│
├── climate/
│   ├── geocoder.py        # city name → lat/lon
│   └── fetcher.py         # Open-Meteo archive API → weekly climate
│
└── models/
    ├── inputs.py          # CropVariety, SoilState, WaterQuality, StressOverrides
    ├── climate.py         # WeeklyClimate, SeasonClimate
    └── state.py           # WeeklyStress, SimulationResult
```

---

## Data Sources

| Data | Source |
|---|---|
| Historical weather | Open-Meteo Archive API (free, no key) |
| Variety data | ICAR Annual Reports 2022–2024, DWR, NRRI, PAU |
| Drought yield loss | Daryanto et al. 2016/2017 meta-analysis |
| Heat stress | Zachariah et al. 2021, GRL; Frontiers 2023 |
| Disease yield loss | Savary et al. 2016 Food Security; Ficke 2016 |
| Weed HR cases | Soni et al. 2023 Phytoparasitica; Frontiers Agronomy 2026 |
| Soil fertility | Agriculture.Institute 2025; ICRIER soil health report |
| Irrigation water | CGWB state groundwater data; state agricultural universities |
| Salinity response | FAO Irrigation & Drainage Paper No. 29 |

---

## License

Research and educational use. Crop parameters derived from FAO and ICAR literature. Regional data from published peer-reviewed sources.
