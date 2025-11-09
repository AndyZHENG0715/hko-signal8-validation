# Typhoon Wind Analysis (Hong Kong)

This repository contains a simple, configurable script to parse 10‑minute wind speed snapshots from multiple automatic weather stations and estimate an approximate Hong Kong Tropical Cyclone Signal level over time.

Important: This is for analysis and comparison only. Hong Kong Observatory (HKO) issues official signals based on a broader set of criteria including spatial representativeness, cyclone movement, and operational discretion. The thresholds used here are approximations and configurable.

## Input data

CSV snapshots under `Typhoon 7.19 2230 - 7.21 0010/` with schema like:

```
Date time,Automatic Weather Station,10-Minute Mean Wind Direction(Compass points),10-Minute Mean Speed(km/hour),10-Minute Maximum Gust(km/hour)
202507192230,Central Pier,West,12,18
```

## What the script does

- Loads all `*latest_10min_wind.csv` files in the input folder
- Normalizes station names and parses timestamps
- Aggregates per timestamp: area mean/median/P90 and coverage above thresholds
- Estimates a recommended signal using one of three methods: coverage (default), percentile, or mean
- Produces:
  - `reports/time_summary.csv` — per timestamp metrics and the recommended signal
  - `reports/station_summary.csv` — per station metrics (n, mean, P90, max, max gust)
  - `reports/area_speed_and_signal.png` — optional plot if `--plot` is used
  - Console summary: latest snapshot and the peak (highest) recommended signal over the period

## Thresholds and methods

Default minimum sustained wind speed thresholds (10‑minute mean, km/h):

- T1 ≥ 22
- T3 ≥ 41
- T7 ≥ 50 (included per request)
- T8 ≥ 63
- T10 ≥ 118

Recommended signal is the highest level whose condition is satisfied under the chosen method:

- coverage (default): at least `--coverage` fraction of stations at/above threshold
- percentile: the `--percentile` station-speed percentile is at/above threshold
- mean: area mean at/above threshold

These are simplifications. You can edit `DEFAULT_THRESHOLDS_KMH` in `analyze_typhoon.py` to change them.

## Quick start (Windows PowerShell)

1. (Optional) Create and activate a virtual environment

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
```

2. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

3. Run the analysis

```powershell
python analyze_typhoon.py --input-folder "Typhoon 7.19 2230 - 7.21 0010" --out-dir reports --plot
```

Alternative decision methods:

```powershell
# Percentile (e.g., median-based decision)
python analyze_typhoon.py --method percentile --percentile 0.5 --plot

# Mean-based decision
python analyze_typhoon.py --method mean --plot

# Coverage tightened to 60%
python analyze_typhoon.py --coverage 0.6 --plot
```

Filter to a subset of stations (name contains the substring):

```powershell
python analyze_typhoon.py --station-filter "Island"
```

Use an explicit list of stations (one per line):

```
# stations.txt
Chek Lap Kok
Cheung Chau
Green Island
Kai Tak
Lau Fau Shan
North Point
Sha Chau
Peng Chau
```

```powershell
python analyze_typhoon.py --stations-file stations.txt --method coverage --coverage 0.5
```

Outputs go to the `reports/` folder.

## Notes

- Timestamps are parsed as local time without timezone information.
- Rows with `N/A` or blank speeds are ignored.
- If fewer than `--min-stations` valid readings exist for a timestamp, the script reports `Below T1` for that time by default.

## HKO criteria (for reference)

According to the Hong Kong Observatory:

- Since 2007, HKO considers a network of eight near‑sea‑level reference anemometers when issuing No. 3 and No. 8 signals.
- The No. 3 (41–62 km/h) or No. 8 (63–117 km/h) signal will be issued when half or more of these reference anemometers register or are expected to register the respective sustained winds, and the condition is expected to persist.
- Transient squalls from rainbands (even if ≥4 anemometers momentarily exceed thresholds) generally do not trigger issuance if not expected to persist.

Sources:
- HKO: Reference for the Issue of No.3 and No.8 Signals — https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm (Last Revision: 25 Mar 2024)
- HKO: The Tropical Cyclone Warning System in Hong Kong — https://www.hko.gov.hk/en/education/weather/weather-warnings/00054-the-tropical-cyclone-warning-system-in-hong-kong.html

How to approximate in this script:
- Use coverage method at 50% over the eight reference stations: `--method coverage --coverage 0.5 --stations-file stations.txt`
- Or specify a count rule (≥4 out of 8) with `--min-count 4` in place of `--coverage`.

## License

For personal/educational use. No warranty.
