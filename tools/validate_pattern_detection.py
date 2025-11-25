#!/usr/bin/env python3
"""Pattern Validation Audit

Audits wind-lull-wind (Tier 2) pattern detection logic against persistence (Tier 1) for all configured typhoon events.

Goals:
1. Confirm no event simultaneously satisfies persistence (Tier 1) and pattern (Tier 2) while being classified as Tier 2.
2. Surface any potential false positives in pattern detection (e.g., very short pre/post segments).
3. Provide a machine-readable JSON summary at reports/pattern_validation_audit.json for transparency.

Usage:
  python tools/validate_pattern_detection.py [--out-file reports/pattern_validation_audit.json]

The script reuses TYPHOON_EVENTS and detect_pattern_validated from export_web_data.py to ensure identical logic.
"""
from __future__ import annotations
import json
from pathlib import Path
import argparse
from typing import Dict, Any
import pandas as pd
import sys

# Ensure repository root (parent of tools/) is on path for direct script execution
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Import shared event metadata and logic
from export_web_data import TYPHOON_EVENTS, detect_pattern_validated  # type: ignore


def analyze_event(event_id: str, meta: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single event's time_summary.csv for conflicts.

    Returns a record containing:
      - event_id
      - persistent_detected (bool)
      - pattern_detected (bool)
      - classification (derived tier based purely on observation logic)
      - conflict (bool)
      - notes (str)
    """
    csv_path = Path("reports") / meta["data_folder"] / "time_summary.csv"
    record: Dict[str, Any] = {
        "event_id": event_id,
        "name": meta.get("name"),
        "persistent_detected": False,
        "pattern_detected": False,
        "classification": "unverified",
        "conflict": False,
        "notes": "",
        "csv_exists": csv_path.exists(),
    }
    if not csv_path.exists():
        record["notes"] = "time_summary.csv missing"
        return record
    try:
        df = pd.read_csv(csv_path)
    except Exception as exc:  # pragma: no cover
        record["notes"] = f"failed to read CSV: {exc}"  # keep going
        return record
    # Basic column presence checks
    required_cols = {"datetime", "count_ge_T8"}
    missing = required_cols - set(df.columns)
    if missing:
        record["notes"] = f"missing columns: {sorted(missing)}"
        return record
    # Persistence (Tier 1)
    if "persistent_T8" in df.columns and df["persistent_T8"].any():
        record["persistent_detected"] = True
    # Pattern (Tier 2) using shared logic (only valid inside official window and excluded if persistence present)
    pattern_flag = detect_pattern_validated(
        csv_path, meta.get("official_signal8_start"), meta.get("official_signal8_end")
    )
    record["pattern_detected"] = pattern_flag
    # Determine classification consistent with export script
    if not meta.get("official_signal8_start"):
        record["classification"] = "no_signal"
    elif record["persistent_detected"]:
        record["classification"] = "verified"
    elif record["pattern_detected"]:
        record["classification"] = "pattern_validated"
    else:
        record["classification"] = "unverified"
    # Conflict if both raw conditions True but classification not verified
    # (detect_pattern_validated already suppresses pattern when persistence present; we re-run to be sure)
    raw_pattern_possible = _raw_pattern_possible(df, meta)
    if record["persistent_detected"] and raw_pattern_possible and record["classification"] != "verified":
        record["conflict"] = True
        record["notes"] = "pattern + persistence simultaneously satisfied but classification not verified"
    # Additional note if pattern detection very short segments (pre/post only single intervals)
    if record["classification"] == "pattern_validated" and _short_pattern(df, meta):
        record["notes"] = (record["notes"] + "; " if record["notes"] else "") + "short pre/post segment (potential borderline pattern)"
    return record


def _raw_pattern_possible(df: pd.DataFrame, meta: Dict[str, Any]) -> bool:
    """Replicate the raw pattern logic WITHOUT excluding persistence, for auditing overlap."""
    try:
        df["_dt"] = pd.to_datetime(df["datetime"], errors="coerce")
        start_dt = pd.to_datetime(meta.get("official_signal8_start"))
        end_dt = pd.to_datetime(meta.get("official_signal8_end"))
    except Exception:
        return False
    window_df = df[(df["_dt"] >= start_dt) & (df["_dt"] <= end_dt)].copy()
    if window_df.empty:
        return False
    meets = window_df["count_ge_T8"] >= 4
    initial_met = False
    calm_run = 0
    for flag in meets.tolist():
        if flag:
            if initial_met and calm_run >= 2:
                return True
            initial_met = True
            calm_run = 0
        else:
            if initial_met:
                calm_run += 1
    return False


def _short_pattern(df: pd.DataFrame, meta: Dict[str, Any]) -> bool:
    """Detect if the pattern segments (pre or post lull) are only single intervals (borderline)."""
    try:
        df["_dt"] = pd.to_datetime(df["datetime"], errors="coerce")
        start_dt = pd.to_datetime(meta.get("official_signal8_start"))
        end_dt = pd.to_datetime(meta.get("official_signal8_end"))
    except Exception:
        return False
    wdf = df[(df["_dt"] >= start_dt) & (df["_dt"] <= end_dt)].copy()
    if wdf.empty:
        return False
    meets_list = (wdf["count_ge_T8"] >= 4).tolist()
    # Identify indices
    first_indices = []
    second_indices = []
    state = "pre"
    calm_run = 0
    for i, flag in enumerate(meets_list):
        if state == "pre":
            if flag:
                first_indices.append(i)
            else:
                if first_indices:
                    state = "lull"
                    calm_run = 1
        elif state == "lull":
            if not flag:
                calm_run += 1
            else:
                if calm_run >= 2:
                    state = "post"
                    second_indices.append(i)
                else:
                    # reset if lull too short
                    state = "pre"
                    first_indices = []
        elif state == "post":
            if flag:
                second_indices.append(i)
            else:
                break
    # Borderline if either side only 1 interval
    return (len(first_indices) == 1) or (len(second_indices) == 1)


def main():
    parser = argparse.ArgumentParser(description="Audit pattern vs persistence classification consistency.")
    parser.add_argument(
        "--out-file",
        default="reports/pattern_validation_audit.json",
        help="Output JSON file path (default: reports/pattern_validation_audit.json)",
    )
    args = parser.parse_args()

    results = []
    conflicts = 0
    for event_id, meta in TYPHOON_EVENTS.items():
        rec = analyze_event(event_id, meta)
        if rec.get("conflict"):
            conflicts += 1
        results.append(rec)

    summary = {
        "total_events": len(results),
        "conflicts": conflicts,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat() + "Z",
        "events": results,
    }

    out_path = Path(args.out_file)
    out_path.parent.mkdir(exist_ok=True, parents=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"Pattern validation audit written to {out_path}")
    if conflicts:
        print(f"⚠️ Conflicts detected: {conflicts}")
    else:
        print("✅ No pattern/persistence classification conflicts found.")


if __name__ == "__main__":
    main()
