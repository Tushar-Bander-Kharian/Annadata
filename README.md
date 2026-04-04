# Annadata — Crop Yield Potential Simulator

Annadata is a deterministic, physics-based crop yield simulator that combines agronomic stress modelling with LLM-powered agronomist agents. It runs a week-by-week simulation of a full growing season — computing six multiplicative stress factors against real historical climate data — and generates a plain-language field report at every growth stage transition plus a final advisory at harvest.

```
┌────────────────────────────────────────────────────┐
│               ANNADATA                             │
│       Crop Yield Potential Simulator               │
└────────────────────────────────────────────────────┘

  Crop: Wheat (Triticum aestivum) — HD-2967
  Location: Ludhiana, Punjab (30.901°, 75.857°)
  Season: 2024-11-01 → 2025-03-01  (17 weeks)

  W01 GERM  T:0.91 W:0.84  S:1.00 N:0.87  ▶ 0.79
  W02 GERM  T:0.88 W:0.90  S:1.00 N:0.87  ▶ 0.82
  ...
  ╔════════════════════ STAGE: REPRODUCTIVE ═════════╗
  ║  Crop is AT RISK — water stress in weeks 9-11... ║
  ╚══════════════════════════════════════════════════╝

  Simulated yield:  4.72 t/ha  (yield gap: 21.3%)
  Top limiting factors:
    1. Water stress
    2. Temperature stress
    3. Low solar radiation
```

---

## Table of Contents

