import pandas as pd
df = pd.read_csv('reports/ragasa_validation/time_summary.csv')
row = df[df['datetime'] == '2025-09-24 02:40:00'].iloc[0]
print('Row data:')
print(f"count_ge_T8: {row['count_ge_T8']}")
print(f"n_stations: {row['n_stations']}")
print(f"coverage_T8: {row['coverage_T8']}")
print(f"recommended_signal: {row['recommended_signal']}")
print(f"in_T8_window: {row['in_T8_window']}")
print(f"in_T10_window: {row['in_T10_window']}")

# Check what the qualifying logic would produce
count_ge_t8 = int(row['count_ge_T8'])
n_stations = int(row['n_stations'])
min_stations = 8  # from --min-stations default
min_count = 4
has_min_stations = n_stations >= min_stations
coverage_ok = count_ge_t8 >= min_count
rec_sig = str(row['recommended_signal'])
label_ok = rec_sig in {"T8", "T10"}
count_ok = count_ge_t8 >= 4
in_t8_window = bool(row['in_T8_window'])

print(f"\nQualifying check components:")
print(f"has_min_stations ({n_stations} >= {min_stations}): {has_min_stations}")
print(f"coverage_ok ({count_ge_t8} >= {min_count}): {coverage_ok}")
print(f"label_ok ({rec_sig} in {{T8, T10}}): {label_ok}")
print(f"count_ok ({count_ge_t8} >= 4): {count_ok}")
print(f"in_t8_window: {in_t8_window}")
print(f"Should qualify: {has_min_stations and (label_ok or count_ok) and coverage_ok and in_t8_window}")

