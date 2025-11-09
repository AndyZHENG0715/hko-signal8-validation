#!/usr/bin/env python3
"""
Analyze Hong Kong wind station data (10-minute mean) from a folder of CSV snapshots
and estimate an approximate Tropical Cyclone Signal level (T1/3/7/8/10) over time.

Notes and caveats:
- This script uses simple, wind-speed-based heuristics. HKO's official signals also
  consider cyclone movement, spatial representativeness, and operational discretion.
- Thresholds are configurable. Defaults are approximate and intended for comparison only.

Input CSV schema (auto-detected from provided samples):
Date time,Automatic Weather Station,10-Minute Mean Wind Direction(Compass points),
10-Minute Mean Speed(km/hour),10-Minute Maximum Gust(km/hour)

Example row:
202507192230,Central Pier,West,12,18

Outputs (in --out-dir):
- time_summary.csv: Per-timestamp aggregated metrics and recommended signal
- station_summary.csv: Per-station metrics across the entire period
- area_speed_and_signal.png: Optional plot of area mean speed and signal (if --plot)

Usage (PowerShell):
  python analyze_typhoon.py --input-folder "Typhoon 7.19 2230 - 7.21 0010" --out-dir reports --plot

"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import sys
import math

import pandas as pd
import numpy as np

# Try to import matplotlib lazily for optional plotting
try:
    import matplotlib.pyplot as plt  # type: ignore

    _HAS_MPL = True
except Exception:
    _HAS_MPL = False


# ---------------------------
# Configuration and thresholds
# ---------------------------
DEFAULT_THRESHOLDS_KMH: Dict[str, float] = {
    # Approximations based on commonly used ranges; customize as needed
    # T1: fresh breeze and above (approx)
    "T1": 22.0,
    # T3: strong wind 41–62 km/h (minimum 41)
    "T3": 41.0,
    # T7: near gale 50–61 km/h (minimum 50); included per user request
    "T7": 50.0,
    # T8: gale/storm 63–117 km/h (minimum 63)
    "T8": 63.0,
    # T10: hurricane force 118+ km/h (minimum 118)
    "T10": 118.0,
}

AGGREGATION_METHODS = {"coverage", "percentile", "mean"}


@dataclass(frozen=True)
class Options:
    input_folder: Path
    out_dir: Path
    method: str
    coverage: float
    min_count: Optional[int]
    percentile: float
    min_stations: int
    station_filter: Optional[str]
    stations_file: Optional[Path]
    plot: bool
    persistence_periods: (
        int  # consecutive 10-min periods required for persistent T8 classification
    )


# ---------------------------
# I/O helpers
# ---------------------------


def parse_args(argv: Optional[List[str]] = None) -> Options:
    parser = argparse.ArgumentParser(
        description="Analyze wind data and estimate HKTC signal."
    )
    parser.add_argument(
        "--input-folder",
        type=str,
        default=str(Path("Typhoon 7.19 2230 - 7.21 0010")),
        help="Folder containing CSV files (each a snapshot with 10-min means)",
    )
    parser.add_argument(
        "--out-dir",
        type=str,
        default=str(Path("reports")),
        help="Directory to write reports/plots",
    )
    parser.add_argument(
        "--method",
        type=str,
        choices=sorted(AGGREGATION_METHODS),
        default="coverage",
        help="How to decide the overall signal from station speeds",
    )
    parser.add_argument(
        "--coverage",
        type=float,
        default=0.40,
        help="For method=coverage: fraction of stations that must meet/exceed a threshold",
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=None,
        help="For method=coverage: minimum count of stations that must meet/exceed a threshold (overrides --coverage if set)",
    )
    parser.add_argument(
        "--percentile",
        type=float,
        default=0.50,
        help="For method=percentile: percentile of station speeds compared to threshold (0–1)",
    )
    parser.add_argument(
        "--min-stations",
        type=int,
        default=10,
        help="Minimum number of valid station readings required to make a decision",
    )
    parser.add_argument(
        "--station-filter",
        type=str,
        default=None,
        help="Optional substring filter: only include stations whose name contains this",
    )
    parser.add_argument(
        "--stations-file",
        type=str,
        default=None,
        help="Optional text file with one station name per line; only these stations are included (applied after --station-filter if both are set)",
    )
    parser.add_argument(
        "--plot",
        action="store_true",
        help="Produce a PNG plot of area mean speed and recommended signal",
    )
    parser.add_argument(
        "--persistence-periods",
        type=int,
        default=2,
        help=(
            "Consecutive 10-min periods meeting T8-level coverage required to treat T8/T10 as persistent. "
            "Set to 1 for legacy instantaneous behavior."
        ),
    )

    args = parser.parse_args(argv)

    input_folder = Path(args.input_folder)
    out_dir = Path(args.out_dir)
    method = args.method
    coverage = float(args.coverage)
    min_count = int(args.min_count) if args.min_count is not None else None
    percentile = float(args.percentile)
    min_stations = int(args.min_stations)
    station_filter = args.station_filter
    stations_file = Path(args.stations_file) if args.stations_file else None
    plot = bool(args.plot)
    persistence_periods = int(args.persistence_periods)

    if method not in AGGREGATION_METHODS:
        parser.error(
            f"Invalid method {method!r}. Choose from {sorted(AGGREGATION_METHODS)}"
        )

    if method == "coverage" and not (0.0 < coverage <= 1.0):
        parser.error("--coverage must be in (0, 1]")

    if method == "percentile" and not (0.0 <= percentile <= 1.0):
        parser.error("--percentile must be in [0, 1]")

    return Options(
        input_folder=input_folder,
        out_dir=out_dir,
        method=method,
        coverage=coverage,
        min_count=min_count,
        percentile=percentile,
        min_stations=min_stations,
        station_filter=station_filter,
        stations_file=stations_file,
        plot=plot,
        persistence_periods=persistence_periods,
    )


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns to canonical names and coerce types.

    Expected source columns:
      - 'Date time'
      - 'Automatic Weather Station'
      - '10-Minute Mean Wind Direction(Compass points)'
      - '10-Minute Mean Speed(km/hour)'
      - '10-Minute Maximum Gust(km/hour)'
    """
    rename_map = {
        "Date time": "datetime_raw",
        "Automatic Weather Station": "station",
        "10-Minute Mean Wind Direction(Compass points)": "direction",
        "10-Minute Mean Speed(km/hour)": "mean_kmh",
        "10-Minute Maximum Gust(km/hour)": "gust_kmh",
    }
    # Be tolerant of minor header variations by mapping known prefixes
    for col in list(df.columns):
        if col not in rename_map:
            if col.lower().startswith("date"):
                rename_map[col] = "datetime_raw"
            elif col.lower().startswith("automatic"):
                rename_map[col] = "station"
            elif "mean wind direction" in col.lower():
                rename_map[col] = "direction"
            elif "mean speed" in col.lower():
                rename_map[col] = "mean_kmh"
            elif "maximum gust" in col.lower():
                rename_map[col] = "gust_kmh"
    df = df.rename(columns=rename_map)

    # Keep only the columns we care about
    keep = [
        c
        for c in ["datetime_raw", "station", "direction", "mean_kmh", "gust_kmh"]
        if c in df.columns
    ]
    df = df[keep].copy()

    # Coerce types
    # Datetime in format YYYYMMDDHHMM
    if "datetime_raw" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["datetime_raw"].astype(str), format="%Y%m%d%H%M", errors="coerce"
        )
    else:
        df["datetime"] = pd.NaT

    # Numeric speeds in km/h
    for col in ("mean_kmh", "gust_kmh"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        else:
            df[col] = np.nan

    # Station name cleanup
    if "station" in df.columns:
        df["station"] = df["station"].astype(str).str.strip()
    else:
        df["station"] = ""

    # Drop rows with no datetime or station
    df = df.dropna(subset=["datetime"])  # allow missing station if truly absent
    # If station is empty string, set to Unknown
    df.loc[df["station"].isna() | (df["station"].str.len() == 0), "station"] = "Unknown"

    # Sort for determinism
    df = df.sort_values(["datetime", "station"]).reset_index(drop=True)
    return df


def _load_one_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str)
    df = _standardize_columns(df)
    df["source_file"] = path.name
    return df


