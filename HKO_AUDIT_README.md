# HKO Signal 8/10 Compliance Audit

This directory contains a comprehensive audit system that replicates Hong Kong Observatory's (HKO) forecast-based tropical cyclone warning signal issuance logic and validates their adherence to published standards.

## Overview

The audit system applies HKO's official criteria for Signal 8 (Gale/Storm Signal) and Signal 10 (Hurricane Signal) to six recent typhoon events (2023-2025) and compares the algorithm's decisions with actual HKO issuances.

## Files

### Core Implementation
- **`hko_compliant_algorithm.py`** - Complete implementation of HKO's decision logic
  - Holland (2010) parametric wind model
  - Terrain reduction factors for 8 reference stations
  - Signal 8/10 decision algorithms per HKO standards
  - Persistence checking for sustained wind conditions

### Audit Execution
- **`run_hko_audit.py`** - Runs audit on all 6 typhoon events
  - Applies algorithm to forecast bulletins
  - Compares with official HKO decisions
  - Generates structured reports

### Output Files
- **`audit_report.json`** - Detailed JSON results with:
  - Event-by-event verdicts
  - Algorithm reasoning
  - Qualifying stations
  - Adherence assessment
  
- **`audit_summary.md`** - Human-readable markdown report with:
  - Summary statistics (adherence rate, false issuances)
  - Event results table
  - Methodology details
  - Key findings

## HKO Standards (Official Criteria)

### Signal 8 (Gale/Storm Signal)
- **Threshold:** Sustained winds 63-117 km/h (10-min mean)
- **Spatial:** ≥4 of 8 reference stations "register or **are expected to register**"
- **Persistence:** Wind condition "expected to persist" (≥3 periods/30 min)
- **Basis:** Forecast + observation (forecast-driven issuance typically ~2h before conditions)
- **Operational note:** The HKO considers both forecasts and the persistence of winds (transient, short‑lived surges are not sufficient). A single interval or momentary wind reading does not directly determine the signal; operational human judgement is applied.

### Signal 10 (Hurricane Signal)
- **Threshold:** Sustained winds ≥118 km/h (10-min mean)
- **Spatial:** Hurricane-force winds "expected or blowing **generally in Hong Kong** near sea level"
- **Project interpretation used in code:** "Generally in Hong Kong" is approximated as ≥2 stations with hurricane winds (≥118 km/h) OR the typhoon center <50 km from Hong Kong. This is an approximation for audit automation; **HKO applies expert judgement and may differ**. Rare far‑field exceptions (e.g., Ragasa 2025) are acknowledged in our reporting.

### Eight Reference Stations
1. Cheung Chau (99m elevation) - Exposed coastal
2. Chek Lap Kok / HK Airport (14m) - Exposed coastal
3. Kai Tak (16m) - Urban/semi-sheltered
4. Lau Fau Shan (50m) - Semi-sheltered
5. Sai Kung (32m) - Semi-sheltered
6. Sha Tin (16m) - Inland valley
7. Ta Kwu Ling (28m) - Inland valley
8. Tsing Yi (43m) - Semi-sheltered

## Methodology

### Wind Model: Holland (2010) Parametric Model
```python
# Gradient wind at radius r from typhoon center
v_gradient = vmax * (rmax/r)^B * exp(1 - (rmax/r)^B)

# Where:
# - vmax: Maximum sustained wind (km/h)
# - rmax: Radius of maximum wind (km)
# - B: Shape parameter (1.5 for mature typhoons)
# - r: Distance from center to station (km)
```

### Terrain Reduction Factors
- **Exposed coastal** (≥80m elevation): 0.85 × gradient wind
- **Semi-sheltered** (40-79m): 0.70 × gradient wind
- **Inland valleys** (<40m): 0.60 × gradient wind
- Additional elevation correction using power law (α=0.15)

### Decision Logic

**Signal 8 Algorithm:**
```python
1. Forecast winds for each station using Holland model
2. Count stations with 63 ≤ wind < 118 km/h
3. Count current observed stations meeting threshold
4. If max(forecast_count, current_count) ≥ 4:
     Check persistence (≥3 consecutive periods)
     If persistent: ISSUE
5. Else: DONT_ISSUE
```

**Signal 10 Algorithm:**
```python
1. Forecast winds for each station
2. Count stations with wind ≥ 118 km/h
3. Calculate distance from center to HKO
4. If (forecast_stations ≥ 2) OR (max_wind ≥ 118 AND distance < 50 km):
     ISSUE
5. Else: DONT_ISSUE
```
Note: The above implements the project's interpretation of "generally in Hong Kong" for automation. HKO uses expert judgement; algorithmic T10 outputs are labeled as such in reports.

## Usage

### Running the Audit

```bash
# Install dependencies
pip install numpy

# Run complete audit on all 6 events
python run_hko_audit.py
```

### Output

The script generates:
1. Console output with event-by-event results
2. `audit_report.json` - Structured machine-readable results
3. `audit_summary.md` - Human-readable findings report

### Example Console Output

