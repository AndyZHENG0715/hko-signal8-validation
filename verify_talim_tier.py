#!/usr/bin/env python3
"""
Independent verification script for Talim (2023) tier classification.
Analyzes raw CSV data to verify Tier 1 criteria.
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# Constants matching the algorithm
T8_THRESHOLD_KMH = 63
MIN_REFERENCE_STATIONS = 4
MIN_PERSISTENCE_INTERVALS = 3

# The 8 reference stations
REFERENCE_STATIONS = [
    "Cheung Chau",
    "Chek Lap Kok",
    "Kai Tak",
    "Lau Fau Shan",
    "Sai Kung",
    "Sha Tin",
    "Ta Kwu Ling",
    "Tsing Yi",
]

def parse_timestamp(filename: str) -> datetime:
    """Extract timestamp from filename like '20230717-0710-latest_10min_wind.csv'"""
    parts = filename.split('-')
    if len(parts) >= 2:
        date_str = parts[0]  # 20230717
        time_str = parts[1]   # 0710
        if len(date_str) == 8 and len(time_str) == 4:
            return datetime.strptime(f"{date_str}{time_str}", "%Y%m%d%H%M")
    raise ValueError(f"Cannot parse timestamp from filename: {filename}")

def read_csv_interval(csv_path: Path) -> Tuple[datetime, Dict[str, float]]:
    """Read a CSV file and return timestamp and station mean wind speeds."""
    timestamp = parse_timestamp(csv_path.name)
    station_winds = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            station_name = row['Automatic Weather Station']
            if station_name in REFERENCE_STATIONS:
                try:
                    wind_speed = float(row['10-Minute Mean Speed(km/hour)'])
                    station_winds[station_name] = wind_speed
                except (ValueError, KeyError):
                    station_winds[station_name] = None

    return timestamp, station_winds

def count_stations_meeting_threshold(station_winds: Dict[str, float]) -> int:
    """Count how many reference stations have >=63 km/h mean wind."""
    count = 0
    for station, wind in station_winds.items():
        if wind is not None and wind >= T8_THRESHOLD_KMH:
            count += 1
    return count

def analyze_talim_data(data_dir: Path) -> List[Tuple[datetime, int, Dict[str, float]]]:
    """Analyze all CSV files and return list of (timestamp, station_count, station_winds)."""
    results = []

    # Get all CSV files
    csv_files = sorted(data_dir.glob("*-latest_10min_wind.csv"))

    print(f"Found {len(csv_files)} CSV files")

    for csv_file in csv_files:
        try:
            timestamp, station_winds = read_csv_interval(csv_file)
            count = count_stations_meeting_threshold(station_winds)
            results.append((timestamp, count, station_winds))
        except Exception as e:
            print(f"Error processing {csv_file.name}: {e}")

    return sorted(results, key=lambda x: x[0])

def find_persistence_windows(results: List[Tuple[datetime, int, Dict[str, float]]]) -> List[Dict]:
    """Find all windows where ≥4 stations meet threshold for ≥3 consecutive intervals."""
    windows = []
    current_window = None

    for i, (timestamp, count, station_winds) in enumerate(results):
        if count >= MIN_REFERENCE_STATIONS:
            if current_window is None:
                # Start new window
                current_window = {
                    'start': timestamp,
                    'end': timestamp,
                    'intervals': 1,
                    'start_idx': i,
                    'end_idx': i,
                }
            else:
                # Extend current window
                current_window['end'] = timestamp
                current_window['intervals'] += 1
                current_window['end_idx'] = i
        else:
            # Close window if it exists
            if current_window is not None:
                if current_window['intervals'] >= MIN_PERSISTENCE_INTERVALS:
                    windows.append(current_window)
                current_window = None

    # Don't forget the last window
    if current_window is not None and current_window['intervals'] >= MIN_PERSISTENCE_INTERVALS:
        windows.append(current_window)

    return windows

def print_detailed_analysis(results: List[Tuple[datetime, int, Dict[str, float]]], windows: List[Dict]):
    """Print detailed analysis of the data."""
    print("\n" + "="*80)
    print("DETAILED ANALYSIS")
    print("="*80)

    # Find peak periods
    print("\n--- Intervals with >=4 stations meeting threshold ---")
    peak_intervals = [(ts, cnt, winds) for ts, cnt, winds in results if cnt >= MIN_REFERENCE_STATIONS]

    if not peak_intervals:
        print("NONE FOUND")
    else:
        for timestamp, count, station_winds in peak_intervals:
            stations_list = [s for s, w in station_winds.items() if w is not None and w >= T8_THRESHOLD_KMH]
            print(f"\n{timestamp.strftime('%Y-%m-%d %H:%M')}: {count} stations")
            for station in stations_list:
                wind = station_winds[station]
                print(f"  - {station}: {wind:.1f} km/h")

    # Show persistence windows
    print("\n--- Tier 1 Persistence Windows (>=3 consecutive intervals with >=4 stations) ---")
    if not windows:
        print("NONE FOUND")
        print("\nThis means NO Tier 1 classification is possible.")
    else:
        for i, window in enumerate(windows, 1):
            duration_min = (window['end'] - window['start']).total_seconds() / 60
            print(f"\nWindow {i}:")
            print(f"  Start: {window['start'].strftime('%Y-%m-%d %H:%M')}")
            print(f"  End: {window['end'].strftime('%Y-%m-%d %H:%M')}")
            print(f"  Intervals: {window['intervals']} (≈{duration_min:.0f} minutes)")
            print(f"  Indices: {window['start_idx']} to {window['end_idx']}")

            # Show station counts for each interval in this window
            for idx in range(window['start_idx'], window['end_idx'] + 1):
                ts, cnt, winds = results[idx]
                stations_list = [s for s, w in winds.items() if w is not None and w >= T8_THRESHOLD_KMH]
                print(f"    {ts.strftime('%H:%M')}: {cnt} stations - {', '.join(stations_list)}")

def main():
    # Path to Talim data
    data_dir = Path(r"D:\HKOSignal8TransparencyPortal\typhoon_data\Talim 20230717")

    if not data_dir.exists():
        print(f"Error: Data directory not found: {data_dir}")
        return

    print("="*80)
    print("TALIM (2023) TIER CLASSIFICATION VERIFICATION")
    print("="*80)
    print(f"\nData directory: {data_dir}")
    print(f"Threshold: >={T8_THRESHOLD_KMH} km/h mean wind")
    print(f"Tier 1 Criteria: >={MIN_REFERENCE_STATIONS} stations for >={MIN_PERSISTENCE_INTERVALS} consecutive intervals")
    print(f"Reference stations: {', '.join(REFERENCE_STATIONS)}")

    # Analyze data
    results = analyze_talim_data(data_dir)

    if not results:
        print("\nNo data found!")
        return

    print(f"\nAnalyzed {len(results)} intervals")
    print(f"Time range: {results[0][0]} to {results[-1][0]}")

    # Find persistence windows
    windows = find_persistence_windows(results)

    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)

    total_intervals = len(results)
    intervals_meeting_threshold = sum(1 for _, cnt, _ in results if cnt >= MIN_REFERENCE_STATIONS)

    print(f"\nTotal intervals analyzed: {total_intervals}")
    print(f"Intervals with >={MIN_REFERENCE_STATIONS} stations meeting threshold: {intervals_meeting_threshold}")
    print(f"Tier 1 persistence windows found: {len(windows)}")

    if windows:
        print(f"\n[VERIFIED] TIER 1 CLASSIFICATION: VERIFIED")
        print(f"   First window starts at: {windows[0]['start']}")
        print(f"   Longest window: {max(w['intervals'] for w in windows)} intervals")
    else:
        print(f"\n[NOT VERIFIED] TIER 1 CLASSIFICATION: NOT VERIFIED")
        print(f"   No sequence of >={MIN_PERSISTENCE_INTERVALS} consecutive intervals with >={MIN_REFERENCE_STATIONS} stations")

    # Show intervals with at least 1 station meeting threshold
    print("\n" + "="*80)
    print("INTERVALS WITH AT LEAST 1 STATION MEETING THRESHOLD")
    print("="*80)
    intervals_with_wind = [(ts, cnt, winds) for ts, cnt, winds in results if cnt > 0]
    if intervals_with_wind:
        print(f"\nFound {len(intervals_with_wind)} intervals with >=1 station meeting threshold:")
        for timestamp, count, station_winds in intervals_with_wind[:20]:  # Show first 20
            stations_list = [f"{s}: {w:.1f}" for s, w in station_winds.items() if w is not None and w >= T8_THRESHOLD_KMH]
            print(f"  {timestamp.strftime('%Y-%m-%d %H:%M')}: {count} station(s) - {', '.join(stations_list)}")
        if len(intervals_with_wind) > 20:
            print(f"  ... and {len(intervals_with_wind) - 20} more intervals")
    else:
        print("\nNONE FOUND")

    # Detailed analysis
    print_detailed_analysis(results, windows)

    # Compare with algorithm outputs
    print("\n" + "="*80)
    print("COMPARISON WITH ALGORITHM OUTPUTS")
    print("="*80)

    print("\nAlgorithm A (old repo): Tier 1 'verified'")
    print("Algorithm B (new repo): Tier 3 'unverified'")

    if windows:
        print("\n[RESULT] Algorithm A is CORRECT")
        print("   Raw data confirms Tier 1 classification.")
    else:
        print("\n[RESULT] Algorithm B is CORRECT")
        print("   Raw data confirms Tier 3 classification (no Tier 1 persistence found).")

if __name__ == "__main__":
    main()
