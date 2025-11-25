# HKO Signal 8/10 Compliance Audit - Quick Start Guide

## What This Does

This audit system replicates Hong Kong Observatory's (HKO) forecast-based tropical cyclone warning signal issuance logic and validates their adherence to published standards for 6 recent typhoon events (2023-2025).

## Quick Start

### 1. Install Dependencies
```bash
pip install numpy
```

### 2. Run Full Audit
```bash
python run_hko_audit.py
```

This generates:
- **`audit_report.json`** - Detailed machine-readable results
- **`audit_summary.md`** - Human-readable findings report

### 3. View Results
```bash
# View summary in terminal (already shown during run)
# Or open the markdown file
cat audit_summary.md
```

## Key Results (Current Audit)

**Adherence Rate:** 37.5% (3 out of 8 decisions)

| Event | Signal | Adherence | Finding |
|-------|--------|-----------|---------|
| Talim (2023) | T8 | ✓ | Met criteria (4 stations forecast) |
| Yagi (2024) | T8 | ✓ | Met criteria (6 stations forecast) |
| Toraji (2025) | T8 | ✗ | Only 1 station forecast (need 4) |
| Wipha (2025) | T8 | ✗ | Only 3 stations forecast (need 4) |
| Wipha (2025) | T10 | ✓ | Met criteria (2 stations hurricane) |
| Tapah (2025) | T8 | ✗ | Only 3 stations forecast (need 4) |
| Ragasa (2025) | T8 | ✗ | Only 3+1 stations (need 4) |
| Ragasa (2025) | T10 | ✗ | 0 stations hurricane, center 120 km |

## Files Overview

### Core Scripts
- **`hko_compliant_algorithm.py`** - Complete implementation (Holland wind model, terrain factors, decision logic)
- **`run_hko_audit.py`** - Runs audit on all 6 events
- **`example_single_event.py`** - Demonstrates usage for single typhoon analysis

### Documentation
- **`HKO_AUDIT_README.md`** - Complete technical documentation
- **`audit_summary.md`** - Generated audit findings (human-readable)
- **`audit_report.json`** - Generated audit results (machine-readable)

## HKO Standards Applied

### Signal 8 (Gale/Storm)
- **Threshold:** 63-117 km/h sustained winds (10-min mean)
- **Spatial:** ≥4 of 8 reference stations "register or **are expected to register**"
- **Persistence:** Conditions "expected to persist" (≥30 min)

### Signal 10 (Hurricane)
- **Threshold:** ≥118 km/h sustained winds
- **Spatial:** "Generally in Hong Kong" = ≥2 stations OR center <50 km

## Example: Analyze Single Event

```python
from hko_compliant_algorithm import hko_signal8_decision

# Define typhoon parameters
forecast_bulletin = {
    "center_lat": 22.3,
    "center_lon": 113.5,
    "vmax_kmh": 175,
    "rmax_km": 40,
    "track_forecast": [...]
}

current_observations = {
    "Cheung Chau": 58,
    "Chek Lap Kok": 51,
    # ... all 8 stations
}

# Get decision
decision, reason, qualifying_stations = hko_signal8_decision(
    forecast_bulletin,
    current_observations
)

print(f"Decision: {decision}")  # "ISSUE" or "DONT_ISSUE"
print(f"Reason: {reason}")
print(f"Qualifying: {qualifying_stations}")
```

See `example_single_event.py` for complete working example.

## Interpretation

### Why 37.5% Adherence?

**Possible Explanations:**
1. **Conservative Forecasting** - HKO may use more conservative wind forecasts than parametric models
2. **Broader Impact Assessment** - Consider factors beyond wind (storm size, rainfall, track uncertainty)
3. **Precautionary Principle** - Issue earlier for Super Typhoons (e.g., Ragasa: 200 km/h vmax)
4. **Operational Refinements** - Internal criteria may differ from published standards

### Key Insight
- ✓ **Forecast-based approach is appropriate** - Aligned with WMO best practices
- ✓ **Criteria-compliant cases work well** - Talim and Yagi show algorithm correctly replicates standards
- ⚠ **Some operational deviations** - Several 2025 events issued with 3 stations (not 4)
- ? **Suggests criteria update needed** - Published standards may not reflect full operational practice

## Customization

### Add New Events
Edit `TYPHOON_EVENTS` dict in `run_hko_audit.py`:

```python
TYPHOON_EVENTS = {
    "NewEvent": {
        "signal8": {
            "forecast_bulletin": {
                "center_lat": 22.0,
                "center_lon": 113.0,
                "vmax_kmh": 150,
                "rmax_km": 45,
                "track_forecast": [...]
            },
            "current_obs": {...},
            "official": {
                "signal8_issued": True,
                "time": "2025-XX-XXTXX:XX:XX+08:00"
            }
        }
    }
}
```

### Adjust Model Parameters
In `hko_compliant_algorithm.py`:

```python
# Holland B-parameter (line ~115)
B = 1.5  # 1.0-2.5 range; lower = flatter profile

# Terrain factors (line ~132)
factors = {
    "exposed": 0.85,      # Adjust coastal reduction
    "semi-sheltered": 0.70,
    "inland": 0.60
}

# Signal 8 threshold (line ~234)
if max_count >= 4:  # Change to 3 or 5 to test sensitivity
```

## Technical Details

**Wind Model:** Holland (2010) parametric tropical cyclone model  
**Terrain Handling:** Elevation-based reduction factors (0.60-0.85)  
**Persistence Check:** ≥3 consecutive 10-min periods (30 min window)  
**Reference Stations:** 8 official HKO stations (Cheung Chau, Chek Lap Kok, Kai Tak, Lau Fau Shan, Sai Kung, Sha Tin, Ta Kwu Ling, Tsing Yi)

## Ragasa Data Normalization

Raw Ragasa snapshot CSVs ship with Chinese headers and station names. Normalize them before analysis:

```powershell
python tools/normalize_ragasa_to_english.py --input-dir "typhoon_data/Ragasa" --output-dir "typhoon_data/Ragasa_en"
python analyze_typhoon.py --input-folder "typhoon_data/Ragasa_en" --out-dir "reports/ragasa_validation" --stations-file "stations_reference_network.txt" --persistence-periods 3 --method coverage --min-count 4 --signal-times data/signal_times/ragasa.json
```

Unknown unmapped Chinese station names are logged (deduplicated) at `reports\ragsa_unknown_station_names.txt`. Extend mappings by editing `data/station_name_map_ragasa.json` and re-running.

## Limitations

1. **Simplified wind model** - Assumes symmetric circulation
2. **Static terrain factors** - Doesn't account for wind direction effects
3. **Estimated forecasts** - Uses approximated typhoon parameters
4. **Wind-only criteria** - Doesn't include storm size, rainfall, or other impacts

## References

- [HKO Tropical Cyclone Warning Signals](https://www.hko.gov.hk/en/wservice/warning/tc.htm)
- Holland, G.J. (2010): "A Revised Hurricane Pressure–Wind Model", *Monthly Weather Review*
- [WMO Tropical Cyclone Guidelines](https://www.wmo.int)

## Support

For detailed methodology, see **`HKO_AUDIT_README.md`**  
For code details, review **`hko_compliant_algorithm.py`**  
For example usage, run **`example_single_event.py`**

---

**Conclusion:** This audit validates HKO's forecast-based approach while identifying operational practices that may deviate from published spatial criteria (≥4 stations). Findings suggest either criteria refinement or documentation of additional decision factors is warranted.
