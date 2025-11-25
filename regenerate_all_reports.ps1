#!/usr/bin/env pwsh
# Regenerate all typhoon validation reports with refactored standards:
# - 30-minute persistence (3 consecutive 10-min intervals)
# - Includes T10 intervals in persistence detection (bug fix: T10 periods now counted)
# - Uses only 8 HKO reference stations (filtered via stations_reference_network.txt)

$ErrorActionPreference = "Stop"

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host "  HKO Signal 8 Validation - Report Regeneration (Refactored)"      -ForegroundColor Cyan
Write-Host "  Standards: 30-min persistence | Includes T10 intervals"            -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host ""

# Common parameters
$commonArgs = @(
    "--stations-file", "stations_reference_network.txt",
    "--method", "coverage",
    "--min-count", "4",
    "--min-stations", "8",  # HKO uses 8 reference stations
    "--persistence-periods", "3"
)

# Event 1: Talim (Pure T8, no T10)
Write-Host "[1/6] Talim 2023..." -ForegroundColor Yellow
$talimTiming = '{"signal8_start": "2023-07-17 00:40", "signal8_end": "2023-07-17 16:20"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Talim 20230717" `
    --out-dir "reports/talim_validation" `
    --signal-times $talimTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Talim analysis failed"; exit 1 }
Write-Host ""

# Event 2: Yagi (Pure T8, no T10)
Write-Host "[2/6] Yagi 2024..." -ForegroundColor Yellow
$yagiTiming = '{"signal8_start": "2024-09-05 18:20", "signal8_end": "2024-09-06 12:40"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Yagi" `
    --out-dir "reports/yagi_validation" `
    --signal-times $yagiTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Yagi analysis failed"; exit 1 }
Write-Host ""

# Event 3: Toraji (Pure T8, no T10)
Write-Host "[3/6] Toraji 2024..." -ForegroundColor Yellow
$torajiTiming = '{"signal8_start": "2024-11-13 23:10", "signal8_end": "2024-11-14 10:20"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Toraji" `
    --out-dir "reports/toraji_validation" `
    --signal-times $torajiTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Toraji analysis failed"; exit 1 }
Write-Host ""

# Event 4: Tapah (Pure T8, no T10)
Write-Host "[4/6] Tapah 2025..." -ForegroundColor Yellow
$tapahTiming = '{"signal8_start": "2025-09-07 21:20", "signal8_end": "2025-09-08 13:10"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Tapah 20250907-20250908" `
    --out-dir "reports/tapah_validation" `
    --signal-times $tapahTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Tapah analysis failed"; exit 1 }
Write-Host ""

# Event 5: Wipha (T8 with T10 escalation)
Write-Host "[5/6] Wipha 2025 (T8 with T10 exclusion)..." -ForegroundColor Yellow
$wiphaTiming = '{"signal8_start": "2025-07-20 00:20", "signal8_end": "2025-07-20 19:40", "signal10_start": "2025-07-20 09:20", "signal10_end": "2025-07-20 16:10"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Wipha 7.19 2230 - 7.21 0010" `
    --out-dir "reports/wipha_validation" `
    --signal-times $wiphaTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Wipha analysis failed"; exit 1 }
Write-Host ""

# Event 6: Ragasa (T8 with T10 escalation)
Write-Host "[6/6] Ragasa 2025 (T8 with T10 exclusion)..." -ForegroundColor Yellow
$ragasaTiming = '{"signal8_start": "2025-09-23 14:20", "signal8_end": "2025-09-24 20:20", "signal10_start": "2025-09-24 02:40", "signal10_end": "2025-09-24 13:20"}'
python analyze_typhoon.py `
    --input-folder "typhoon_data/Ragasa" `
    --out-dir "reports/ragasa_validation" `
    --signal-times $ragasaTiming `
    @commonArgs
if ($LASTEXITCODE -ne 0) { Write-Error "Ragasa analysis failed"; exit 1 }
Write-Host ""

Write-Host "==================================================================" -ForegroundColor Green
Write-Host "  ✓ All 6 event reports regenerated successfully!"                 -ForegroundColor Green
Write-Host "  - Persistence: 30 minutes, 3 periods"                             -ForegroundColor Green
Write-Host "  - Time filtering: Includes T10 intervals (bug fixed)"           -ForegroundColor Green
Write-Host "  - Reference network: 8 stations, 4-of-8 criterion"                -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Manually verify Talim and Ragasa results against official timing"
Write-Host "  2. Run: python export_web_data.py"
Write-Host "  3. Review updated JSON files in docs/data/events/"