def load_all_csvs(
    folder: Path,
    station_filter: Optional[str] = None,
    stations_file: Optional[Path] = None,
) -> pd.DataFrame:
    """Load and concatenate all CSV snapshot files in the folder."""
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Input folder not found: {folder}")

    csv_paths = sorted(folder.glob("*latest_10min_wind.csv"))
    if not csv_paths:
        # Fall back to any CSV
        csv_paths = sorted(folder.glob("*.csv"))

    if not csv_paths:
        raise FileNotFoundError(f"No CSV files found in {folder}")

    frames: List[pd.DataFrame] = []
    for p in csv_paths:
        try:
            df = _load_one_csv(p)
            frames.append(df)
        except Exception as exc:
            print(f"Warning: failed to load {p.name}: {exc}", file=sys.stderr)

    if not frames:
        raise RuntimeError("No CSV files could be loaded successfully.")

    all_df = pd.concat(frames, ignore_index=True)

    # Filter to stations if requested
    if station_filter:
        needle = station_filter.lower()
        all_df = all_df[
            all_df["station"].str.lower().str.contains(needle, na=False)
        ].copy()

    if stations_file:
        try:
            lines = [
                ln.strip()
                for ln in stations_file.read_text(encoding="utf-8").splitlines()
            ]
            whitelist = {ln for ln in lines if ln and not ln.startswith("#")}
            if whitelist:
                all_df = all_df[all_df["station"].isin(whitelist)].copy()
        except Exception as exc:
            print(
                f"Warning: failed to read stations file {stations_file}: {exc}",
                file=sys.stderr,
            )

    # Drop rows with missing mean speed
    all_df = all_df.dropna(subset=["mean_kmh"]).reset_index(drop=True)

    return all_df


