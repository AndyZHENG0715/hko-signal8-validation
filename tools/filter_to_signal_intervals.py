#!/usr/bin/env python3
"""
Filter typhoon wind data to official Signal 8 intervals only, excluding Signal 10 periods.

This utility ensures analysis focuses on T8 intervals where the "4-of-8 stations, ≥63 km/h,
≥30 minutes" criterion can be algorithmically verified. T10 periods are excluded as they
involve substantial expert judgment regarding rapid intensification and territory-wide impact.

Usage:
    from tools.filter_to_signal_intervals import filter_to_t8_intervals

    timing = {
        "signal8_start": "2025-09-23 14:20",
        "signal8_end": "2025-09-24 20:20",
        "signal10_start": "2025-09-24 02:40",  # Optional
        "signal10_end": "2025-09-24 13:20"     # Optional
    }

    filtered_df = filter_to_t8_intervals(raw_df, timing)
"""

from __future__ import annotations
from typing import Dict
import pandas as pd


def parse_hkt_datetime(dt_str: str) -> pd.Timestamp:
    """Parse HKT datetime string to pandas Timestamp (naive, assumed HKT)."""
    return pd.to_datetime(dt_str, format="%Y-%m-%d %H:%M")


def filter_to_t8_intervals(
    df: pd.DataFrame,
    timing: Dict[str, str],
    datetime_col: str = "datetime",
) -> pd.DataFrame:
    """
    Filter DataFrame to T8-only intervals, excluding any T10 escalation periods.

    Parameters:
    -----------
    df : pd.DataFrame
        Input DataFrame with datetime column
    timing : dict
        Signal timing metadata with keys:
        - 'signal8_start': T8 issuance time (required)
        - 'signal8_end': T8 cancellation time (required)
        - 'signal10_start': T10 issuance time (optional)
        - 'signal10_end': T10 cancellation time (optional)
    datetime_col : str
        Name of datetime column in df (default: 'datetime')

    Returns:
    --------
    pd.DataFrame
        Filtered DataFrame containing only T8 interval rows

    Example:
    --------
    For Ragasa with T10 escalation:
    - T8: 2025-09-23 14:20 to 2025-09-24 20:20
    - T10: 2025-09-24 02:40 to 2025-09-24 13:20

    Result: Returns rows in [14:20 - 02:40) + (13:20 - 20:20]
    """
    if datetime_col not in df.columns:
        raise ValueError(f"DataFrame must have '{datetime_col}' column")

    # Parse signal times
    t8_start = parse_hkt_datetime(timing["signal8_start"])
    t8_end = parse_hkt_datetime(timing["signal8_end"])

    has_t10 = "signal10_start" in timing and "signal10_end" in timing

    if has_t10:
        t10_start = parse_hkt_datetime(timing["signal10_start"])
        t10_end = parse_hkt_datetime(timing["signal10_end"])

        # Validate T10 is within T8 bounds
        if not (t8_start <= t10_start < t10_end <= t8_end):
            raise ValueError(
                f"T10 interval ({t10_start} to {t10_end}) must be within "
                f"T8 interval ({t8_start} to {t8_end})"
            )

    # Ensure datetime column is parsed
    df_filtered = df.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_filtered[datetime_col]):
        df_filtered[datetime_col] = pd.to_datetime(df_filtered[datetime_col])

    # Filter to T8 overall window
    mask_t8 = (df_filtered[datetime_col] >= t8_start) & (
        df_filtered[datetime_col] <= t8_end
    )

    if has_t10:
        # Exclude T10 period: keep rows before T10 start OR after T10 end
        mask_not_t10 = (df_filtered[datetime_col] < t10_start) | (
            df_filtered[datetime_col] > t10_end
        )
        final_mask = mask_t8 & mask_not_t10

        # Log exclusion info
        n_t10_excluded = (
            (df_filtered[datetime_col] >= t10_start)
            & (df_filtered[datetime_col] <= t10_end)
        ).sum()
        print(f"  T10 period detected: {t10_start} to {t10_end}")
        print(
            f"  Excluded {n_t10_excluded} rows during T10 interval (expert judgment applies)"
        )
    else:
        final_mask = mask_t8

    result = df_filtered[final_mask].copy()

    # Log filtering results
    n_total = len(df)
    n_kept = len(result)
    n_excluded = n_total - n_kept

    print(f"  T8 interval: {t8_start} to {t8_end}")
    print(
        f"  Filtered: {n_kept}/{n_total} rows kept, {n_excluded} excluded (outside T8 or within T10)"
    )

    return result


def get_event_timing_from_metadata(event_key: str, metadata: Dict) -> Dict[str, str]:
    """
    Extract timing information from event metadata dict (e.g., from export_web_data.py).

    Parameters:
    -----------
    event_key : str
        Event identifier (e.g., 'talim', 'ragasa')
    metadata : dict
        Event metadata dictionary (e.g., TYPHOON_EVENTS from export_web_data.py)

    Returns:
    --------
    dict with 'signal8_start', 'signal8_end', and optionally 'signal10_start'/'signal10_end'
    """
    if event_key not in metadata:
        raise ValueError(f"Event '{event_key}' not found in metadata")

    event = metadata[event_key]

    timing = {
        "signal8_start": event["official_signal8_start"],
        "signal8_end": event["official_signal8_end"],
    }

    # Add T10 timing if present
    if "official_signal10_start" in event and "official_signal10_end" in event:
        timing["signal10_start"] = event["official_signal10_start"]
        timing["signal10_end"] = event["official_signal10_end"]

    return timing


if __name__ == "__main__":
    # Example usage demonstration

    # Create sample data (2025-09-23 12:00 to 2025-09-24 22:00 = 34 hours = 204 10-min intervals + 1)
    n_intervals = 205
    sample_data = pd.DataFrame(
        {
            "datetime": pd.date_range(
                "2025-09-23 12:00", periods=n_intervals, freq="10min"
            ),
            "value": range(n_intervals),
        }
    )

    print("Example 1: Pure T8 event (Talim)")
    print("=" * 60)
    timing_talim = {
        "signal8_start": "2023-07-17 00:40",
        "signal8_end": "2023-07-17 16:20",
    }
    # Would filter sample_data if dates matched
    print(
        f"  T8 interval: {timing_talim['signal8_start']} to {timing_talim['signal8_end']}"
    )
    print("  No T10 escalation\n")

    print("Example 2: T8 with T10 escalation (Ragasa)")
    print("=" * 60)
    timing_ragasa = {
        "signal8_start": "2025-09-23 14:20",
        "signal8_end": "2025-09-24 20:20",
        "signal10_start": "2025-09-24 02:40",
        "signal10_end": "2025-09-24 13:20",
    }

    filtered = filter_to_t8_intervals(sample_data, timing_ragasa)
    print(f"  Result: {len(filtered)} rows in T8-only intervals")
    print(
        f"  T8 segments: [{timing_ragasa['signal8_start']} - {timing_ragasa['signal10_start']}) + "
        f"({timing_ragasa['signal10_end']} - {timing_ragasa['signal8_end']}]"
    )
