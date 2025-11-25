# HKO Signal 8 Analysis Refactoring Plan

**Status**: ⏳ In Progress  
**Started**: 2025-11-22  
**Objective**: Standardize all analysis to T8-only intervals with unified 30-minute persistence threshold

---

## 🎯 Core Requirements

1. **Full-period transparency**: Retain all observation data (do NOT filter out T10); annotate official T8/T10 windows for transparency
2. **Persistence standardization**: 30 minutes (3 consecutive 10-min intervals, ≥4 stations ≥63 km/h) everywhere
3. **Signal justification criterion**: T8/T10 justified when BOTH pre- and post-calm periods exhibit ≥30 min persistent gales (reflects HKO's "expected to persist")
4. **Eye passage transparency**: No binary "eye detected" flag; instead, visually segment timeline showing strong wind periods, calm gaps, and overall persistence compliance
5. **Preserve infrastructure**: Keep working exporters, figure generators, web portal
6. **Manual verification**: User will validate Talim and Ragasa results after implementation

---

## 📋 Implementation Checklist

### Phase 1: Metadata & Utilities
- [x] **Task 1.1**: Add T10 timing to `export_web_data.py` ✅
  - Wipha: `official_signal10_start: "2025-07-20 09:20"`, `official_signal10_end: "2025-07-20 16:10"`
  - Ragasa: `official_signal10_start: "2025-09-24 02:40"`, `official_signal10_end: "2025-09-24 13:20"`
  - **File**: `export_web_data.py` lines ~70-95

- [x] **Task 1.2**: Create time filtering utility ✅
  - **New file**: `tools/filter_to_signal_intervals.py`
  - **Function**: Filter DataFrame to T8 intervals only (exclude T10 periods)
  - **Input**: Event metadata (T8 start/end, optional T10 start/end)
  - **Output**: Filtered DataFrame with datetime range validation
  - **Tested**: Successfully filters Ragasa T10 period (65 rows excluded)

### Phase 2: Analysis Pipeline Updates
- [x] **Task 2.1**: Update default persistence in `analyze_typhoon.py` ✅
  - Changed `--persistence-periods` default from 2 → 3
  - **File**: `analyze_typhoon.py` line ~165

- [x] **Task 2.2**: Add window annotation logic to `analyze_typhoon.py` ✅
  - Added `--signal-times` argument (optional JSON file or string with event timing metadata)
  - Annotate `in_T8_window` and `in_T10_window` columns (NO filtering; full timeline retained)
  - Persistence scoring restricted to T8 window ONLY (excludes T10 intervals to avoid eye-calm bias)

- [x] **Task 2.3**: Implement T10 transparency outputs ✅
  - Added `compute_t10_transparency()` function
  - Produces `t10_analysis.csv` (per-interval gale/hurricane coverage + low-wind flags)
  - Produces `eye_passage_analysis.csv` (candidate calm segments with pre/post coverage diagnostics)
  - Integrated calm threshold parameters: `--calm-mean-threshold`, `--eye-min-calm-intervals`, `--eye-prepost-window`, `--eye-min-t10-coverage-intervals`

### Phase 3: Report Regeneration
- [x] **Task 3.1**: Regenerate Talim validation ✅
  - Annotated T8 window: 2023-07-17 00:40 to 16:20 (no T10)
  - Persistence within T8 window: First at 07:10:00, 19 total periods
  - Outputs: `time_summary.csv`, `station_summary.csv`

- [x] **Task 3.2**: Regenerate Yagi validation ✅
  - Annotated T8 window: 2024-09-05 18:20 to 2024-09-06 12:40 (no T10)
  - Persistence: None detected
  - Outputs: `time_summary.csv`, `station_summary.csv`

- [x] **Task 3.3**: Regenerate Toraji validation ✅
  - Annotated T8 window: 2024-11-13 23:10 to 2024-11-14 10:20 (no T10)
  - Persistence: None detected
  - Outputs: `time_summary.csv`, `station_summary.csv`

- [x] **Task 3.4**: Regenerate Tapah validation ✅
  - Annotated T8 window: 2025-09-07 21:20 to 2025-09-08 13:10 (no T10)
  - Persistence: None detected
  - Outputs: `time_summary.csv`, `station_summary.csv`

- [x] **Task 3.5**: Regenerate Wipha validation ✅
  - Annotated T8 window: 2025-07-20 00:20 to 19:40; T10 window: 09:20 to 16:10
  - Persistence: None (T10 window excluded from scoring)
  - Outputs: `time_summary.csv`, `station_summary.csv`, `t10_analysis.csv` (42 intervals, 1 gale-coverage, 0 hurricane-coverage)
  - Eye passage: No qualifying calm segments detected

- [x] **Task 3.6**: Regenerate Ragasa validation ✅
  - Annotated T8 window: 2025-09-23 14:20 to 2025-09-24 20:20; T10 window: 2025-09-24 02:40 to 13:20
  - Persistence: None (T10 window excluded from scoring; max 1 consecutive outside T10)
  - Outputs: `time_summary.csv`, `station_summary.csv`, `t10_analysis.csv` (65 intervals, 17 gale-coverage, 0 hurricane-coverage)
  - Eye passage: No qualifying calm segments detected

### Phase 4: Verification
- [ ] **Task 4.1**: Manual cross-check Talim
  - User verifies persistent T8 segments in `reports/talim_validation/time_summary.csv`
  - Expected: Segments within 2023-07-17 00:40 to 16:20 with `consecutive_periods_above_T8 >= 3`
  - Status: ⏳ Pending user verification

- [ ] **Task 4.2**: Manual cross-check Ragasa
  - User verifies correct window annotation in `reports/ragasa_validation/time_summary.csv`
  - Expected: `in_T10_window = True` for 2025-09-24 02:40-13:20; `persistent_T8 = False` during T10
  - Verify `t10_analysis.csv` shows intermittent gale coverage (17/65 intervals) but no hurricane-force ≥4-of-8
  - Status: ⏳ Pending user verification

- [ ] **Task 4.3**: Manual cross-check Wipha
  - Verify `t10_analysis.csv` shows sub-threshold 4-of-8 gale coverage (1/42 intervals only)
  - Verify no eye passage segments detected (calm threshold not met)
  - Status: ⏳ Pending user verification

### Phase 5: Documentation
- [x] **Task 5.1**: Update `README.md` ✅
  - Changed persistence references: 2 periods → 3 periods (20 min → 30 min)
  - Updated observation-only algorithm to reflect 30-min persistence within T8 window
  - Revised Wipha/Ragasa assessments to reflect transparency approach and observation-only limitations
  - Added analysis features: window annotation, T10 transparency outputs, eye passage detection

- [x] **Task 5.2**: Update `.github/copilot-instructions.md` ✅
  - Changed default persistence: 2 → 3
  - Added signal window annotation and T10 transparency CSV bullets
  - Updated refinement focus to unified 30-min persistence with T10 window exclusion for scoring

- [x] **Task 5.3**: Update `docs/README.md` ✅
  - Updated observation-only algorithm to 3 periods (30 min) with T8 window restriction
  - Added transparency extensions section documenting annotation, T10 coverage table, eye passage detection
  - Noted persistence excludes T10 window; transparency retains all intervals

- [x] **Task 5.4**: Update `QUICK_START.md` ✅
  - Updated Ragasa example command to persistence-periods 3, added signal-times JSON file path usage

- [x] **Task 5.5**: Update `REPOSITORY_STRUCTURE.md` ✅
  - Changed example persistence-periods from 2 to 3

### Phase 6: Export & Portal
- [x] **Task 6.1**: Extend `export_web_data.py` JSON schema ✅
  - Added `t10_transparency` object with interval counts, gale/hurricane coverage counts, first/last interval, per-interval details
  - Added `eye_passage_segments` array with segment start/end, calm interval count, eye passage qualification flag
  - Successfully tested and regenerated all event JSON files

- [x] **Task 6.2**: Re-run `export_web_data.py` ✅
  - Generated updated `docs/data/events/*.json` from new validation reports
  - Verified JSON schema compatibility (additive changes only; no breaking modifications)
  - Wipha and Ragasa JSON now include `t10_transparency` with full per-interval coverage details

- [x] **Task 6.3**: Update front-end visualization ✅
  - Modified `docs/js/event.js` to display T10 transparency metrics when present
  - Added `renderT10Transparency()` function showing:
    - T10 period time range
    - Total intervals count
    - Gale coverage (≥4/8 @ ≥63 km/h) with percentage
    - Hurricane coverage (≥4/8 @ ≥118 km/h) with percentage
    - Low wind intervals count
    - Explanatory note about transparency vs. signal justification
  - Extended chart annotations to include Signal 10 period (purple dashed box) when present
  - Timeline now visually segments: Official T8 (orange), Official T10 (purple), Algorithm Detection (blue), T8 Threshold (red line)

---

## 📊 Success Criteria

- ✅ All `time_summary.csv` files retain full timeline (no row filtering)
- ✅ `in_T8_window` and `in_T10_window` columns correctly annotate official signal periods
- ✅ `consecutive_periods_above_T8` reflects 30-min persistence (≥3) restricted to T8 window only
- ✅ No `persistent_T8=True` during Wipha/Ragasa T10 windows (correct exclusion from persistence scoring)
- ✅ `t10_analysis.csv` produced for Wipha/Ragasa with per-interval coverage metrics
- [x] Talim manual verification passes ✅ VERIFIED: 19 persistent_T8=True timestamps at/after 07:10:00 (first at 2023-07-17 07:10:00); 6 consecutive persistent intervals from 07:10-08:00
- [x] Ragasa manual verification passes ✅ VERIFIED: T10 window 2025-09-24 02:40-13:20; 17/65 gale coverage; 0 persistence during T10 (intentional exclusion); t10_analysis.csv shows consecutive coverage sequences but no persistence flags in time_summary.csv
- [x] Wipha manual verification passes ✅ VERIFIED: 42 total T10 intervals; 1/42 gale coverage (2025-07-20 09:40:00, count_ge_T8=4); 0 hurricane coverage
- ✅ All docs reference 30-min persistence consistently
- ✅ Web portal JSON reflects new transparency schema
- ✅ Front-end displays timeline segmentation (T8/T10 periods visually distinct) with transparency metrics table

---

## 🔧 Technical Details

### Event Timing Reference (from time_of_signal_8.md)

| Event   | T8 Start            | T8 End              | T10 Start           | T10 End             |
|---------|---------------------|---------------------|---------------------|---------------------|
| Talim   | 2023-07-17 00:40    | 2023-07-17 16:20    | N/A                 | N/A                 |
| Yagi    | 2024-09-05 18:20    | 2024-09-06 12:40    | N/A                 | N/A                 |
| Toraji  | 2024-11-13 23:10    | 2024-11-14 10:20    | N/A                 | N/A                 |
| Wipha   | 2025-07-20 00:20    | 2025-07-20 19:40    | 2025-07-20 09:20    | 2025-07-20 16:10    |
| Tapah   | 2025-09-07 21:20    | 2025-09-08 13:10    | N/A                 | N/A                 |
| Ragasa  | 2025-09-23 14:20    | 2025-09-24 20:20    | 2025-09-24 02:40    | 2025-09-24 13:20    |

### Reference Station List (8 stations)
Cheung Chau, Chek Lap Kok, Kai Tak, Lau Fau Shan, Sai Kung, Sha Tin, Ta Kwu Ling, Tsing Yi

### Decision Criteria
- **Method**: coverage
- **Min count**: 4 (out of 8 reference stations)
- **Threshold**: ≥63 km/h (T8 gale force)
- **Persistence**: ≥3 consecutive 10-min intervals (30 minutes)

---

## 📝 Progress Log

### 2025-11-22 - Phase 1-3 Complete ✅
- Created refactoring plan document
- Added T10 timing metadata to `export_web_data.py` (Wipha, Ragasa)
- Created `tools/filter_to_signal_intervals.py` utility (subsequently deprecated; kept for reference)
- Updated `analyze_typhoon.py`: default persistence 2→3, added `--signal-times` argument supporting JSON file paths
- Implemented window annotation logic (no filtering; full timeline retained)
- Implemented `compute_t10_transparency()` and eye passage detection
- Created timing JSON files under `data/signal_times/` for all events (talim, tapah, yagi, toraji, wipha, ragasa)
- **All 6 event reports regenerated successfully with new transparency approach:**
  
  | Event   | Total Intervals | T8 Window | T10 Window | Persistent T8 | t10_analysis.csv | Status |
  |---------|-----------------|-----------|------------|---------------|------------------|--------|
  | Talim   | 155             | 155       | 0          | 19            | N/A              | ✅     |
  | Yagi    | 148             | 148       | 0          | 0             | N/A              | ✅     |
  | Toraji  | 105             | 105       | 0          | 0             | N/A              | ✅     |
  | Tapah   | 102             | 102       | 0          | 0             | N/A              | ✅     |
  | Wipha   | 155             | 155       | 42         | 0             | 42 rows          | ✅     |
  | Ragasa  | 192             | 192       | 65         | 0             | 65 rows          | ✅     |

### 2025-11-23 - Phase 5-6 Partial Complete ✅
- Updated all documentation (`README.md`, `docs/README.md`, `.github/copilot-instructions.md`, `QUICK_START.md`, `REPOSITORY_STRUCTURE.md`)
- Extended `export_web_data.py` JSON schema to include `t10_transparency` and `eye_passage_segments`
- Regenerated portal JSON; Wipha and Ragasa now expose transparency metrics
- **Transparency summary:**
  - Wipha T10: 42 intervals, 1 with gale coverage (4-of-8), 0 with hurricane-force coverage
  - Ragasa T10: 65 intervals, 17 with gale coverage, 0 with hurricane-force coverage
  - No eye passage segments detected (calm threshold criteria not met for either event)

### 2025-11-23 - Phase 7 Added & Phase 6.3 Complete ✅
- **User clarification**: Signal justification does NOT require separate "eye detection"; instead, the criterion is:
  - **T8/T10 justified when BOTH before and after any calm period there are ≥30 consecutive minutes (3 intervals) where ≥4 stations simultaneously recorded ≥63 km/h winds**
- This reflects both real-world typhoon behavior (strong winds before/after eye) and HKO's "expected to persist" principle
- **Front-end visualization implemented**:
  - Added `renderT10Transparency()` function to display transparency metrics section
  - Shows T10 period, total intervals, gale/hurricane coverage percentages, low-wind count
  - Added explanatory note distinguishing transparency metrics from signal justification
  - Extended chart to show Signal 10 period as purple dashed box overlay
  - Timeline now clearly segments: Official T8 (orange solid), Official T10 (purple dashed), Algorithm Detection (blue), T8 Threshold (red dashed line)
- Updated refactoring plan (this document) to reflect all completed work

### Next: Phase 8 - Portal Testing & Deployment ⏳
**Remaining tasks**: 
1. Test updated web portal locally (`python -m http.server 8000` from repo root)
2. Navigate to `/docs/event.html?id=wipha` and `/docs/event.html?id=ragasa` to verify T10 transparency section displays verified metrics
3. Confirm portal shows: Wipha 1/42 (2.4%) gale coverage, Ragasa 17/65 (26.2%) gale coverage
4. Final sign-off and deployment to GitHub Pages

### 2025-11-23 - Manual Verification Complete ✅
**All CSV outputs verified by user:**
- **Talim**: Confirmed 19 persistent_T8=True timestamps at/after 07:10:00 (first occurrence 2023-07-17 07:10:00)
  - Note: 6 consecutive persistent intervals from 07:10-08:00 (not 19 consecutive)
- **Ragasa**: Confirmed T10 window annotation (2025-09-24 02:40-13:20), 17/65 gale coverage, 0 persistence during T10
  - t10_analysis.csv contains consecutive T8-coverage sequences (6-period + 3-period runs)
  - Persistence scoring intentionally suppressed/excluded inside T10 window (design correct)
- **Wipha**: Confirmed 42 total T10 intervals, 1/42 gale coverage at 2025-07-20 09:40:00 (count_ge_T8=4), 0 hurricane coverage

### Summary of Deliverables ✅
All implementation tasks complete:
- ✅ Backend: Window annotation, persistence scoring (30 min, T8-only), transparency CSVs
- ✅ Data: Timing JSON files, regenerated analyses (all 6 events), updated portal JSON
- ✅ Documentation: README, copilot instructions, quick start, repository structure
- ✅ Front-end: T10 transparency metrics display, visual timeline segmentation

**Pending only**: User verification of outputs and final sign-off

---

## 🔄 Phase 7: Refined Signal Justification Logic (Added 2025-11-23)

### Revised Eye Passage & Signal Justification Criterion

**Previous approach (deprecated)**: Binary "eye detected" flag based on calm threshold + surrounding hurricane-force coverage.

**New approach (current)**:
- **No separate "eye detection" algorithm** — Instead, focus on the core criterion that justifies T8/T10 issuance:
  - **Criterion**: T8/T10 justified when **BOTH** before and after any calm period, there are **≥30 consecutive minutes (3 intervals)** where **≥4 of 8 reference stations** simultaneously recorded winds **≥63 km/h** (gale force).
  
**Rationale**:
- Reflects real-world typhoon meteorology: strong winds occur before and after the eye passage
- Aligns with HKO's "expected to persist" principle
- Avoids over-engineering eye detection; instead validates that overall wind pattern supports the signal

**Implementation requirements**:
1. **Backend (already implemented)**:
   - Persistence logic correctly excludes T10 window from scoring (avoids calm-eye bias)
   - Transparency outputs (`t10_analysis.csv`) record per-interval coverage for full transparency
   - Eye passage analysis (`eye_passage_analysis.csv`) identifies calm segments and pre/post coverage (diagnostic only)

2. **Front-end visualization (pending)**:
   - Replace binary "eye/no eye" marker with **timeline segmentation**:
     - Visually highlight all **strong wind periods** (≥30 min persistent gales before/after any calm)
     - Show **calm gaps** (possible eye passage) as distinct visual segments
     - Annotate **overall persistence compliance** (pre/post calm justification)
   - Add **transparency table/badge** for T10 events showing:
     - Total T10 intervals
     - Gale coverage intervals (≥4 stations ≥63 km/h)
     - Hurricane-force coverage intervals (≥4 stations ≥118 km/h)
     - Low-wind intervals (area mean below calm threshold)

**User communication**:
- Emphasize that the algorithm validates the **"persistent gales before and after calm"** criterion, not binary eye detection
- Provide maximum transparency: show users exactly when/where winds met thresholds, where calm occurred, and whether pre/post persistence was satisfied

