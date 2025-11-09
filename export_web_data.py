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
        "official_signal8_start": None,
        "official_signal8_end": None,
        "severity": "No Signal 8",
        "folder": "Yagi",
        "data_folder": "yagi_validation",
    },
    "toraji": {
        "name": "Toraji",
        "name_zh": "潭美",
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
        "severity": "T10",
        "folder": "Wipha 7.19 2230 - 7.21 0010",
        "data_folder": "wipha_validation",
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
    """Parse time_summary.csv to extract algorithm detection periods."""
    if not csv_path.exists():
        return {"detected": False, "start": None, "end": None, "duration_min": 0}

    df = pd.read_csv(csv_path)
    persistent = df[df["persistent_T8"]]

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

    # Determine assessment
    if not event_meta["official_signal8_start"]:
        assessment = "consistent"
        verdict = "No Signal 8 issued, no persistent gales detected"
        verdict_zh = "未發出8號信號，未檢測到持續烈風"
    elif not algo_detection["detected"]:
        assessment = "forecast_driven"
        verdict = "Official issuance appropriate (forecast-based early warning)"
        verdict_zh = "官方發佈適當（基於預報的預警）"
    elif timing_delta and timing_delta > 0:
        assessment = "appropriate"
        verdict = f"Appropriate issuance with {timing_delta} min forecast lead time"
        verdict_zh = f"適當發佈，預報提前 {timing_delta} 分鐘"
    else:
        assessment = "appropriate"
        verdict = "Appropriate timing alignment"
        verdict_zh = "時間對齊適當"

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
                "timing_delta_min": event_data["timing_analysis"]["start_delta_min"],
                "assessment": event_data["timing_analysis"]["assessment"],
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

    return {
        "generated_at": datetime.now().isoformat(),
        "statistics": {
            "total_events": total_events,
            "signal8_issued": signal8_issued,
            "algorithm_detected": detected_events,
            "avg_lead_time_min": avg_lead_time,
            "reference_stations": len(REFERENCE_STATIONS),
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
        print(f"    ✓ {output_path}")

    # Generate summary JSON
    print("  Generating summary...")
    summary_json = generate_summary_json(events_data)
    summary_path = events_dir / "summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_json, f, indent=2, ensure_ascii=False)
    print(f"    ✓ {summary_path}")

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
    print(f"    ✓ {stations_path}")

    # Export sensitivity analysis
    print("  Parsing sensitivity analysis...")
    sensitivity_data = parse_sensitivity_analysis()
    sensitivity_path = data_dir / "sensitivity.json"
    with open(sensitivity_path, "w", encoding="utf-8") as f:
        json.dump(sensitivity_data, f, indent=2, ensure_ascii=False)
    print(f"    ✓ {sensitivity_path}")

    print("\n✅ Export complete!")
    print(f"   Generated {len(events_data)} event files")
    print(f"   Data directory: {data_dir}")


if __name__ == "__main__":
    main()
