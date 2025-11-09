#!/usr/bin/env python3
"""Generate figures for HKO Signal 8 validation report.

Outputs to reports/figs:
- {event}_timeline.png: area mean wind vs. time, with official Signal 8 shading and persistent_T8 overlay
- {event}_station_heatmap.png: station vs. time heatmap of mean wind (km/h)

Also reuses existing persistence_sensitivity_plot.png for sensitivity section.
"""

from __future__ import annotations

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE = Path(".").resolve()
REPORTS = BASE / "reports"
FIGS = REPORTS / "figs"
FIGS.mkdir(parents=True, exist_ok=True)

EVENTS = {
    "Talim": {
        "input": BASE / "typhoon_data" / "Talim 20230717",
        "time_summary": REPORTS / "talim_validation" / "time_summary.csv",
        "official_start": pd.Timestamp("2023-07-17 00:40:00"),
        "official_end": pd.Timestamp("2023-07-17 16:20:00"),
    },
    "Tapah": {
        "input": BASE / "typhoon_data" / "Tapah 20250907-20250908",
        "time_summary": REPORTS / "tapah_validation" / "time_summary.csv",
        "official_start": pd.Timestamp("2025-09-07 21:20:00"),
        "official_end": pd.Timestamp("2025-09-08 13:10:00"),
    },
    "Yagi": {
        "input": BASE / "typhoon_data" / "Yagi",
        "time_summary": REPORTS / "yagi_validation" / "time_summary.csv",
        # No official Signal 8 period (0%)
        "official_start": None,
        "official_end": None,
    },
    "Toraji": {
        "input": BASE / "typhoon_data" / "Toraji",
        "time_summary": REPORTS / "toraji_validation" / "time_summary.csv",
        "official_start": pd.Timestamp("2024-11-13 23:10:00"),
        "official_end": pd.Timestamp("2024-11-14 10:20:00"),
    },
    "Wipha": {
        "input": BASE / "typhoon_data" / "Wipha 7.19 2230 - 7.21 0010",
        "time_summary": REPORTS / "wipha_validation" / "time_summary.csv",
        "official_start": pd.Timestamp("2025-07-20 00:20:00"),
        "official_end": pd.Timestamp("2025-07-20 19:40:00"),
    },
}