# ---------------------------
# Aggregation and signal logic
# ---------------------------


def _sorted_threshold_items(
    thresholds_kmh: Dict[str, float],
) -> List[Tuple[str, float]]:
    # Sort by ascending threshold so we can iterate and pick the highest satisfied later
    return sorted(thresholds_kmh.items(), key=lambda kv: kv[1])


def _decide_signal_for_snapshot(
    speeds_kmh: np.ndarray,
    thresholds_kmh: Dict[str, float],
    method: str,
    coverage: float,
    percentile: float,
    min_count: Optional[int] = None,
) -> Optional[str]:
    """Return the highest signal label satisfied under the chosen method, or None if below T1."""
    if speeds_kmh.size == 0:
        return None

    valid = speeds_kmh[~np.isnan(speeds_kmh)]
    if valid.size == 0:
        return None

    # Precompute aggregations used by some methods
    if method == "percentile":
        p_val = float(np.nanpercentile(valid, percentile * 100.0))
    elif method == "mean":
        mean_val = float(np.nanmean(valid))

    chosen: Optional[str] = None
    for label, thr in _sorted_threshold_items(thresholds_kmh):
        passed = False
        if method == "coverage":
            cnt = int(np.sum(valid >= thr))
            if min_count is not None:
                passed = cnt >= min_count
            else:
                frac = float(cnt) / float(valid.size)
                passed = frac >= coverage
        elif method == "percentile":
            passed = p_val >= thr
        elif method == "mean":
            passed = mean_val >= thr
        else:
            raise ValueError(f"Unknown method: {method}")

        if passed:
            chosen = label  # keep going to pick the highest
    return chosen


