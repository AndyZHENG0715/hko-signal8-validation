# HKO Signal 8 Transparency Portal

**Data-driven validation of Hong Kong Observatory Signal No. 8 timing**

[![Live Portal](https://img.shields.io/badge/Live-Portal-blue)](https://AndyZHENG0715.github.io/GCAP3226/)
[![GitHub](https://img.shields.io/badge/GitHub-Repository-green)](https://github.com/AndyZHENG0715/GCAP3226)

## Overview

This project provides independent, transparent validation of Hong Kong Observatory's (HKO) tropical cyclone Signal No. 8 issuance timing. By comparing official signal periods with observation-based detection algorithms, we demonstrate the value of forecast-based early warning systems and validate that HKO follows published standards appropriately.

### 🌐 Live Portal

**Visit the interactive portal:** [https://AndyZHENG0715.github.io/GCAP3226/](https://AndyZHENG0715.github.io/GCAP3226/)

### Key Findings

- ✅ **HKO issues signals appropriately** according to published standards
- ⏱️ **Forecast-based lead time** (average 330 minutes) provides crucial public safety warning
- 📊 **6 typhoons analyzed** (2023-2025): Talim, Yagi, Toraji, Tapah, Wipha, Ragasa
- 🎯 **Observation-only algorithm** demonstrates the value of forecast-inclusive methodology
- 🌍 **Full transparency**: All data, code, and methodology publicly available
- 🏆 **Historic 2025**: First year since 1964 with two Signal 10 warnings (Wipha, Ragasa)

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
5. Provide lead time for public preparation

### Our Validation Algorithm (Observation-Only)
1. Observe actual 10-minute mean wind speeds
2. Count stations currently ≥63 km/h
3. Require **≥4 stations for ≥2 consecutive periods** (20 minutes)
4. Retrospectively validate HKO's issuance timing
5. Compare algorithm detection with official signal periods

### Key Difference
**HKO uses forecast** (expected conditions) while **algorithm uses observations** (actual measurements). This creates an intentional timing gap representing forecast-based early warning value.

---

## Key Findings

### Talim (2023-07-17)
- **Official Signal 8**: 00:40 – 16:20 (940 minutes)
- **Algorithm Detection**: 06:10 – 16:30 (620 minutes)
- **Timing Delta**: +330 minutes (algorithm detected 5.5h after official)
- **Assessment**: ✅ **Appropriate issuance** — HKO's forecast-based lead time provided crucial early warning

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
- **Algorithm Detection**: None (structural limitation)
- **Assessment**: ⚠️ **Algorithm failure** — Eye passage disrupted persistence detection; multiple stations exceeded thresholds individually

### Ragasa (2025-09-23 to 09-24)
- **Official Signal 8**: 14:20 Sep 23 – 20:20 Sep 24 (1800 minutes)
- **Official Signal 10**: 02:40 – 13:20 Sep 24 (640 minutes)
- **Algorithm Detection**: None
- **Assessment**: ✅ **Forecast-driven** — Record-breaking Signal 10 at 120 km distance (furthest on record); second-longest T10 duration (10h 40m)

---

## Conclusion

**HKO issues Typhoon Signal No. 8 appropriately according to published standards.** Timing differences between official issuance and observation-only algorithm detection reflect:

1. **Forecast-based lead time** (intentional early warning for public safety)
2. **Spatial coverage beyond lowland stations** (high-ground/offshore considerations)
3. **Meteorological judgment** (track, intensity, expected persistence)

The observation-only algorithm demonstrates the **value of HKO's forecast-inclusive methodology** rather than evidence of premature issuance.

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

### Analysis Features
- **Persistence Detection**: Filters transient spikes vs. sustained winds
- **Reference Network**: HKO's 8 official stations (Chek Lap Kok, Lau Fau Shan, Ta Kwu Ling, Sha Tin, Sai Kung, Kai Tak, Tsing Yi, Cheung Chau)
- **Configurable Thresholds**: T1 (22), T3 (41), T8 (63), T10 (118 km/h)
- **Multiple Aggregation Methods**: Coverage, percentile, mean
- **Sensitivity Analysis**: Tests 1-4 consecutive period requirements

### Web Portal Features
- **Bilingual Support**: English and Traditional Chinese (繁體中文)
- **Interactive Charts**: Chart.js timeline comparisons
- **Mobile-Responsive**: Optimized for Hong Kong's mobile-first audience
- **Accessibility**: WCAG compliant, semantic HTML
- **Open Data API**: JSON endpoints for developers

---

## References

- **Hong Kong Observatory**: Reference for the Issue of No.3 and No.8 Signals  
  [https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm](https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm)

- **HKO Tropical Cyclone Warning System**  
  [https://www.hko.gov.hk/en/education/weather/weather-warnings/00054-the-tropical-cyclone-warning-system-in-hong-kong.html](https://www.hko.gov.hk/en/education/weather/weather-warnings/00054-the-tropical-cyclone-warning-system-in-hong-kong.html)

---

## License

For personal and educational use. No warranty provided.

**Note**: This is an independent educational research project. It is not affiliated with or endorsed by the Hong Kong Observatory.

---

## Contact

Project maintained by: [AndyZHENG0715](https://github.com/AndyZHENG0715)

Feedback and suggestions welcome via GitHub Issues.
