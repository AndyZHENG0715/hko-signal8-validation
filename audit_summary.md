# HKO Signal 8/10 Adherence Audit Summary

**Audit Date:** 2025-11-18 12:11:41
**Methodology:** Holland (2010) parametric wind model with terrain factors

## Overall Statistics

- **Total Decisions Audited:** 8
- **Adherent to Standards:** 5
- **Adherence Rate:** 62.5%
- **False Issuances:** 3
- **Delays:** 0

## Standards Applied

- **Signal 8:** Issue when ≥4 of 8 reference stations 'register or are expected to register' sustained winds at least gale force (≥63 km/h; stations ≥118 km/h also count toward ≥63) AND wind condition expected to persist (≥3 periods/≈30 min)
  - HKO considers both forecasts and the persistence of winds (transient, short-lived surges are not sufficient). A single interval or momentary wind reading does not directly determine the signal; operational human judgement is applied.
- **Signal 10:** Issue when hurricane-force winds (≥118 km/h) 'expected or blowing generally in Hong Kong near sea level' (≥2 stations OR center <50 km) — project interpretation; HKO applies expert judgement

## Event Results

| Event | Signal | Verdict | Algorithm | Official | Adherence | Reason |
|-------|--------|---------|-----------|----------|-----------|--------|
| Talim | T8 | ADHERENT | ISSUE | ISSUED | ✓ | Forecast: 4 stations ≥63 km/h, Current: 0 stations, Persistence: ≥3 periods c... |
| Yagi | T8 | ADHERENT | ISSUE | ISSUED | ✓ | Forecast: 8 stations ≥63 km/h, Current: 0 stations, Persistence: ≥3 periods c... |
| Toraji | T8 | FALSE_ISSUANCE | DONT_ISSUE | ISSUED | ✗ | Forecast: 1 stations, Current: 0 stations (need ≥4) |
| Wipha | T8 | ADHERENT | ISSUE | ISSUED | ✓ | Forecast: 4 stations ≥63 km/h, Current: 0 stations, Persistence: ≥3 periods c... |
| Wipha | T10 | ADHERENT | ISSUE | ISSUED | ✓ | Hurricane force expected: 2 stations ≥118 km/h, max 146 km/h, center 2 km fro... |
| Tapah | T8 | ADHERENT | ISSUE | ISSUED | ✓ | Forecast: 4 stations ≥63 km/h, Current: 0 stations, Persistence: ≥3 periods c... |
| Ragasa | T8 | FALSE_ISSUANCE | DONT_ISSUE | ISSUED | ✗ | Forecast: 3 stations, Current: 1 stations (need ≥4) |
| Ragasa | T10 | FALSE_ISSUANCE | DONT_ISSUE | ISSUED | ✗ | Max forecast: 94 km/h, Max current: 115 km/h, Hurricane stations: 0/2 needed ... |

## Reference Stations (8 official HKO stations)

1. Cheung Chau (99m elevation)
2. Chek Lap Kok / HK Airport (14m)
3. Kai Tak (16m)
4. Lau Fau Shan (50m)
5. Sai Kung (32m)
6. Sha Tin (16m)
7. Ta Kwu Ling (28m)
8. Tsing Yi (43m)

## Methodology Details

### Wind Model
- Holland (2010) parametric tropical cyclone wind model
- Computes gradient wind at each station based on distance from center
- Applies B-parameter (shape) = 1.5 for mature typhoons

### Terrain Factors
- **Exposed coastal** (≥80m elevation): 0.85 reduction factor
- **Semi-sheltered** (40-79m): 0.70 reduction factor
- **Inland valleys** (<40m): 0.60 reduction factor
- Elevation correction applied using power law (α=0.15)

### Decision Criteria

**Signal 8:**
- Forecast OR current observations show ≥4 stations with ≥63 km/h (including ≥118)
- Persistence check: ≥3 consecutive 10-min periods (30 min window)
- Accounts for 'expected to register' language in HKO standards

**Signal 10:**
- Forecast OR current ≥118 km/h at ≥2 stations, OR
- Max wind ≥118 km/h AND typhoon center <50 km from Hong Kong
- Note: 'Generally in Hong Kong' is approximated for this audit as ≥2 stations ≥118 km/h or center <50 km (project interpretation); HKO uses expert judgement and may differ (rare exceptions acknowledged)

## Key Findings

⚠ **Adherence concerns** - Some issuances deviate from published criteria
- 3 case(s) where signals issued without meeting stated criteria

---

*This audit validates HKO's forecast-based issuance approach against their published standards.*
*Forecast-driven warnings are appropriate and align with WMO best practices.*