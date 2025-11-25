# Verification Guide: Talim & Ragasa T8 Analysis

**Date**: 2025-11-22  
**Purpose**: Manual cross-check of refactored T8-only analysis against official HKO timing

---

## ✅ Verification Checklist

### 1. Talim 2023-07-17 (Pure T8, No T10)

**Official Signal Times**:
- T8 Start: 2023-07-17 00:40
- T8 End: 2023-07-17 16:20
- Duration: 15h 40m

**Analysis Results** (from `reports/talim_validation/time_summary.csv`):
- **Data filtered**: 3688 rows kept (within T8), 296 excluded (outside T8)
- **First persistent T8**: 2023-07-17 07:10:00
- **Total persistent T8 periods**: 19 (consecutive periods ≥3 with 4+ stations ≥63 km/h)
- **Peak signal**: T8

**Verification Steps**:
1. Open `reports/talim_validation/time_summary.csv`
2. Filter to rows where `persistent_T8 == True`
3. Confirm:
   - ✅ All persistent_T8=True rows fall between 00:40 and 16:20
   - ✅ First occurrence is at 07:10:00
   - ✅ `consecutive_periods_above_T8 >= 3` for all persistent_T8=True rows
   - ✅ `count_ge_T8 >= 4` (4-of-8 stations criterion met)

**Expected Result**: Persistent T8 detected approximately 6.5 hours after signal issuance (HKO forecast-driven early warning advantage demonstrated)

---

### 2. Ragasa 2025-09-23/24 (T8 with T10 Escalation)

**Official Signal Times**:
- **T8 Start**: 2025-09-23 14:20
- **T8 End**: 2025-09-24 20:20
- **T10 Start**: 2025-09-24 02:40 ← **EXCLUDED from analysis**
- **T10 End**: 2025-09-24 13:20 ← **EXCLUDED from analysis**

**T8-Only Windows** (analyzed):
- Segment 1: 2025-09-23 14:20 to 2025-09-24 02:40 (12h 20m)
- Segment 2: 2025-09-24 13:20 to 2025-09-24 20:20 (7h 0m)

**Analysis Results** (from `reports/ragasa_validation/time_summary.csv`):
- **Data filtered**: 991 rows kept (T8-only), 533 T10 rows excluded, 8 outside T8 excluded
- **Persistent T8 periods**: 0 (max consecutive: 1 period, below threshold of 3)
- **Peak signal**: T8 (instantaneous at 02:00, just before T10 escalation)

**Verification Steps**:
1. Open `reports/ragasa_validation/time_summary.csv`
2. Confirm **NO** rows exist between 2025-09-24 02:40 and 13:20 (T10 period excluded)
3. Check for `persistent_T8 == True`:
   - Expected: **NONE** (no sustained 30-min gale periods in T8-only windows)
4. Verify `recommended_signal == 'T8'` row at 2025-09-24 02:00:
   - ✅ Just 1 snapshot (not sustained ≥3 periods)
   - ✅ Within T8 window (before 02:40 T10 start)

**Expected Result**: No persistent T8 detected in T8-only intervals (winds escalated to T10 levels before meeting 30-min T8 persistence criterion). This aligns with HKO's forecast-based early warning approach.

---

## 🎯 Success Criteria

### Both Events PASS if:
1. ✅ **Talim**: Persistent T8 periods found within official T8 window (00:40-16:20), starting ~07:10
2. ✅ **Ragasa**: NO persistent_T8=True rows during T10 interval (02:40-13:20), max 1 consecutive period elsewhere
3. ✅ All time_summary.csv rows have timestamps within official T8 windows only
4. ✅ Station counts (`count_ge_T8`) meet 4-of-8 criterion where signal recommended

### If Verification Fails:
- Check for off-by-one errors in time filtering bounds
- Verify CSV datetime parsing (timezone-naive HKT assumed)
- Inspect `consecutive_periods_above_T8` calculation logic
- Review station filtering (should be 8 reference stations only)

---

## 📊 Quick SQL-like Queries (for manual CSV inspection)

**Talim - Find all persistent T8 periods**:
```
Filter: persistent_T8 == True
Sort by: datetime
Expected count: 19 rows
```

**Ragasa - Verify T10 exclusion**:
```
Filter: datetime >= "2025-09-24 02:40" AND datetime <= "2025-09-24 13:20"
Expected count: 0 rows (should be empty!)
```

**Ragasa - Check T8 peak**:
```
Filter: recommended_signal == "T8"
Expected: 1 row at 2025-09-24 02:00, consecutive_periods_above_T8 = 1
```

---

## 🔍 After Verification

If both events PASS:
1. Mark Task 6 complete in `REFACTORING_PLAN.md`
2. Proceed to Phase 5: Documentation updates
3. Re-run `export_web_data.py` to update web portal JSON

If either FAILS:
1. Document specific issue in `REFACTORING_PLAN.md` → "Verification Log"
2. Diagnose root cause (time filtering, persistence logic, station filtering)
3. Fix and regenerate reports
4. Re-verify before updating documentation
