# HKO Signal 8 Transparency Portal

**Data-driven validation of Hong Kong Observatory Signal No. 8 timing**

[![Live Portal](https://img.shields.io/badge/Live-Portal-blue)](https://AndyZHENG0715.github.io/GCAP3226/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-green)](https://github.com/AndyZHENG0715/GCAP3226)

## Overview

This project provides independent, transparent validation of Hong Kong Observatory's (HKO) Tropical Cyclone Signal No. 8 issuance timing. We surface observation-based evidence without assuming appropriateness by default. A separate advanced (forecast/model) audit is retained for technical users.

### Dual Validation Tracks
| Track | Purpose | Data Basis | Audience |
|-------|---------|------------|----------|
| Observation (Primary) | Independent verification of official Signal 8 periods | Actual 10‑min mean winds at HKO's 8 reference stations | Public / transparency |
| Forecast Audit (Advanced) | Modeled adherence to published criteria | Parametric (Holland) wind model + terrain factors | Researchers |

The public portal uses ONLY observation data. The advanced audit is published separately for those who wish to examine modeled adherence.

### 3‑Tier Observation Classification
1. **Verified (Tier 1)** – ≥4 of 8 stations ≥63 km/h for ≥3 consecutive 10‑min intervals (≈30 min) inside the official Signal 8 window.
2. **Pattern‑Validated (Tier 2)** – Pattern inside the official window: ≥4 stations → lull (<4 for ≥2 consecutive intervals) → ≥4 stations again. (No “eye” wording – not every lull is an eye passage.)
3. **Unverified (Tier 3)** – Neither persistence nor wind‑lull‑wind pattern detected by observation-only algorithm.
4. **No Signal** – Official Signal 8 not issued.

### 🌐 Live Portal

**Visit the interactive portal:** [https://AndyZHENG0715.github.io/GCAP3226/](https://AndyZHENG0715.github.io/GCAP3226/)

### Key Findings

Current sample (6 typhoons, 2023–2025) – will expand with additional historical & future events:

- ✅ **Verified (Tier 1)**: Talim (sustained ≥30 min T8-level winds)
- ⚠️ **Pattern-Validated (Tier 2)**: (None yet – logic implementation in progress)
- ❓ **Unverified (Tier 3)**: Yagi, Tapah, Toraji, Wipha, Ragasa (no sustained or wind‑lull‑wind pattern)
- 🔬 **Advanced audit retained** (forecast/model) for technical comparison

Other highlights:
- ⏱️ **Early Warning Advantage**: time between official Signal 8 issuance and first sustained (Tier 1) detection; reflects forecast-based preparation window before multi-station gales are concurrently observed.
- 🌍 **Transparency-first**: All source, raw data, and derived JSON published.
- 🏆 **Historic 2025**: Two official Signal 10 warnings (Wipha, Ragasa) – coverage variability documented.

---

## Project Structure

### 🌐 Web Portal (`/docs`)
Interactive website with bilingual support (English/中文):
- **Homepage**: Typhoon timeline and key metrics
- **Event Details**: Station-by-station analysis with charts
- **Methodology**: HKO vs. algorithm comparison and FAQs
- **Data Downloads**: Raw data, JSON API, source code

### 🔬 Analysis Pipeline
Python scripts for validation analysis:
- **`analyze_typhoon.py`**: Main wind analysis script with persistence detection
- **`export_web_data.py`**: Converts validation reports to web-ready JSON
- **`generate_report_figures.py`**: Creates timeline and heatmap visualizations
- **`persistence_sensitivity.py`**: Tests different persistence thresholds
- **`stations_reference_network.txt`**: HKO's 8 reference stations

### 📊 Reference Data
- **8 Reference Stations**: Chek Lap Kok, Lau Fau Shan, Ta Kwu Ling, Sha Tin, Sai Kung, Kai Tak, Tsing Yi, Cheung Chau
- **Data Source**: Hong Kong Observatory public archives (10-minute mean wind speeds)
- **Analysis Period**: 2023-2025 (6 major typhoon events)

---

## Quick Start

### View Results
Visit the **[live portal](https://AndyZHENG0715.github.io/GCAP3226/)** for interactive analysis.

### Run Analysis Locally

1. **Clone repository**
   ```bash
   git clone https://github.com/AndyZHENG0715/GCAP3226.git
   cd GCAP3226
   ```

2. **Install dependencies**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. **Run validation analysis**
   ```bash
   # Analyze specific typhoon with reference network and persistence
   python analyze_typhoon.py --input-folder "typhoon_data/Talim 20230717" \
       --stations-file stations_reference_network.txt \
       --method coverage --min-count 4 --persistence-periods 2 \
       --out-dir reports/talim_validation
   ```

4. **Generate web data**
   ```bash
   python export_web_data.py
   ```

5. **View portal locally**
   ```bash
   cd docs
   python -m http.server 8000
   # Open http://localhost:8000 in browser
   ```

---

## Methodology

### HKO Official Criteria (Forecast-Based)
1. Forecast typhoon track and intensity 12-24 hours ahead
2. Predict wind speeds at 8 reference stations
3. Issue Signal 8 when **≥4 stations expected** to reach gale-force winds (≥63 km/h)
4. Consider persistence: winds must be sustained, not transient squalls
5. Provide early warning advantage for public preparation (issuance before full observation confirmation)

### Our Validation Algorithm (Observation-Only)
1. Observe actual 10-minute mean wind speeds
2. Count stations currently ≥63 km/h (gale force) at the 8 reference stations
3. Require **≥4 stations for ≥3 consecutive periods** (30 minutes) inside the official Signal 8 window (persistence scoring excludes the Signal 10 eye window; transparency retains all data)
4. Retrospectively validate HKO's issuance timing
5. Compare algorithm detection with official signal periods

### Key Difference
Official issuance may incorporate forecast expectations and expert judgment beyond what has materialized at lowland stations. Our classification uses only actual 10‑minute mean readings from the official 8 reference stations. Timing gaps and unverified periods are surfaced for public scrutiny – they are not automatically labelled correct or incorrect.

---

## Example Event

### Talim (2023-07-17)
- **Official Signal 8**: 00:40 – 16:20 (940 minutes)
- **Algorithm Detection**: 06:10 – 16:30 (620 minutes)
- **Timing Delta**: +330 minutes (algorithm detected 5.5h after official)
- **Assessment**: ✅ **Appropriate issuance** — HKO's forecast-based early warning advantage provided crucial public preparation time

### Tapah (2025-09-07 to 09-08)
- **Official Signal 8**: 21:20 – 13:10 (950 minutes)
- **Algorithm Detection**: None (0 minutes)
- **Assessment**: ✅ **Forecast-driven** — Localized/offshore winds; lowland reference stations never reached sustained gale thresholds

### Yagi (2024-09-05 to 09-06)
- **Official Signal 8**: 18:20 Sep 5 – 12:40 Sep 6 (1100 minutes)
- **Algorithm Detection**: None
- **Assessment**: ✅ **Forecast-driven** — Super Typhoon passed offshore; no sustained gales at lowland reference network

### Toraji (2024-11-13 to 11-14)
- **Official Signal 8**: 23:10 – 10:20 (670 minutes)
- **Algorithm Detection**: None
- **Assessment**: ✅ **Forecast-driven** — Late-season weakening system; forecast-based precautionary issuance

### Wipha (2025-07-19 to 07-20)
- **Official Signal 8**: 00:20 – 19:40 (1160 minutes)
- **Official Signal 10**: 09:20 – 16:10 (410 minutes)
- **Algorithm Detection**: None (persistence not satisfied)
- **Transparency**: `t10_analysis.csv` shows sub-threshold 4-of-8 gale coverage and no hurricane-force 4-of-8; no calm segment met eye detection criteria under current thresholds
- **Assessment**: ⚠️ **Observation-only under-representation** — Eye passage and spatial heterogeneity prevented ≥4 concurrent gales; highlights forecast & expert judgement value

### Ragasa (2025-09-23 to 09-24)
- **Official Signal 8**: 14:20 Sep 23 – 20:20 Sep 24 (1800 minutes)
- **Official Signal 10**: 02:40 – 13:20 Sep 24 (640 minutes)
- **Algorithm Detection**: None (no 30‑min 4‑of‑8 gale persistence outside eye window)
- **Transparency**: `t10_analysis.csv` shows intermittent gale counts reaching 4 but hurricane-force coverage never ≥4 concurrently; no calm eye segment confirmed (low-wind criterion not met)
- **Assessment**: ✅ **Forecast-driven** — Record-breaking far‑field Signal 10; emphasizes limitations of lowland-only observation network for eye & maximum wind structure

---

## Interpretation Guidance
Use tiers as transparency markers:

- **Verified** – Observation confirms sustained conditions matching published criterion language (≥4 stations, expected to persist).
- **Pattern-Validated** – Structured re‑emergence pattern even without full 30‑min persistence; merits deeper meteorological review.
- **Unverified** – Observation data alone cannot confirm standard adherence; prompts constructive inquiry.

The project does not assert motive; it surfaces data for public discussion (e.g. safety vs. economic impact of early issuance).

---

## Data Transparency

All project components are publicly available:

- 🌐 **Interactive Portal**: [AndyZHENG0715.github.io/GCAP3226](https://AndyZHENG0715.github.io/GCAP3226/)
- 💻 **Source Code**: [github.com/AndyZHENG0715/GCAP3226](https://github.com/AndyZHENG0715/GCAP3226)
- 📊 **Validation Reports**: [Full technical report](docs/data/HKO_Signal8_Validation_Report.md)
- 📥 **Raw Data**: Wind data from HKO public archives
- 📈 **Analysis Results**: JSON/CSV exports in `/docs/data/`

---

## Technical Details

### Analysis Features (Observation Track)
* **Tier 1 Persistence Detection** – ≥4 stations ≥63 km/h for ≥3 consecutive intervals (≈30 min)
* **Tier 2 Pattern Detection** – ≥4 stations → lull (<4 for ≥2 intervals) → ≥4 stations again (inside official window)
* **Reference Network** – Official HKO 8 stations (Chek Lap Kok, Lau Fau Shan, Ta Kwu Ling, Sha Tin, Sai Kung, Kai Tak, Tsing Yi, Cheung Chau)
* **Thresholds** – T1 (22), T3 (41), T8 (63), T10 (118 km/h)
* **Window Annotation** – `in_T8_window`, `in_T10_window` for transparency (timeline not filtered)
* **Signal 10 Transparency** – `t10_analysis.csv` + optional calm segment diagnostics
* **Sensitivity Analysis** – Persistence parameter benchmarking (1–4 intervals)

### Web Portal Features
- **Bilingual Support**: English and Traditional Chinese (繁體中文)
- **Interactive Charts**: Chart.js timeline comparisons
- **Mobile-Responsive**: Optimized for Hong Kong's mobile-first audience
- **Accessibility**: WCAG compliant, semantic HTML
- **Open Data API**: JSON endpoints for developers

---

## References (Official sources – to be re-fetched for updated wording)

- **Hong Kong Observatory**: Reference for the Issue of No.3 and No.8 Signals  
  [https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm](https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm)

- **HKO Tropical Cyclone Warning System**  
  [https://www.hko.gov.hk/en/education/weather/weather-warnings/00054-the-tropical-cyclone-warning-system-in-hong-kong.html](https://www.hko.gov.hk/en/education/weather/weather-warnings/00054-the-tropical-cyclone-warning-system-in-hong-kong.html)

---

## License

For personal and educational use. No warranty provided.

**Note**: Independent educational research project. Not affiliated with or endorsed by the Hong Kong Observatory.

---

## Contact

Project maintained by: [AndyZHENG0715](https://github.com/AndyZHENG0715)

Feedback and suggestions welcome via GitHub Issues.
