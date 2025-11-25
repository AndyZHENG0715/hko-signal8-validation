#!/usr/bin/env python3
"""Regenerate all 11 typhoon events with fixed algorithm."""
import subprocess
import sys
from pathlib import Path

events = [
    ("Chaba 220701-220702", "chaba_validation", '{"signal8_start": "2022-07-01 19:10", "signal8_end": "2022-07-02 16:20"}'),
    ("Ma-on 220824-220825", "ma-on_validation", '{"signal8_start": "2022-08-24 19:25", "signal8_end": "2022-08-25 09:20"}'),
    ("Nalgae 221102-221103", "nalgae_validation", '{"signal8_start": "2022-11-02 13:40", "signal8_end": "2022-11-03 05:20"}'),
    ("Talim 20230717", "talim_validation", '{"signal8_start": "2023-07-17 00:40", "signal8_end": "2023-07-17 16:20"}'),
    ("Saola 230901-230902", "saola_validation", '{"signal8_start": "2023-09-01 02:40", "signal8_end": "2023-09-02 16:20", "signal10_start": "2023-09-01 20:15", "signal10_end": "2023-09-02 03:40"}'),
    ("Koinu", "koinu_validation", '{"signal8_start": "2023-10-08 12:40", "signal8_end": "2023-10-09 11:40"}'),
    ("Yagi", "yagi_validation", '{"signal8_start": "2024-09-05 18:20", "signal8_end": "2024-09-06 12:40"}'),
    ("Toraji", "toraji_validation", '{"signal8_start": "2024-11-13 23:10", "signal8_end": "2024-11-14 10:20"}'),
    ("Tapah 20250907-20250908", "tapah_validation", '{"signal8_start": "2025-09-07 21:20", "signal8_end": "2025-09-08 13:10"}'),
    ("Wipha 7.19 2230 - 7.21 0010", "wipha_validation", '{"signal8_start": "2025-07-20 00:20", "signal8_end": "2025-07-20 19:40", "signal10_start": "2025-07-20 09:20", "signal10_end": "2025-07-20 16:10"}'),
    ("Ragasa", "ragasa_validation", '{"signal8_start": "2025-09-23 14:20", "signal8_end": "2025-09-24 20:20", "signal10_start": "2025-09-24 02:40", "signal10_end": "2025-09-24 13:20"}'),
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
    timing_file = Path(f"temp_{out_dir}_timing.json")
    timing_file.write_text(timing, encoding="utf-8")

    cmd = [
        "python", "analyze_typhoon.py",
        "--input-folder", f"typhoon_data/{folder}",
        "--out-dir", f"reports/{out_dir}",
        "--signal-times", str(timing_file),
    ] + common_args

    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if result.returncode != 0:
        print(f"ERROR processing {folder}:")
        print(result.stderr)
        sys.exit(1)
    print(f"OK {folder} done")

    timing_file.unlink()

print("\nAll 11 events regenerated!")
