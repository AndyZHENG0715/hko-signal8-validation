import csv
import statistics
import json
import pathlib

# Mapping of event names to time_summary.csv paths
EVENT_FILES = {
    "Talim": pathlib.Path(r"d:\Dev\GCAP3226\reports\talim_validation\time_summary.csv"),
    "Tapah": pathlib.Path(r"d:\Dev\GCAP3226\reports\tapah_validation\time_summary.csv"),
    "Toraji": pathlib.Path(
        r"d:\Dev\GCAP3226\reports\toraji_validation\time_summary.csv"
    ),
    "Wipha": pathlib.Path(r"d:\Dev\GCAP3226\reports\wipha_validation\time_summary.csv"),
    "Yagi": pathlib.Path(r"d:\Dev\GCAP3226\reports\yagi_validation\time_summary.csv"),
    "Ragasa": pathlib.Path(
        r"d:\Dev\GCAP3226\reports\ragasa_validation\time_summary.csv"
    ),
}

INTERVAL_MINUTES = 10

per_event = []
all_segment_lengths_intervals = []  # raw lengths in 10-min intervals
all_continuous_segment_hours = []

for event, path in EVENT_FILES.items():
    if not path.exists():
        continue
    with path.open("r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        flags = []  # True if count_ge_T8 >=4
        for row in reader:
            try:
                cnt = int(row["count_ge_T8"])
            except ValueError:
                # handle possible float? convert safely
                cnt = int(float(row["count_ge_T8"]))
            flags.append(cnt >= 4)
        total_intervals = sum(flags)
        total_hours = total_intervals * INTERVAL_MINUTES / 60.0
        # Find continuous segments
        segments = []  # lengths in intervals
        current_len = 0
        for flag in flags:
            if flag:
                current_len += 1
            else:
                if current_len > 0:
                    segments.append(current_len)
                    current_len = 0
        if current_len > 0:
            segments.append(current_len)

        max_continuous_intervals = max(segments) if segments else 0
        max_continuous_hours = max_continuous_intervals * INTERVAL_MINUTES / 60.0
        segment_hours = [s * INTERVAL_MINUTES / 60.0 for s in segments]
        all_continuous_segment_hours.extend(segment_hours)
        all_segment_lengths_intervals.extend(segments)

        # Per-event segment length stats (in intervals)
        if segments:
            mean_seg = sum(segments) / len(segments)
            median_seg = statistics.median(segments)
            min_seg = min(segments)
            max_seg = max(segments)
        else:
            mean_seg = median_seg = min_seg = max_seg = 0

        per_event.append(
            {
                "event": event,
                "segment_count": len(segments),
                "mean_segment_length_intervals": mean_seg,
                "median_segment_length_intervals": median_seg,
                "min_segment_length_intervals": min_seg,
                "max_segment_length_intervals": max_seg,
                "total_intervals": total_intervals,
                "total_hours": total_hours,
                "max_continuous_intervals": max_continuous_intervals,
                "max_continuous_hours": max_continuous_hours,
                "continuous_segments_hours": segment_hours,
                "continuous_segments_intervals": segments,
            }
        )

# Aggregated stats across events (total_hours and max_continuous_hours)
if per_event:
    total_hours_list = [e["total_hours"] for e in per_event]
    max_hours_list = [e["max_continuous_hours"] for e in per_event]

    def stats(lst):
        return {
            "min": min(lst),
            "max": max(lst),
            "average": sum(lst) / len(lst),
            "median": statistics.median(lst),
        }

    summary = {
        "total_hours": stats(total_hours_list),
        "max_continuous_hours": stats(max_hours_list),
    }
else:
    summary = {}

# Stats across all continuous segments (distribution of segment durations)
if all_continuous_segment_hours:
    segment_summary = {
        "min": min(all_continuous_segment_hours),
        "max": max(all_continuous_segment_hours),
        "average": sum(all_continuous_segment_hours)
        / len(all_continuous_segment_hours),
        "median": statistics.median(all_continuous_segment_hours),
    }
else:
    segment_summary = {}

overall_mean_segment_length_intervals = (
    sum(all_segment_lengths_intervals) / len(all_segment_lengths_intervals)
    if all_segment_lengths_intervals
    else 0
)

output = {
    "per_event": per_event,
    "summary_across_events": summary,
    "continuous_segment_duration_distribution_hours": segment_summary,
    "overall_mean_segment_length_intervals": overall_mean_segment_length_intervals,
    "recommended_persistence_threshold_intervals": round(
        overall_mean_segment_length_intervals, 2
    ),
}

print(json.dumps(output, indent=2))