def summarize_over_time(
    df: pd.DataFrame,
    thresholds_kmh: Dict[str, float],
    method: str,
    coverage: float,
    min_count: Optional[int],
    percentile: float,
    min_stations: int,
) -> pd.DataFrame:
    """Aggregate per timestamp, computing metrics and recommended signal."""
    rows: List[Dict[str, object]] = []
    # Iterate chronologically across snapshots

    for ts, g in df.groupby("datetime", sort=True):
        speeds = g["mean_kmh"].to_numpy(dtype=float)
        valid_mask = ~np.isnan(speeds)
        n_valid = int(valid_mask.sum())
        if n_valid < min_stations:
            rec = None
        else:
            rec = _decide_signal_for_snapshot(
                speeds_kmh=speeds[valid_mask],
                thresholds_kmh=thresholds_kmh,
                method=method,
                coverage=coverage,
                percentile=percentile,
                min_count=min_count,
            )

        area_mean = float(np.nanmean(speeds)) if n_valid > 0 else math.nan
        area_med = float(np.nanmedian(speeds)) if n_valid > 0 else math.nan
        area_p90 = (
            float(np.nanpercentile(speeds[valid_mask], 90.0))
            if n_valid > 0
            else math.nan
        )

        # Coverage per threshold (useful diagnostic regardless of method)
        cov = {
            f"coverage_{lbl}": float(np.sum(speeds >= thr)) / float(n_valid)
            if n_valid > 0
            else math.nan
            for lbl, thr in _sorted_threshold_items(thresholds_kmh)
        }

        row: Dict[str, object] = {
            "datetime": ts,
            "n_stations": n_valid,
            "area_mean_kmh": area_mean,
            "area_median_kmh": area_med,
            "area_p90_kmh": area_p90,
            "recommended_signal": rec if rec is not None else "Below T1",
            **cov,
        }

        # Also record absolute counts above each threshold
        for lbl, thr in _sorted_threshold_items(thresholds_kmh):
            row[f"count_ge_{lbl}"] = int(np.sum(speeds >= thr))
        rows.append(row)

    result = pd.DataFrame(rows).sort_values("datetime").reset_index(drop=True)
    return result


