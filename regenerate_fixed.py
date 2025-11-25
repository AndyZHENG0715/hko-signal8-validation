#!/usr/bin/env python3
"""Quick script to regenerate all events with fixed algorithm."""
import subprocess
import sys
from pathlib import Path

events = [
    ("Talim 20230717", "talim_validation", "talim_timing.json"),
    ("Yagi", "yagi_validation", '{"signal8_start": "2024-09-05 18:20", "signal8_end": "2024-09-06 12:40"}'),
    ("Toraji", "toraji_validation", '{"signal8_start": "2024-11-13 23:10", "signal8_end": "2024-11-14 10:20"}'),
    ("Tapah 20250907-20250908", "tapah_validation", '{"signal8_start": "2025-09-07 21:20", "signal8_end": "2025-09-08 13:10"}'),
    ("Wipha 7.19 2230 - 7.21 0010", "wipha_validation", '{"signal8_start": "2025-07-20 00:20", "signal8_end": "2025-07-20 19:40", "signal10_start": "2025-07-20 09:20", "signal10_end": "2025-07-20 16:10"}'),
    ("Ragasa", "ragasa_validation", "ragasa_timing.json"),
]

common_args = [
    "--stations-file", "stations_reference_network.txt",
    "--method", "coverage",
    "--min-count", "4",
    "--min-stations", "8",
    "--persistence-periods", "3"
]

for folder, out_dir, timing in events:
    print(f"\nProcessing {folder}...")
    timing_file = Path(timing)
    if timing_file.exists():
        timing_arg = str(timing_file)
    else:
        # Create temp file
        timing_file = Path(f"temp_{out_dir}_timing.json")
        timing_file.write_text(timing)
        timing_arg = str(timing_file)

    cmd = [
        "python", "analyze_typhoon.py",
        "--input-folder", f"typhoon_data/{folder}",
        "--out-dir", f"reports/{out_dir}",
        "--signal-times", timing_arg,
    ] + common_args

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR processing {folder}:")
        print(result.stderr)
        sys.exit(1)
    print(f"OK {folder} done")

    # Clean up temp file
    if timing_file.name.startswith("temp_"):
        timing_file.unlink()

print("\nAll events regenerated!")