- [Features](#features)
- [How It Works](#how-it-works)
- [Stress Factor Model](#stress-factor-model)
- [Supported Crops](#supported-crops)
- [Regional Soil Presets](#regional-soil-presets)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running with Different LLM Backends](#running-with-different-llm-backends)
  - [Grok (xAI) — Default](#grok-xai--default)
  - [Claude (Anthropic)](#claude-anthropic)
  - [Ollama (Local, No API Key)](#ollama-local-no-api-key)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [Adding More Regional Presets](#adding-more-regional-presets)
- [Data Sources](#data-sources)

---

## Features

### Simulation Engine
- **Week-by-week deterministic yield model** — computes six independent stress factors every week of the growing season and combines them multiplicatively to calculate final yield
- **Four growth stages** — germination, vegetative, reproductive, maturity — each with configurable stage weight and duration boundaries
- **Stage-weighted yield accumulation** — reproductive stage carries the highest weight (50%) matching FAO agronomic standards
- **Heat sterility penalty** — automatically applies a 20% yield reduction when three or more consecutive weeks exceed the crop's critical temperature during the reproductive stage (grain-fill period)
- **Liebig's Law of Minimum** for nutrients — the most deficient nutrient limits yield, not an average
- **Organic matter bonus** — soils with >2% OM release extra nitrogen via mineralization

### Climate Data
- **Real historical weather** fetched automatically from the [Open-Meteo archive API](https://open-meteo.com/) — no API key required
- **Automatic geocoding** of any city or district name via Open-Meteo geocoding API
- Daily data aggregated to weekly: mean/max/min temperature, precipitation, solar radiation, ET₀ (FAO-56 reference evapotranspiration), wind speed

### LLM Agronomist Agents
- **Stage analyst** — called once per growth stage transition; receives averaged stress factors and climate context; produces a 3–4 sentence field observation (ON TRACK / AT RISK / SEVERELY STRESSED)
- **Final agronomist report** — written at harvest; structured advisory including season summary, primary constraints, field observations, and four specific recommendations for the next season
- **Pluggable backends** — switch between Grok, Claude, or local Ollama with a single environment variable

### Inputs & Presets
- **Seven crops** with calibrated agronomic parameters
- **Six soil textures** (sandy to clay) with drainage and water-holding properties
- **Five irrigation methods** (rainfed, drip, flood, furrow, sprinkler) with weekly water-supply estimates
- **Regional soil presets** loaded from peer-reviewed field data — currently covers three Punjab districts; designed to expand to all Indian states

### Output Display
- Colour-coded Rich terminal UI with progress bars for each stress factor every week
- Climate data preview table before simulation
- Input summary panel showing all parameters at a glance
- Critical alerts panel for temperature, water, and salinity threshold breaches
- Final yield outcome table with potential vs. simulated yield and yield gap percentage

---

## How It Works

```
User inputs
  ├── Crop selection + variety label
  ├── Soil parameters (or regional preset)
  ├── Water quality + irrigation method
  ├── Sowing date
  └── Location (city / district name)
        │
        ▼
  Geocoder → lat/lon
        │
        ▼
  Open-Meteo API → historical daily climate → weekly aggregates
        │
        ▼
  ┌─────────────────────────────────────────┐
  │  Week-by-week simulation loop           │
  │                                         │
  │  For each week:                         │
  │    1. Identify growth stage             │
  │    2. Interpolate crop coefficient (Kc) │
  │    3. Compute 6 stress factors          │
  │    4. Multiply → combined factor        │
  │    5. Accumulate stage-weighted yield   │
  │    6. Check alert thresholds            │
  │                                         │
  │  On stage transition:                   │
  │    └── Call LLM Stage Analyst           │
  └─────────────────────────────────────────┘
        │
        ▼
  Compute final yield + yield gap
        │
        ▼
  Call LLM Agronomist → final advisory report
        │
        ▼
  Rich terminal display
```

---

## Stress Factor Model

Each factor returns a value in **[0.0, 1.0]** where 1.0 = optimal and 0.0 = crop failure. The six factors are multiplied together each week.

| Factor | Formula basis | Key parameters |
|---|---|---|
| **Temperature** | Trapezoidal response curve (standard agronomy) | `critical_temp_low`, `optimal_temp_min/max`, `critical_temp_high` |
| **Water** | Water balance ratio (supply ÷ ET₀ × Kc) | Irrigation method, soil texture, waterlogging penalty for clay+flood |
| **Salinity** | FAO-29 linear yield loss above EC threshold | `ec_threshold_ds_m`, `ec_slope_pct_per_ds_m`, soil EC = 0.7 × irrigation EC |
| **Soil pH** | Trapezoidal response (full score inside optimal range) | `optimal_ph_min/max`, hard floor at pH 4.5 and ceiling at pH 9.0 |
| **Nutrients** | Liebig's Law of the Minimum (N, P, K separately) | Crop demand per tonne × base yield; OM bonus if >2% |
| **Solar radiation** | Fraction of optimal weekly radiation (140 MJ/m²) | Floor at 0.30 — cloudy weeks still support growth |

**Combined weekly factor** = T × W × S × pH × N × Rad

**Final yield** = base\_yield × Σ(combined × stage\_weight) / Σ(stage\_weight)

---

## Supported Crops

| Key | Crop | Base yield (t/ha) | Season (days) |
|---|---|---|---|
| `wheat` | Wheat (*Triticum aestivum*) | 6.0 | 120 |
| `rice` | Rice (*Oryza sativa*) | 8.0 | 130 |
| `maize` | Maize/Corn (*Zea mays*) | 9.0 | 100 |
| `cotton` | Cotton (*Gossypium hirsutum*) | 2.5 | 160 |
| `soybean` | Soybean (*Glycine max*) | 3.5 | 110 |
| `tomato` | Tomato (*Solanum lycopersicum*) | 40.0 | 100 |
| `potato` | Potato (*Solanum tuberosum*) | 30.0 | 110 |

---

## Regional Soil Presets

Instead of entering soil parameters manually, select a preset based on the actual location of your field. Presets are derived from measured field data collected in peer-reviewed agricultural theses.

### Punjab (currently available)

| Preset key | District | Texture | pH | OM% | Olsen-P (kg/ha) | Avail-K (kg/ha) |
|---|---|---|---|---|---|---|
| `punjab_mansa` | Mansa | sandy loam | 8.46 | 0.52 | 32.5 | 443.9 |
| `punjab_ludhiana` | Ludhiana | sandy loam | 7.69 | 1.00 | 48.9 | 374.5 |
| `punjab_patiala` | Patiala | loam | 7.71 | 0.93 | 115.4 | 493.0 |

**Data sources:**
- Sravanthi Y. (2022). *Assessment of soil fertility status in three districts of Punjab.* M.Sc. Thesis, PAU Ludhiana. (340 soil samples, 0–30 cm depth)
- Mondal S. (2017). *Soil quality indicators under different land use systems in Ludhiana.* Ph.D. Thesis, PAU Ludhiana. (Ladian village, rice-wheat system)

All individual values can be overridden after loading a preset.

---

## Installation

**Requirements:** Python 3.11 or later

### 1. Clone the repository

```bash
git clone https://github.com/Tushar-Bander-Kharian/Annadata.git
cd Annadata
```

### 2. Create and activate a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install the package

```bash
pip install -e .
```

This installs all dependencies (`httpx`, `rich`, `anthropic`) and registers the `annadata` command.

---

## Quick Start

```bash
# Set your API key for the default backend (Grok)
set GROK_API_KEY=your-key-here       # Windows CMD
$env:GROK_API_KEY="your-key-here"    # Windows PowerShell
export GROK_API_KEY="your-key-here"  # macOS / Linux

# Run the simulator
annadata
# or equivalently:
python -m annadata.main
```

You will be prompted interactively for:

1. **Crop** — choose from the list or type a key (e.g. `wheat`)
2. **Variety label** — free text (e.g. `HD-2967`, `local`)
3. **Soil parameters** — optionally load a regional preset, then confirm or override each value
4. **Water quality** — irrigation EC, pH, and method
5. **Sowing date** — defaults to one year ago (ensures archive weather data is available)
6. **Location** — any city or district name (e.g. `Ludhiana`, `New Delhi`, `Nagpur`)

The simulation then runs automatically, streaming weekly stress factors to the terminal.

---

## Running with Different LLM Backends

### Grok (xAI) — Default

Grok is the default backend. Get a free API key from [console.x.ai](https://console.x.ai).

```bash
# Windows CMD
set GROK_API_KEY=xai-xxxxxxxxxxxxxxxx
set ANNADATA_BACKEND=grok
annadata

# Windows PowerShell
$env:GROK_API_KEY="xai-xxxxxxxxxxxxxxxx"
$env:ANNADATA_BACKEND="grok"
annadata

# macOS / Linux
export GROK_API_KEY="xai-xxxxxxxxxxxxxxxx"
export ANNADATA_BACKEND="grok"
annadata
```

Default model: `grok-3-mini`. Override with `ANNADATA_MODEL=grok-3` for higher quality.

---

### Claude (Anthropic)

Get an API key from [console.anthropic.com](https://console.anthropic.com).

```bash
# Windows CMD
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx
set ANNADATA_BACKEND=claude
annadata

# Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"
$env:ANNADATA_BACKEND="claude"
annadata

# macOS / Linux
export ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"
export ANNADATA_BACKEND="claude"
annadata
```

Default model: `claude-haiku-4-5-20251001`. Override with `ANNADATA_MODEL=claude-sonnet-4-6` for more detailed agronomic reports.

```bash
# Example: use Sonnet for higher-quality reports
set ANNADATA_BACKEND=claude
set ANTHROPIC_API_KEY=sk-ant-...
set ANNADATA_MODEL=claude-sonnet-4-6
annadata
```

---

### Ollama (Local, No API Key)

Run LLM agents entirely on your own machine — no internet connection required for the LLM (weather data still needs internet).

**Step 1 — Install Ollama** from [ollama.com](https://ollama.com)

**Step 2 — Pull a model:**

```bash
ollama pull qwen2.5:7b        # default, good balance of speed and quality
ollama pull llama3.2:3b       # faster, smaller
ollama pull mistral:7b        # alternative
```

**Step 3 — Start Ollama** (it usually starts automatically after install):

```bash
ollama serve
```

**Step 4 — Run Annadata:**

```bash
# Windows CMD
set ANNADATA_BACKEND=ollama
annadata

# Windows PowerShell
$env:ANNADATA_BACKEND="ollama"
annadata

# macOS / Linux
export ANNADATA_BACKEND="ollama"
annadata
```

Default model: `qwen2.5:7b`. Override with `ANNADATA_MODEL=llama3.2:3b`.

If Ollama is running on a different machine or port:

```bash
set OLLAMA_URL=http://192.168.1.10:11434
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANNADATA_BACKEND` | `grok` | LLM backend: `grok`, `claude`, or `ollama` |
| `ANNADATA_MODEL` | backend-specific | Override the model name for both stage and report agents |
| `GROK_API_KEY` | — | Required when `ANNADATA_BACKEND=grok` |
| `ANTHROPIC_API_KEY` | — | Required when `ANNADATA_BACKEND=claude` |
| `OLLAMA_URL` | `http://localhost:11434` | Base URL for a local or remote Ollama instance |

---

## Project Structure

```
annadata/
├── pyproject.toml              # package metadata and dependencies
└── annadata/
    ├── config.py               # crop database, soil textures, stage weights,
    │                           # irrigation rates, regional soil presets
    ├── main.py                 # interactive CLI entry point
    ├── llm.py                  # LLM backend abstraction (Grok / Claude / Ollama)
    │
    ├── engine/
    │   ├── stress.py           # pure math: all six stress factor functions
    │   └── simulator.py        # deterministic week-by-week simulation loop
    │
    ├── agents/
    │   ├── stage_analyst.py    # LLM agent: per-stage field assessment
    │   └── agronomist.py       # LLM agent: final harvest advisory report
    │
    ├── climate/
    │   ├── geocoder.py         # city name → lat/lon via Open-Meteo
    │   └── fetcher.py          # lat/lon + dates → SeasonClimate via Open-Meteo archive
    │
    ├── models/
    │   ├── inputs.py           # CropVariety, SoilState, WaterQuality dataclasses
    │   ├── climate.py          # WeeklyClimate, SeasonClimate dataclasses
    │   └── state.py            # WeeklyStress, SimulationResult dataclasses
    │
    └── display/
        └── renderer.py         # Rich terminal UI: tables, panels, progress bars
```

---

## Adding More Regional Presets

To add soil presets for another state, open `annadata/config.py` and follow the Punjab pattern:

```python
# Example: Haryana presets
HARYANA_SOIL_PRESETS: dict[str, dict] = {
    "haryana_karnal": {
        "display_name": "Haryana - Karnal district (loam, rice-wheat zone)",
        "texture": "loam",
        "ph": 7.8,
        "ec_ds_m": 0.45,
        "nitrogen_kg_ha": 85.0,
        "phosphorus_kg_ha": 42.0,
        "potassium_kg_ha": 310.0,
        "organic_matter_pct": 0.85,
    },
    # add more districts ...
}

# Then register it in the master index:
REGION_SOIL_PRESETS: dict[str, dict[str, dict]] = {
    "Punjab":  PUNJAB_SOIL_PRESETS,
    "Haryana": HARYANA_SOIL_PRESETS,   # <-- new entry
}
```

No changes to `main.py` are needed — presets are loaded dynamically from `REGION_SOIL_PRESETS`.

---

## Data Sources

| Data | Source | Cost |
|---|---|---|
| Historical daily weather | [Open-Meteo Archive API](https://archive-api.open-meteo.com/) | Free, no key |
| Geocoding | [Open-Meteo Geocoding API](https://geocoding-api.open-meteo.com/) | Free, no key |
| Punjab soil data (Mansa, Ludhiana, Patiala) | Sravanthi (2022), Mondal (2017) — PAU Ludhiana theses | Published research |
| Crop agronomic parameters | FAO crop manuals, ICAR recommendations | Public domain |
| Salinity response curves | FAO Irrigation and Drainage Paper No. 29 | Public domain |
| ET₀ calculation | FAO-56 Penman-Monteith (computed by Open-Meteo) | Public domain |

---

## License

This project is for research and educational use. Crop parameter values and stress thresholds are derived from publicly available FAO and ICAR literature. Regional soil data is sourced from published university theses.
