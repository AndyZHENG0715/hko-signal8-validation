#!/usr/bin/env python3
"""
Export typhoon validation data to JSON format for web portal.

This script processes validation reports and generates structured JSON files
that can be consumed by the static web portal for visualization.

Output structure:
- docs/data/events/{typhoon}.json - Individual event details
- docs/data/events/summary.json - All events overview
- docs/data/stations.json - Reference station metadata
- docs/data/sensitivity.json - Persistence sensitivity analysis
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import pandas as pd

# ----------------------------------------------------------------------------------
# NOTE: Observation-only classification tiers (added Phase 2)
#   Tier 1 (verified): ≥4 stations ≥63 km/h for ≥3 consecutive intervals (persistent_T8 True)
#   Tier 2 (pattern_validated): pattern inside official window:
#       ≥4 stations → lull (<4 stations for ≥2 consecutive intervals) → ≥4 stations again
#       (Does not require persistence >=3 intervals; avoids "eye" wording.)
#   Tier 3 (unverified): Neither persistence nor pattern detected.
#   no_signal: Official Signal 8 not issued.
# ----------------------------------------------------------------------------------

# Event metadata
TYPHOON_EVENTS = {
    "talim": {
        "name": "Talim",
        "name_zh": "泰利",
        "year": 2023,
        "date_range": "2023-07-17",
        "official_signal8_start": "2023-07-17 00:40",
        "official_signal8_end": "2023-07-17 16:20",
        "severity": "T8",
        "folder": "Talim 20230717",
        "data_folder": "talim_validation",
    },
    "tapah": {
        "name": "Tapah",
        "name_zh": "塔巴",
        "year": 2025,
        "date_range": "2025-09-07 to 2025-09-08",
        "official_signal8_start": "2025-09-07 21:20",
        "official_signal8_end": "2025-09-08 13:10",
        "severity": "T8",
        "folder": "Tapah 20250907-20250908",
        "data_folder": "tapah_validation",
    },
    "yagi": {
        "name": "Yagi",
        "name_zh": "摩羯",
        "year": 2024,
        "date_range": "2024-09-05 to 2024-09-06",
        "official_signal8_start": "2024-09-05 18:20",
        "official_signal8_end": "2024-09-06 12:40",
        "severity": "T8",
        "folder": "Yagi",
        "data_folder": "yagi_validation",
    },
    "toraji": {
        "name": "Toraji",
        "name_zh": "桃芝",
        "year": 2024,
        "date_range": "2024-11-13 to 2024-11-14",
        "official_signal8_start": "2024-11-13 23:10",
        "official_signal8_end": "2024-11-14 10:20",
        "severity": "T8",
        "folder": "Toraji",
        "data_folder": "toraji_validation",
    },
    "wipha": {
        "name": "Wipha",
        "name_zh": "韋帕",
        "year": 2025,
        "date_range": "2025-07-19 to 2025-07-20",
        "official_signal8_start": "2025-07-20 00:20",
        "official_signal8_end": "2025-07-20 19:40",
        "official_signal10_start": "2025-07-20 09:20",
        "official_signal10_end": "2025-07-20 16:10",
        "severity": "T10",
        "folder": "Wipha 7.19 2230 - 7.21 0010",
        "data_folder": "wipha_validation",
    },
    "ragasa": {
        "name": "Ragasa",
        "name_zh": "樺加沙",
        "year": 2025,
        "date_range": "2025-09-23 to 2025-09-24",
        "official_signal8_start": "2025-09-23 14:20",
        "official_signal8_end": "2025-09-24 20:20",
        "official_signal10_start": "2025-09-24 02:40",
        "official_signal10_end": "2025-09-24 13:20",
        "severity": "T10",
        "folder": "Ragasa",
        "data_folder": "ragasa_validation",
    },
    "chaba": {
        "name": "Chaba",
        "name_zh": "暹芭",
        "year": 2022,
        "date_range": "2022-07-01 to 2022-07-02",
        "official_signal8_start": "2022-07-01 19:10",
        "official_signal8_end": "2022-07-02 16:20",
        "severity": "T8",
        "folder": "Chaba 220701-220702",
        "data_folder": "chaba_validation",
    },
    "ma-on": {
        "name": "Ma-on",
        "name_zh": "馬鞍",
        "year": 2022,
        "date_range": "2022-08-24 to 2022-08-25",
        "official_signal8_start": "2022-08-24 19:25",
        "official_signal8_end": "2022-08-25 09:20",
        "severity": "T8",
        "folder": "Ma-on 220824-220825",
        "data_folder": "ma-on_validation",
    },
    "nalgae": {
        "name": "Nalgae",
        "name_zh": "尼格",
        "year": 2022,
        "date_range": "2022-11-02 to 2022-11-03",
        "official_signal8_start": "2022-11-02 13:40",
        "official_signal8_end": "2022-11-03 05:20",
        "severity": "T8",
        "folder": "Nalgae 221102-221103",
        "data_folder": "nalgae_validation",
    },
    "saola": {
        "name": "Saola",
        "name_zh": "蘇拉",
        "year": 2023,
        "date_range": "2023-09-01 to 2023-09-02",
        "official_signal8_start": "2023-09-01 02:40",
        "official_signal8_end": "2023-09-02 16:20",
        "official_signal10_start": "2023-09-01 20:15",
        "official_signal10_end": "2023-09-02 03:40",
        "severity": "T10",
        "folder": "Saola 230901-230902",
        "data_folder": "saola_validation",
    },
    "koinu": {
        "name": "Koinu",
        "name_zh": "小犬",
        "year": 2023,
        "date_range": "2023-10-08 to 2023-10-09",
        "official_signal8_start": "2023-10-08 12:40",
        "official_signal8_end": "2023-10-09 11:40",
        "severity": "T8",
        "folder": "Koinu",
        "data_folder": "koinu_validation",
    },
}

# Reference stations
REFERENCE_STATIONS = [
    {
        "id": "chek_lap_kok",
        "name": "Chek Lap Kok",
        "name_zh": "赤鱲角",
        "description": "Airport station, coastal exposure",
        "elevation_m": 5,
        "latitude": 22.3089,
        "longitude": 113.9179,
    },
    {
        "id": "lau_fau_shan",
        "name": "Lau Fau Shan",
        "name_zh": "流浮山",
        "description": "Northwestern coastal station",
        "elevation_m": 5,
        "latitude": 22.4692,
        "longitude": 113.9883,
    },
    {
        "id": "ta_kwu_ling",
        "name": "Ta Kwu Ling",
        "name_zh": "打鼓嶺",
        "description": "Northeastern inland station",
        "elevation_m": 35,
        "latitude": 22.5289,
        "longitude": 114.1536,
    },
    {
        "id": "sha_tin",
        "name": "Sha Tin",
        "name_zh": "沙田",
        "description": "Sheltered valley station",
        "elevation_m": 7,
        "latitude": 22.4031,
        "longitude": 114.2103,
    },
    {
        "id": "sai_kung",
        "name": "Sai Kung",
        "name_zh": "西貢",
        "description": "Eastern coastal station",
        "elevation_m": 4,
        "latitude": 22.3814,
        "longitude": 114.2742,
    },
    {
        "id": "kai_tak",
        "name": "Kai Tak",
        "name_zh": "啟德",
        "description": "Urban harbor-side station",
        "elevation_m": 6,
        "latitude": 22.3078,
        "longitude": 114.2194,
    },
    {
        "id": "tsing_yi",
        "name": "Tsing Yi",
        "name_zh": "青衣",
        "description": "Sheltered harbor station",
        "elevation_m": 8,
        "latitude": 22.3508,
        "longitude": 114.1050,
    },
    {
        "id": "cheung_chau",
        "name": "Cheung Chau",
        "name_zh": "長洲",
        "description": "Island station, high exposure",
        "elevation_m": 72,
        "latitude": 22.2019,
        "longitude": 114.0264,
    },
]


def calculate_duration_minutes(start_str: str, end_str: str) -> int:
    """Calculate duration in minutes between two datetime strings."""
    if not start_str or not end_str:
        return 0

    # Handle both formats: with and without seconds
    for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]:
        try:
            start = datetime.strptime(start_str, fmt)
            end = datetime.strptime(end_str, fmt)
            return int((end - start).total_seconds() / 60)
        except ValueError:
            continue

    # If both fail, try parsing the first 16 characters
    start = datetime.strptime(start_str[:16], "%Y-%m-%d %H:%M")
    end = datetime.strptime(end_str[:16], "%Y-%m-%d %H:%M")
    return int((end - start).total_seconds() / 60)


def parse_time_summary(csv_path: Path) -> Dict[str, Any]:
    """Parse time_summary.csv to extract algorithm detection periods.

    Only considers rows where n_stations <= 8 (filtered to reference stations).
    This ensures we use the correctly filtered data, not the unfiltered time_summary.
    """
    if not csv_path.exists():
        return {"detected": False, "start": None, "end": None, "duration_min": 0}

    df = pd.read_csv(csv_path)
    # Filter to only rows with n_stations <= 8 (the 8 reference stations)
    # This ensures we use the correctly filtered data
    df_filtered = df[df["n_stations"] <= 8].copy()
    if df_filtered.empty:
        # Fallback: if no filtered rows, use all data but this indicates a problem
        df_filtered = df.copy()
    persistent = df_filtered[df_filtered["persistent_T8"]]

    if len(persistent) == 0:
        return {"detected": False, "start": None, "end": None, "duration_min": 0}

    start_time = persistent.iloc[0]["datetime"]
    end_time = persistent.iloc[-1]["datetime"]
    duration = len(persistent) * 10  # 10-minute intervals

    return {
        "detected": True,
        "start": start_time,
        "end": end_time,
        "duration_min": duration,
        "peak_stations": int(persistent["count_ge_T8"].max()),
        "mean_wind_peak": float(persistent["area_mean_kmh"].max()),
    }


def detect_pattern_validated(
    csv_path: Path, official_start: str, official_end: str
) -> bool:
    """Detect Tier 2 (pattern_validated) wind-lull-wind pattern.

    Pattern definition (inside official Signal 8 window):
      ≥4 stations (count_ge_T8 >=4) at least once before a lull,
      then a lull segment of ≥2 consecutive intervals with count_ge_T8 <4,
      then ≥4 stations again after the lull.

    Returns True if such a pattern is found when persistent detection (Tier 1) is absent.
    """
    if not csv_path.exists() or not official_start or not official_end:
        return False
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return False
    if "datetime" not in df.columns or "count_ge_T8" not in df.columns:
        return False
    # Filter to only rows with n_stations <= 8 (the 8 reference stations)
    if "n_stations" in df.columns:
        df = df[df["n_stations"] <= 8].copy()
    # Parse datetimes
    try:
        df["_dt"] = pd.to_datetime(df["datetime"], errors="coerce")
        start_dt = pd.to_datetime(official_start)
        end_dt = pd.to_datetime(official_end)
    except Exception:
        return False
    window_df = df[(df["_dt"] >= start_dt) & (df["_dt"] <= end_dt)].copy()
    if window_df.empty:
        return False
    # Quick exclusion: if Tier 1 (persistent_T8) already present, Tier 2 not needed here
    if "persistent_T8" in window_df.columns and window_df["persistent_T8"].any():
        return False
    meets = window_df["count_ge_T8"] >= 4
    # State machine
    initial_met = False
    calm_run = 0
    for meets_flag in meets.tolist():
        if meets_flag:
            # If we have initial met and a calm run of >=2 before, pattern confirmed
            if initial_met and calm_run >= 2:
                return True
            # Otherwise establish initial met (or continue before lull)
            initial_met = True
            calm_run = 0  # reset calm run after second segment detection attempt failed
        else:
            if initial_met:
                calm_run += 1
            # If not initial met yet, lulls before first met don't count
    return False


def parse_station_summary(csv_path: Path) -> List[Dict[str, Any]]:
    """Parse station_summary.csv."""
    if not csv_path.exists():
        return []

    df = pd.read_csv(csv_path)
    stations = []

    for _, row in df.iterrows():
        stations.append(
            {
                "name": row["station"],
                "observations": int(row["n_observations"]),
                "mean_wind_kmh": round(float(row["mean_kmh"]), 1),
                "p90_wind_kmh": round(float(row["p90_kmh"]), 1),
                "max_wind_kmh": round(float(row["max_kmh"]), 1),
                "max_gust_kmh": round(float(row["max_gust_kmh"]), 1),
            }
        )

    return stations


def generate_event_json(event_id: str, event_meta: Dict) -> Dict[str, Any]:
    """Generate comprehensive event JSON."""
    reports_dir = Path("reports")
    data_folder = reports_dir / event_meta["data_folder"]

    # Parse algorithm detection
    time_summary_path = data_folder / "time_summary.csv"
    algo_detection = parse_time_summary(time_summary_path)

    # Parse station data
    station_summary_path = data_folder / "station_summary.csv"
    station_data = parse_station_summary(station_summary_path)

    # Calculate official signal duration
    official_duration = 0
    timing_delta = None
    coverage_percent = 0

    if event_meta["official_signal8_start"]:
        official_duration = calculate_duration_minutes(
            event_meta["official_signal8_start"], event_meta["official_signal8_end"]
        )

        if algo_detection["detected"]:
            start_delta = calculate_duration_minutes(
                event_meta["official_signal8_start"], algo_detection["start"]
            )
            timing_delta = start_delta
            coverage_percent = round(
                (algo_detection["duration_min"] / official_duration) * 100, 1
            )

    # Observation-based verification tier classification
    if not event_meta["official_signal8_start"]:
        verification_tier = "no_signal"
        verdict = "No Signal 8 issued"
        verdict_zh = "未發出 8 號信號"
    else:
        pattern_validated = detect_pattern_validated(
            time_summary_path,
            event_meta["official_signal8_start"],
            event_meta["official_signal8_end"],
        )
        if algo_detection["detected"]:
            verification_tier = "verified"
            if timing_delta and timing_delta > 0:
                verdict = f"Verified: sustained T8-level winds detected after issuance (+{timing_delta} min advance)."
                verdict_zh = f"觀測驗證：持續 8 號級風在發佈後被檢測（提前 {timing_delta} 分鐘）。"
            else:
                verdict = "Verified: sustained T8-level winds met 30‑min requirement."
                verdict_zh = "觀測驗證：持續達到 30 分鐘 8 號級風。"
        elif pattern_validated:
            verification_tier = "pattern_validated"
            verdict = "Pattern‑validated: wind met ≥4 stations, dipped (<4 for ≥2 intervals), then met again – structured wind re‑emergence."
            verdict_zh = "模式驗證：風力達標→下降（<4 連續≥2 個時段）→再次達標，呈現結構性再增長。"
        else:
            verification_tier = "unverified"
            verdict = "Unverified by observation: no sustained (≥30 min) nor wind‑lull‑wind pattern detected during official Signal 8 period."
            verdict_zh = "未經觀測驗證：官方 8 號期間未檢測到持續（≥30 分鐘）或 '達標-下降-再達標' 模式。"

    # Backward-compatible assessment mapping (legacy front-end still consuming 'assessment')
    # Map tiers to existing classes until UI updated fully:
    tier_to_assessment = {
        "verified": "appropriate",
        "pattern_validated": "appropriate",  # will gain its own styling later
        "unverified": "forecast_driven",
        "no_signal": "consistent",
    }
    assessment = tier_to_assessment.get(verification_tier, "forecast_driven")

    event_json = {
        "id": event_id,
        "name": event_meta["name"],
        "name_zh": event_meta["name_zh"],
        "year": event_meta["year"],
        "date_range": event_meta["date_range"],
        "severity": event_meta["severity"],
        "official_signal8": {
            "issued": event_meta["official_signal8_start"] is not None,
            "start": event_meta["official_signal8_start"],
            "end": event_meta["official_signal8_end"],
            "duration_min": official_duration,
        },
        "algorithm_detection": algo_detection,
        "verification_tier": verification_tier,
        "timing_analysis": {
            "start_delta_min": timing_delta,
            "coverage_percent": coverage_percent,
            "assessment": assessment,
            "verdict": verdict,
            "verdict_zh": verdict_zh,
        },
        "station_summary": station_data,
        "validation_report": f"reports/{event_meta['data_folder']}/",
        "figures": {
            "timeline": f"reports/figs/{event_id}_timeline.png",
            "heatmap": f"reports/figs/{event_id}_station_heatmap.png",
        },
    }

    # Optional T10 transparency augmentation (only for events with official Signal 10 and generated CSV)
    t10_path = data_folder / "t10_analysis.csv"
    if t10_path.exists():
        try:
            t10_df = pd.read_csv(t10_path)
            if not t10_df.empty:
                transparency_details = []
                for _, r in t10_df.iterrows():
                    transparency_details.append(
                        {
                            "datetime": str(r.get("datetime")),
                            "count_ge_T8": int(r.get("count_ge_T8", 0)),
                            "count_ge_T10": int(r.get("count_ge_T10", 0)),
                            "low_wind": bool(r.get("t10_low_wind_flag", False)),
                        }
                    )
                event_json["t10_transparency"] = {
                    "intervals": int(t10_df.shape[0]),
                    "gale_coverage_intervals": int(
                        t10_df["t10_meets_t8_coverage"].sum()
                    ),
                    "hurricane_coverage_intervals": int(
                        t10_df["t10_meets_t10_coverage"].sum()
                    ),
                    "low_wind_intervals": int(t10_df["t10_low_wind_flag"].sum()),
                    "first_interval": str(t10_df.iloc[0]["datetime"]),
                    "last_interval": str(t10_df.iloc[-1]["datetime"]),
                    "details": transparency_details,
                }
        except Exception as exc:
            print(f"Warning: failed to parse {t10_path}: {exc}")

    eye_path = data_folder / "eye_passage_analysis.csv"
    if eye_path.exists():
        try:
            eye_df = pd.read_csv(eye_path)
            if not eye_df.empty:
                segments = []
                for _, r in eye_df.iterrows():
                    segments.append(
                        {
                            "segment_start": str(r.get("segment_start")),
                            "segment_end": str(r.get("segment_end")),
                            "n_calm_intervals": int(r.get("n_calm_intervals", 0)),
                            "qualifies_eye_passage": bool(
                                r.get("qualifies_eye_passage", False)
                            ),
                        }
                    )
                event_json["eye_passage_segments"] = segments
        except Exception as exc:
            print(f"Warning: failed to parse {eye_path}: {exc}")

    return event_json


def generate_summary_json(events_data: Dict[str, Dict]) -> Dict[str, Any]:
    """Generate summary of all events."""
    events_list = []

    for event_id, event_data in events_data.items():
        events_list.append(
            {
                "id": event_id,
                "name": event_data["name"],
                "name_zh": event_data["name_zh"],
                "year": event_data["year"],
                "date_range": event_data["date_range"],
                "severity": event_data["severity"],
                "official_issued": event_data["official_signal8"]["issued"],
                "algorithm_detected": event_data["algorithm_detection"]["detected"],
                "verification_tier": event_data.get("verification_tier"),
                "timing_delta_min": event_data["timing_analysis"]["start_delta_min"],
                "assessment": event_data["timing_analysis"]["assessment"],  # legacy
                "verdict": event_data["timing_analysis"]["verdict"],
            }
        )

    # Sort by date (year)
    events_list.sort(key=lambda x: x["year"])

    # Calculate statistics
    total_events = len(events_list)
    signal8_issued = sum(1 for e in events_list if e["official_issued"])
    detected_events = sum(1 for e in events_list if e["algorithm_detected"])

    avg_lead_time = None
    if detected_events > 0:
        deltas = [e["timing_delta_min"] for e in events_list if e["timing_delta_min"]]
        if deltas:
            avg_lead_time = round(sum(deltas) / len(deltas))

    # Tier counts
    tier_counts = {
        "verified": sum(
            1 for e in events_list if e.get("verification_tier") == "verified"
        ),
        "pattern_validated": sum(
            1 for e in events_list if e.get("verification_tier") == "pattern_validated"
        ),
        "unverified": sum(
            1 for e in events_list if e.get("verification_tier") == "unverified"
        ),
        "no_signal": sum(
            1 for e in events_list if e.get("verification_tier") == "no_signal"
        ),
    }

    return {
        "generated_at": datetime.now().isoformat(),
        "statistics": {
            "total_events": total_events,
            "signal8_issued": signal8_issued,
            "algorithm_detected": detected_events,
            "avg_lead_time_min": avg_lead_time,
            "reference_stations": len(REFERENCE_STATIONS),
            "tier_counts": tier_counts,
        },
        "events": events_list,
    }


def parse_sensitivity_analysis() -> Dict[str, Any]:
    """Parse persistence sensitivity analysis data."""
    sensitivity_csv = Path("reports/persistence_sensitivity_analysis.csv")

    if not sensitivity_csv.exists():
        return {}

    df = pd.read_csv(sensitivity_csv)

    sensitivity_data = {}
    for event in df["Event"].unique():
        event_df = df[df["Event"] == event]
        sensitivity_data[event.lower()] = []

        for _, row in event_df.iterrows():
            sensitivity_data[event.lower()].append(
                {
                    "persistence_periods": int(row["PersistencePeriods"]),
                    "start_delay_min": float(row["DeltaStart_vs_Official(min)"])
                    if pd.notna(row["DeltaStart_vs_Official(min)"])
                    else None,
                    "end_lag_min": float(row["DeltaEnd_vs_Official(min)"])
                    if pd.notna(row["DeltaEnd_vs_Official(min)"])
                    else None,
                    "duration_min": int(row["AlgoDuration(min)"])
                    if pd.notna(row["AlgoDuration(min)"])
                    else 0,
                    "detected": row["AlgoDuration(min)"] > 0
                    if pd.notna(row["AlgoDuration(min)"])
                    else False,
                }
            )

    return sensitivity_data


def main():
    """Main export function."""
    print("Exporting typhoon validation data to JSON for web portal...")

    # Create output directories
    docs_dir = Path("docs")
    data_dir = docs_dir / "data"
    events_dir = data_dir / "events"

    for dir_path in [docs_dir, data_dir, events_dir]:
        dir_path.mkdir(exist_ok=True)

    # Generate individual event JSONs
    events_data = {}
    for event_id, event_meta in TYPHOON_EVENTS.items():
        print(f"  Processing {event_meta['name']} ({event_meta['year']})...")
        event_json = generate_event_json(event_id, event_meta)
        events_data[event_id] = event_json

        # Write individual event file
        output_path = events_dir / f"{event_id}.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(event_json, f, indent=2, ensure_ascii=False)
        print(f"    OK {output_path}")

    # Generate summary JSON
    print("  Generating summary...")
    summary_json = generate_summary_json(events_data)
    summary_path = events_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)
    print(f"    OK {summary_path}")

    # Export reference stations
    print("  Exporting reference stations...")
    stations_path = data_dir / "stations.json"
    with open(stations_path, "w", encoding="utf-8") as f:
        json.dump(
            {"total_stations": len(REFERENCE_STATIONS), "stations": REFERENCE_STATIONS},
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"    OK {stations_path}")

    # Export sensitivity analysis
    print("  Parsing sensitivity analysis...")
    sensitivity_data = parse_sensitivity_analysis()
    sensitivity_path = data_dir / "sensitivity.json"
    with open(sensitivity_path, "w", encoding="utf-8") as f:
        json.dump(sensitivity_data, f, indent=2, ensure_ascii=False)
    print(f"    OK {sensitivity_path}")

    print("\nExport complete!")
    print(f"   Generated {len(events_data)} event files")
    print(f"   Data directory: {data_dir}")


if __name__ == "__main__":
    main()