# Reuse standardization from analyze_typhoon (simplified version)


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {
        "Date time": "datetime_raw",
        "Automatic Weather Station": "station",
        "10-Minute Mean Wind Direction(Compass points)": "direction",
        "10-Minute Mean Speed(km/hour)": "mean_kmh",
        "10-Minute Maximum Gust(km/hour)": "gust_kmh",
    }
    for col in list(df.columns):
        if col not in rename_map:
            cl = col.lower()
            if cl.startswith("date"):
                rename_map[col] = "datetime_raw"
            elif cl.startswith("automatic"):
                rename_map[col] = "station"
            elif "mean wind direction" in cl:
                rename_map[col] = "direction"
            elif "mean speed" in cl:
                rename_map[col] = "mean_kmh"
            elif "maximum gust" in cl:
                rename_map[col] = "gust_kmh"
    df = df.rename(columns=rename_map)
    keep = [
        c
        for c in ["datetime_raw", "station", "direction", "mean_kmh", "gust_kmh"]
        if c in df.columns
    ]
    df = df[keep].copy()
    if "datetime_raw" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["datetime_raw"].astype(str), format="%Y%m%d%H%M", errors="coerce"
        )
    else:
        df["datetime"] = pd.NaT
    for c in ("mean_kmh", "gust_kmh"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        else:
            df[c] = np.nan
    if "station" in df.columns:
        df["station"] = df["station"].astype(str).str.strip()
    df = (
        df.dropna(subset=["datetime"])
        .sort_values(["datetime", "station"])
        .reset_index(drop=True)
    )
    return df


def _load_raw(input_dir: Path) -> pd.DataFrame:
    csvs = sorted(input_dir.glob("*latest_10min_wind*.csv"))
    if not csvs:
        csvs = sorted(input_dir.glob("*.csv"))
    frames = []
    for p in csvs:
        try:
            df = pd.read_csv(p, dtype=str)
            df = _standardize_columns(df)
            frames.append(df)
        except Exception:
            pass
    if not frames:
        return pd.DataFrame(columns=["datetime", "station", "mean_kmh", "gust_kmh"])
    return pd.concat(frames, ignore_index=True)


def timeline_plot(
    event: str, df_time: pd.DataFrame, official_start, official_end, out_path: Path
):
    fig, ax = plt.subplots(figsize=(12, 5))
    if not df_time.empty:
        ax.plot(
            df_time["datetime"],
            df_time["area_mean_kmh"],
            color="#1f77b4",
            label="Area mean (km/h)",
        )
        # Overlay persistent_T8 bands
        if "persistent_T8" in df_time.columns:
            y = df_time["persistent_T8"].astype(int) * (
                df_time["area_mean_kmh"].max() * 0.1
            )
            ax.fill_between(
                df_time["datetime"],
                0,
                y,
                step="mid",
                color="#d62728",
                alpha=0.2,
                label="Persistent T8 (p=2)",
            )
        # Also mark count_ge_T8 as secondary line
        if "count_ge_T8" in df_time.columns:
            ax2 = ax.twinx()
            ax2.plot(
                df_time["datetime"],
                df_time["count_ge_T8"],
                color="#ff1493",
                alpha=0.6,
                label="Stations ≥ T8",
            )
            ax2.set_ylabel("Stations ≥63 km/h")
            ax2.set_ylim(bottom=0)
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax2.legend(lines + lines2, labels + labels2, loc="upper left")
    # Shade official Signal 8 if available
    if official_start is not None and official_end is not None:
        ax.axvspan(
            official_start,
            official_end,
            color="gold",
            alpha=0.2,
            label="Official Signal 8",
        )
    ax.set_title(f"{event}: Area mean wind & persistent T8 vs Official Signal 8")
    ax.set_xlabel("Time")
    ax.set_ylabel("Area mean wind (km/h)")
    ax.grid(True, linestyle=":", alpha=0.4)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d %H:%M"))
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


def station_heatmap(event: str, df_raw: pd.DataFrame, out_path: Path):
    if df_raw.empty:
        # create an empty figure to avoid failures
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.text(0.5, 0.5, "No raw data available", ha="center", va="center")
        ax.axis("off")
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        return
    # pivot mean speed by station over time
    pivot = df_raw.pivot_table(
        index="datetime", columns="station", values="mean_kmh", aggfunc="mean"
    )
    # limit to reference stations if desired (kept all for context)
    # sort stations by overall mean for readability
    station_order = pivot.mean(axis=0).sort_values(ascending=False).index
    pivot = pivot[station_order]
    # plot heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    im = ax.imshow(pivot.T, aspect="auto", interpolation="nearest", cmap="viridis")
    ax.set_title(f"{event}: Station mean wind heatmap (km/h)")
    ax.set_yticks(range(len(pivot.columns)))
    ax.set_yticklabels(pivot.columns)
    # x-axis ticks: select a few evenly spaced time labels
    xticks = np.linspace(0, len(pivot.index) - 1, num=min(10, len(pivot.index))).astype(
        int
    )
    ax.set_xticks(xticks)
    ax.set_xticklabels(
        [pivot.index[i].strftime("%m-%d %H:%M") for i in xticks],
        rotation=45,
        ha="right",
    )
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("10-min mean wind (km/h)")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)


if __name__ == "__main__":
    for name, meta in EVENTS.items():
        # Load time_summary for timeline
        try:
            df_time = pd.read_csv(meta["time_summary"], parse_dates=["datetime"])
        except Exception:
            df_time = pd.DataFrame(columns=["datetime", "area_mean_kmh"])
        tl_path = FIGS / f"{name.lower()}_timeline.png"
        timeline_plot(
            name, df_time, meta["official_start"], meta["official_end"], tl_path
        )
        # Load raw and make heatmap
        df_raw = _load_raw(meta["input"])
        hm_path = FIGS / f"{name.lower()}_station_heatmap.png"
        station_heatmap(name, df_raw, hm_path)
    print(f"Figures written to: {FIGS}")