def summarize_by_station(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate per station across the entire period."""
    agg = (
        df.groupby("station")
        .agg(
            n_observations=("mean_kmh", "count"),
            mean_kmh=("mean_kmh", "mean"),
            p90_kmh=(
                "mean_kmh",
                lambda s: np.nanpercentile(s.dropna().to_numpy(), 90.0)
                if s.dropna().size
                else np.nan,
            ),
            max_kmh=("mean_kmh", "max"),
            max_gust_kmh=("gust_kmh", "max"),
        )
        .reset_index()
        .sort_values("mean_kmh", ascending=False)
    )
    return agg


# ---------------------------
# Persistence / sustained gale logic
# ---------------------------
def compute_persistence_columns(
    time_df: pd.DataFrame,
    persistence_periods: int,
    min_count: Optional[int],
    coverage: float,
    min_stations: int,
) -> pd.DataFrame:
    """Add persistence detection columns for T8-level winds.

    Definitions:
      - A *qualifying period* is a 10-min snapshot where:
          (a) instantaneous recommended signal is T8 or T10, AND
          (b) station coverage at/above the T8 threshold satisfies either:
                count >= min_count (if provided), OR
                fraction >= coverage (if min_count is None), AND
          (c) number of valid stations >= min_stations.
      - consecutive_periods_above_T8: running count of consecutive qualifying periods
      - persistent_T8: True when consecutive_periods_above_T8 >= persistence_periods (and qualifying)
      - transient_spike_T8: instantaneous T8/T10 reading but not yet persistent (qualifying but count < required run length)

    Notes:
      - Setting persistence_periods=1 yields legacy instantaneous behavior (persistent_T8 mirrors qualifying snapshot).
      - We intentionally do not alter the original recommended_signal logic; persistence augments it.
    """
    if time_df.empty:
        # Still create columns for downstream consistency
        time_df["consecutive_periods_above_T8"] = []
        time_df["persistent_T8"] = []
        time_df["transient_spike_T8"] = []
        return time_df

    # Work on a copy to avoid side effects
    df = time_df.copy()
    consec: List[int] = []
    persistent_flags: List[bool] = []
    transient_flags: List[bool] = []
    run_len = 0
    for _, row in df.iterrows():
        rec_sig = str(row.get("recommended_signal", ""))
        n_stations = int(row.get("n_stations", 0))
        count_ge_t8 = int(row.get("count_ge_T8", 0))

        # Determine count/fraction condition only if we have enough stations
        has_min_stations = n_stations >= min_stations
        if n_stations > 0:
            frac_ge_t8 = count_ge_t8 / float(n_stations)
        else:
            frac_ge_t8 = 0.0

        if min_count is not None:
            coverage_ok = count_ge_t8 >= min_count
        else:
            coverage_ok = frac_ge_t8 >= coverage

        label_ok = rec_sig in {"T8", "T10"}
        qualifying = has_min_stations and label_ok and coverage_ok

        if qualifying:
            run_len += 1
        else:
            run_len = 0

        consec.append(run_len if qualifying else 0)

        is_persistent = qualifying and run_len >= persistence_periods
        persistent_flags.append(is_persistent)
        is_transient = qualifying and not is_persistent
        transient_flags.append(is_transient)

    df["consecutive_periods_above_T8"] = consec
    df["persistent_T8"] = persistent_flags
    df["transient_spike_T8"] = transient_flags
    return df


# ---------------------------
# Plotting
# ---------------------------


def plot_area_time_series(
    time_df: pd.DataFrame,
    thresholds_kmh: Dict[str, float],
    out_path: Path,
):
    if not _HAS_MPL:
        print("Matplotlib not available; skipping plot.")
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(
        time_df["datetime"],
        time_df["area_mean_kmh"],
        label="Area mean (km/h)",
        color="#1f77b4",
    )

    # Add threshold lines
    colors = {
        "T1": "#9edae5",
        "T3": "#2ca02c",
        "T7": "#ff7f0e",
        "T8": "#d62728",
        "T10": "#9467bd",
    }
    for label, thr in _sorted_threshold_items(thresholds_kmh):
        ax.axhline(thr, linestyle="--", color=colors.get(label, "gray"), alpha=0.5)
        ax.text(
            time_df["datetime"].min(),
            thr + 1,
            f"{label} ({thr:.0f} km/h)",
            color=colors.get(label, "gray"),
            va="bottom",
        )

    # Overlay recommended signal as a step-like numeric indicator by mapping to threshold values
    # Convert label to minimum threshold value; Below T1 -> 0
    label_to_thr = {lbl: thr for lbl, thr in _sorted_threshold_items(thresholds_kmh)}
    y_sig = [
        label_to_thr.get(lbl, 0.0) for lbl in time_df["recommended_signal"].tolist()
    ]
    ax.step(
        time_df["datetime"],
        y_sig,
        label="Recommended signal (as min threshold)",
        where="mid",
        color="#ff1493",
    )

    ax.set_title("Area mean wind speed and recommended signal over time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Wind speed (km/h)")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(loc="upper left")
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


# ---------------------------
# Main
# ---------------------------


def main(argv: Optional[List[str]] = None) -> int:
    opts = parse_args(argv)

    # Ensure output dir exists
    opts.out_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading CSV files from: {opts.input_folder}")
    df = load_all_csvs(
        opts.input_folder,
        station_filter=opts.station_filter,
        stations_file=opts.stations_file,
    )

    # Summaries
    print("Summarizing by time…")
    time_df = summarize_over_time(
        df=df,
        thresholds_kmh=DEFAULT_THRESHOLDS_KMH,
        method=opts.method,
        coverage=opts.coverage,
        min_count=opts.min_count,
        percentile=opts.percentile,
        min_stations=opts.min_stations,
    )
    # Augment with persistence columns (does not alter recommendation logic)
    time_df = compute_persistence_columns(
        time_df,
        persistence_periods=opts.persistence_periods,
        min_count=opts.min_count,
        coverage=opts.coverage,
        min_stations=opts.min_stations,
    )

    print("Summarizing by station…")
    station_df = summarize_by_station(df)

    # Write outputs
    time_csv = opts.out_dir / "time_summary.csv"
    station_csv = opts.out_dir / "station_summary.csv"
    time_df.to_csv(time_csv, index=False)
    station_df.to_csv(station_csv, index=False)
    print(f"Wrote: {time_csv}")
    print(f"Wrote: {station_csv}")

    if opts.plot:
        plot_path = opts.out_dir / "area_speed_and_signal.png"
        plot_area_time_series(time_df, DEFAULT_THRESHOLDS_KMH, plot_path)
        print(f"Wrote: {plot_path}")

    # Print a quick overview: last timestamp recommendation
    if not time_df.empty:
        # Latest snapshot summary
        last_row = time_df.iloc[-1]
        print("\nMost recent snapshot:")
        print(f"  Time: {last_row['datetime']}")
        print(f"  Stations: {int(last_row['n_stations'])}")
        print(f"  Area mean: {last_row['area_mean_kmh']:.1f} km/h")
        # Instantaneous vs persistent classification
        print(f"  Recommended signal (instantaneous): {last_row['recommended_signal']}")
        if opts.persistence_periods <= 1:
            # Legacy behavior: persistence disabled / identical
            print(
                "  Persistent signal recommendation: (persistence disabled; equals instantaneous)"
            )
        else:
            if bool(last_row.get("persistent_T8", False)):
                consec = int(last_row.get("consecutive_periods_above_T8", 0))
                print(
                    f"  Persistent signal recommendation: T8/T10 sustained (consecutive qualifying periods: {consec} ≥ {opts.persistence_periods})"
                )
            elif bool(last_row.get("transient_spike_T8", False)):
                consec = int(last_row.get("consecutive_periods_above_T8", 0))
                print(
                    f"  Persistent signal recommendation: Hold below T8 (transient spike; consecutive qualifying periods: {consec} < {opts.persistence_periods})"
                )
            else:
                consec = int(last_row.get("consecutive_periods_above_T8", 0))
                print(
                    f"  Persistent signal recommendation: Below T8 (consecutive qualifying periods: {consec} < {opts.persistence_periods})"
                )

        # Peak signal over the period
        label_to_thr = {
            lbl: thr for lbl, thr in _sorted_threshold_items(DEFAULT_THRESHOLDS_KMH)
        }
        label_to_val = {**{"Below T1": 0.0}, **label_to_thr}
        vals = time_df["recommended_signal"].map(label_to_val).fillna(0.0)
        idx = int(vals.idxmax())
        peak_row = time_df.loc[idx]
        peak_label = str(peak_row["recommended_signal"])  # type: ignore
        peak_time = peak_row["datetime"]
        n_peak = int((vals == vals.max()).sum())
        print("\nPeak over period:")
        print(f"  Highest recommended signal (instantaneous): {peak_label}")
        print(f"  First reached at: {peak_time}")
        print(f"  Number of 10-min snapshots at this level: {n_peak}")

        # Persistence summary
        if not time_df.empty and opts.persistence_periods > 1:
            max_consec = (
                int(time_df["consecutive_periods_above_T8"].max())
                if "consecutive_periods_above_T8" in time_df.columns
                else 0
            )
            if max_consec >= opts.persistence_periods:
                # Find first timestamp where persistent_T8 true
                persistent_rows = time_df[time_df["persistent_T8"]]
                first_persistent_time = (
                    persistent_rows.iloc[0]["datetime"]
                    if not persistent_rows.empty
                    else None
                )
                total_persistent_periods = int(persistent_rows.shape[0])
                print("\nPersistent T8 summary:")
                print(f"  First persistent T8/T10 reached at: {first_persistent_time}")
                print(
                    f"  Total persistent qualifying periods (T8/T10 sustained): {total_persistent_periods}"
                )
            else:
                print("\nPersistent T8 summary:")
                print(
                    f"  No sustained T8/T10 (max consecutive qualifying periods: {max_consec} < {opts.persistence_periods})"
                )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
