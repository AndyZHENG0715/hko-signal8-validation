# Repository Structure

## Core Scripts

- **`analyze_typhoon.py`** - Main analysis script for observation-only wind validation
- **`hko_compliant_algorithm.py`** - HKO forecast-based compliance algorithm (audit logic)
- **`run_hko_audit.py`** - Execute full compliance audit across all events
- **`export_web_data.py`** - Export validation results to JSON for web portal
- **`generate_report_figures.py`** - Generate timeline and heatmap visualizations
- **`persistence_sensitivity.py`** - Analyze sensitivity to persistence thresholds

## Documentation

- **`README.md`** - Main project documentation and overview
- **`HKO_AUDIT_README.md`** - Compliance audit methodology and results
- **`QUICK_START.md`** - Quick start guide for running analysis
- **`.github/copilot-instructions.md`** - Agent guidance for repository

## Configuration

- **`requirements.txt`** - Python dependencies
- **`stations_reference_network.txt`** - HKO's 8 official reference stations

## Data Directories

### `typhoon_data/`
Raw HKO wind data (10-minute means) organized by typhoon event:
- `Talim 20230717/`
- `Tapah 20250907-20250908/`
- `Toraji/`
- `Wipha 7.19 2230 - 7.21 0010/`
- `Yagi/`
- `Ragasa/` (Chinese headers; use `Ragasa_en/` after normalization)

### `reports/`
Analysis outputs:
- `{event}_validation/` - Per-event CSV reports (`time_summary.csv`, `station_summary.csv`)
- `figs/` - Timeline and heatmap figures for each event

### `docs/`
Web portal (GitHub Pages):
- `data/` - JSON exports for web consumption
  - `events/*.json` - Individual event data
  - `events/summary.json` - All events overview
  - `stations.json` - Reference station metadata
  - `sensitivity.json` - Persistence sensitivity data
- HTML/CSS/JS files for interactive portal

### `data/`
Supporting data:
- `station_name_map_ragasa.json` - Chinese-to-English station name mappings

### `tools/`
Utility scripts:

## Current Reports

- **`audit_report.json`** - Latest compliance audit (JSON)
- **`audit_summary.md`** - Human-readable audit summary (Markdown)

## Workflow

1. **Normalize Ragasa data** (if needed):
   ```bash
   python tools/normalize_ragasa_to_english.py
   ```

2. **Run observation-only analysis** per event:
   ```bash
   python analyze_typhoon.py --input-folder "typhoon_data/Talim 20230717" \
       --stations-file stations_reference_network.txt \
       --method coverage --min-count 4 --persistence-periods 3 \
       --out-dir reports/talim_validation
   ```

3. **Generate figures** (optional):
   ```bash
   python generate_report_figures.py
   ```

4. **Export for web portal**:
   ```bash
   python export_web_data.py
   ```

5. **Run compliance audit**:
   ```bash
   python run_hko_audit.py
   ```

## Notes

- Keep validation folders in `reports/` named `{event}_validation` to match `export_web_data.py` configuration
- Always use `--stations-file stations_reference_network.txt` for HKO-compliant S8 analysis (8 reference stations)
- Portal data in `docs/data/` is auto-generated; do not hand-edit
- For persistence sensitivity analysis, run `persistence_sensitivity.py` before exporting
