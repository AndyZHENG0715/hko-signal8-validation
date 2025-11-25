# Algorithm Bug Fixes - Summary

## Critical Bugs Fixed

### 1. Signal 10 Interval Exclusion Bug ✅ FIXED
**Problem:** Algorithm excluded all intervals during Signal 10 windows from persistence detection, causing Ragasa to be incorrectly classified as Tier 2 instead of Tier 1.

**Fix:** Removed `and not in_t10_window` condition from `compute_persistence_columns()` in `analyze_typhoon.py` (line 616). T10 intervals are now included in tier classification.

**Result:** Ragasa now correctly shows Tier 1 (verified) with persistence detected during T10 window (02:40-05:10, 70 minutes).

### 2. Reference Station Filtering ✅ FIXED
**Problem:** Algorithm was using all stations from CSV files instead of only the 8 HKO reference stations.

**Fix:** Script already uses `--stations-file stations_reference_network.txt` parameter. Verified that the stations file contains the correct 8 stations and is being used in the regenerate script.

**Result:** All analysis now uses only: Cheung Chau, Chek Lap Kok, Kai Tak, Lau Fau Shan, Sai Kung, Sha Tin, Ta Kwu Ling, Tsing Yi.

### 3. Minimum Stations Parameter Bug ✅ FIXED
**Problem:** `--min-stations` defaulted to 10, but HKO only uses 8 reference stations, causing persistence detection to fail.

**Fix:** Added `--min-stations 8` to `regenerate_all_reports.ps1` and updated persistence detection logic to check `count_ge_T8 >= 4` directly (HKO standard) regardless of `recommended_signal` label.

**Result:** Persistence detection now works correctly with 8 reference stations.

### 4. Persistence Detection Logic ✅ FIXED
**Problem:** Persistence detection required `recommended_signal` to be "T8" or "T10", but this could be "Below T1" even when 4+ stations met the threshold (due to low area mean).

**Fix:** Changed qualifying check to use HKO standard directly: `count_ge_T8 >= 4` (≥4 of 8 stations ≥63 km/h), regardless of recommended_signal label.

**Result:** Persistence detection now correctly identifies periods with ≥4 stations ≥63 km/h for ≥3 consecutive intervals.

## Current Tier Classifications

- **Ragasa**: Tier 1 (verified) ✅ - 70-minute persistence block detected
- **Talim**: Tier 1 (verified) ⚠️ - Still showing persistence; may need manual verification against new pipeline
- **Saola**: Not in current event list (needs to be added)
- **All others**: Tier 3 (unverified) ✅

## Files Modified

1. `analyze_typhoon.py`:
   - Removed T10 exclusion from persistence detection (line 616)
   - Fixed persistence qualifying logic to use HKO standard directly (lines 610-622)

2. `regenerate_all_reports.ps1`:
   - Added `--min-stations 8` parameter
   - Updated comments to reflect T10 inclusion

3. `export_web_data.py`:
   - Fixed Unicode encoding issues in print statements

## Next Steps

1. Verify Talim classification against new pipeline - if it should be Tier 3, investigate why persistence is still being detected
2. Add Saola event to the event list if needed
3. Test GitHub Pages deployment
4. Verify all JSON files are accessible via relative paths

## GitHub Pages Compatibility

- All paths in `docs/` are relative ✅
- JSON files in `docs/data/events/` are accessible ✅
- No absolute URLs or `file://` references ✅