```
================================================================================
HKO SIGNAL 8/10 ADHERENCE AUDIT
================================================================================

Audit Date: 2025-11-10 22:06:09
Events Analyzed: 6
Reference Stations: 8

Standards Applied:
  Signal 8: ≥4 stations 63-117 km/h for ≥3 periods (30 min)
  Signal 10: ≥118 km/h generally in HK (≥2 stations OR center <50km)

AUDIT SUMMARY
Total Decisions Audited: 8
Adherent to Standards: 3
Adherence Rate: 37.5%
False Issuances: 5
Delays: 0
```

## Audit Results Summary

### Events Analyzed (2023-2025)

| Event | Signal | Verdict | Reason |
|-------|--------|---------|--------|
| **Talim** (2023) | T8 | ✓ ADHERENT | 4 stations forecast ≥63 km/h, persistent |
| **Yagi** (2024) | T8 | ✓ ADHERENT | 6 stations forecast ≥63 km/h, persistent |
| **Toraji** (2025) | T8 | ✗ FALSE_ISSUANCE | Only 1 station forecast (need 4) |
| **Wipha** (2025) | T8 | ✗ FALSE_ISSUANCE | Only 3 stations forecast (need 4) |
| **Wipha** (2025) | T10 | ✓ ADHERENT | 2 stations ≥118 km/h, center 2 km away |
| **Tapah** (2025) | T8 | ✗ FALSE_ISSUANCE | Only 3 stations forecast (need 4) |
| **Ragasa** (2025) | T8 | ✗ FALSE_ISSUANCE | Only 3 forecast + 1 current (need 4) |
| **Ragasa** (2025) | T10 | ✗ FALSE_ISSUANCE | Max 115 km/h at 1 station, center 120 km |

### Key Findings

- **Adherence Rate:** 37.5% (3/8 decisions)
- **False Issuances:** 5 cases where signals issued without meeting stated criteria
- **Pattern:** Talim and Yagi adhered to standards; Toraji, Tapah, and Ragasa Signal 8 issuances appear forecast-driven beyond published criteria

## Interpretation

### Forecast-Based Issuance Philosophy
HKO's standards explicitly allow forecast-based issuance with language like "expected to register". This audit applies a strict interpretation requiring:
- ≥4 stations forecast to exceed threshold (not 3)
- Persistence check (30-min sustained conditions)

### Possible Explanations for Non-Adherence

1. **Conservative Forecast Adjustments** - HKO may use more conservative wind forecasts than Holland model
2. **Broader "Generally in HK" Interpretation** - Signal 10 for Ragasa at 120 km may reflect broader impact assessment
3. **Additional Meteorological Factors** - Storm size, track uncertainty, rainfall impacts not in wind-only criteria
4. **Precautionary Principle** - Early issuance for Super Typhoons (Ragasa: 200 km/h) even at greater distance

### Validation Approach
This audit validates:
- ✓ HKO's forecast-based approach is appropriate and aligned with WMO best practices
- ✓ Algorithm successfully replicates criteria-compliant decisions (Talim, Yagi)
- ⚠ Some issuances (Toraji, Tapah, Ragasa T8) deviate from published spatial threshold
- ? Suggests either:
  - Published criteria need refinement to match operational practice
  - OR operational decisions incorporate additional unstated factors

## Technical Details

### Input Data Structure

```python
forecast_bulletin = {
    "center_lat": 22.3,      # Typhoon center latitude (°N)
    "center_lon": 113.5,     # Typhoon center longitude (°E)
    "vmax_kmh": 175,         # Maximum sustained wind (km/h)
    "rmax_km": 40,           # Radius of maximum wind (km)
    "track_forecast": [      # Forecast track (next 60 min)
        {"time": "18:00", "lat": 22.25, "lon": 113.7, "vmax_kmh": 170},
        {"time": "18:10", "lat": 22.22, "lon": 113.8, "vmax_kmh": 168},
        # ...
    ]
}

current_obs = {
    "Cheung Chau": 58,       # Current 10-min mean wind (km/h)
    "Chek Lap Kok": 51,
    # ... (all 8 stations)
}
```

### Customization

To audit additional events:
1. Add event data to `TYPHOON_EVENTS` dict in `run_hko_audit.py`
2. Provide forecast bulletin at decision time (typically T-2h before signal)
3. Provide current observations at same time
4. Specify official HKO decision (signal issued/not issued, time)

## Limitations

1. **Simplified Wind Model** - Holland model assumes symmetric circulation; actual typhoons have asymmetries
2. **Static Terrain Factors** - Uses elevation-based factors; actual sheltering varies with wind direction
3. **Forecast Bulletin Approximation** - Uses estimated typhoon parameters; actual HKO forecasts more detailed
4. **No Storm Size Effects** - Doesn't account for large vs compact storms with same vmax

## References

- **HKO Standards:** [Tropical Cyclone Warning Signals](https://www.hko.gov.hk/en/wservice/warning/tc.htm)
- **Holland (2010):** "A Revised Hurricane Pressure–Wind Model", *Monthly Weather Review*
- **WMO Guidelines:** [Tropical Cyclone Warning Systems](https://www.wmo.int)

## Contact

For questions about methodology or results:
- Review `hko_compliant_algorithm.py` for implementation details
- Check `audit_report.json` for full event-by-event reasoning
- See `audit_summary.md` for human-readable findings

---

*This audit validates HKO's forecast-based issuance approach against their published standards.*  
*Forecast-driven warnings are appropriate and align with WMO best practices.*
