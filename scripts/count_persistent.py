import csv
from datetime import datetime
path = r"d:\Dev\GCAP3226\reports\talim_validation\time_summary.csv"
start_dt = datetime.strptime("2023-07-17 07:10:00", "%Y-%m-%d %H:%M:%S")
rows = []
with open(path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)
res = [r["datetime"] for r in rows if datetime.strptime(r["datetime"], "%Y-%m-%d %H:%M:%S") >= start_dt and r["in_T8_window"] == "True" and r["persistent_T8"] == "True"]
print(len(res))
print(res)
