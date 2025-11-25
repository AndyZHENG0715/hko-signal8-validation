# Development Plan (Live Execution Log)

This file tracks the phased implementation of the enhanced HKO Signal 8 Transparency Portal. It is updated as changes are made to preserve context for future contributors and AI agents.

## Phase Overview (Status)
1. Dual-Track Documentation (observation vs forecast audit) – PARTIAL (observation tier system + audit page scaffold complete)
2. 3-Tier Categorization Implementation – COMPLETE (export logic + JSON + UI badges)
3. Public-Facing Language Simplification – IN PROGRESS (methodology + main/event pages updated; about page pending rewrite)
4. Methodology Page Enhancements – COMPLETE (neutral framing, social/economic cost, bilingual text)
5. Data-Driven Architecture – IN PROGRESS (dynamic JSON export, no manual hard-coding; continuous validation) 
6. Multi-Event Comparison Tool – IN PROGRESS (baseline table + sparklines implemented; overlay & export pending)
7. File Structure Consolidation (/research, /docs/archive) – NOT STARTED

## Observation Track Classification (Implemented)
- Tier 1: VERIFIED – ≥4 of 8 stations ≥63 km/h for ≥3 consecutive 10‑min intervals (≈30 min) within official Signal 8 window.
- Tier 2: PATTERN-VALIDATED – Wind re‑emergence pattern: meet threshold (≥4) → lull (<4 for ≥2 intervals) → meet again; no Tier 1 persistence.
- Tier 3: UNVERIFIED – Neither persistence nor pattern detected.
- NO_SIGNAL – Official Signal 8 not issued.

Note: Tier 2 avoids "eye" terminology to remain structurally descriptive.

## JSON Schema (Current)
Per-event JSON (`docs/data/events/<id>.json`):
- `verification_tier`: `verified` | `pattern_validated` | `unverified` | `no_signal`
- `algorithm_detection.detected`: boolean (Tier 1 persistence)
- `algorithm_detection.pattern_validated`: boolean (Tier 2)
Summary JSON (`docs/data/events/summary.json`):
- Includes `verification_tier` per event + `tier_counts` aggregate.

## Front-End Adjustments (Completed/Active)
- Badges implemented (✅ / ⚠️ / ❓)
- Standard term adopted: "Early Warning Time" across portal (replaces "Early Warning Advantage" / "Lead Time" / "Advance Warning Time").
- Chart annotations repaired (event timeline) with persistent vs intermittent segments + pattern boxes.
- Chart X-axis now shows labels every 30 minutes (00:00, 00:30, 01:00...) in 24-hour format for consistency.
- Tier-based border colors implemented (verified=green, pattern_validated=yellow, unverified=gray) overriding severity colors.
- Comparison page adds multi-event table & sparkline mini timelines.

## Dual Tracks
- Observation portal (primary public surface): tiers + timelines.
- Forecast audit (advanced): `audit.html` now live referencing `audit_report.json` / `audit_summary.md` + criteria list.

## Implementation Log (Chronological)
| Timestamp (UTC) | Phase | Action | Notes |
|-----------------|-------|--------|-------|
| 2025-11-24T00:00 | 1 | Created DEVELOPMENT_PLAN.md | Initialized live execution log |
| 2025-11-24T00:40 | 2 | Implemented tier logic in export_web_data.py | Added pattern detection + verification_tier assignment |
| 2025-11-24T01:05 | 4 | Rewrote methodology.html | Added neutral framing, tiers, bilingual content |
| 2025-11-24T01:30 | 6 | Added comparison page (compare.html + compare.js) | Multi-event selection + metrics table + sparklines |
| 2025-11-24T01:50 | 2 | Repaired event.js chart logic | Persistent & intermittent annotation + pattern boxes |
| 2025-11-24T02:10 | 1 | Created audit.html + audit.css | Forecast audit separation established |
| 2025-11-24T02:15 | 1 | Updated global navigation & footers | Added Compare + Audit links across pages |
| 2025-11-24T04:20 | 5 | Pattern validation script + terminology fix | Created tools/validate_pattern_detection.py; changed "Advantage" → "Time" globally; fixed tier border colors; improved chart X-axis intervals |

## Current Focus (Next Iterations)
- ✅ COMPLETED: Pattern validation script (tools/validate_pattern_detection.py) - audits tier logic, outputs JSON.
- ✅ COMPLETED: Wording changed to "Early Warning Time" (提前預警時間) globally.
- ✅ COMPLETED: Tier-based card border colors (verified=green, pattern_validated=yellow, unverified=gray).
- ✅ COMPLETED: Chart X-axis improved (30-min interval labels, 24-hour format).
- Extend comparison tool: aggregated overlay chart (stacked coverage or tier timeline), export (CSV/JSON) of selected subset.
- README / docs/README updates for dual-track explanation & schema changes + terminology.
- Implement interactive chart controls (toggle layers, dual Y-axis for mean wind speed, zoom/pan).
- Add interactive station heatmap (replacing or augmenting static PNG).
- Reference station map visualization (methodology page).

## Planned Enhancements / Backlog
- Accessibility review (ARIA labels for comparison table controls).
- Station sensitivity explorer integration (link from comparison).
- Add a consolidated "All Events Timeline" overlay view.
- Parameterized persistence window sensitivity (already in sensitivity.json; surface on site).
- File structure cleanup: move research scripts into /research/ keeping /docs/ minimal.

## Next Actions (Immediate)
1. ✅ Pattern detection validation script - DONE
2. ✅ Global wording consistency (Early Warning Time) - DONE
3. Update README.md & docs/README.md with "Early Warning Time" terminology & tier system details.
4. Implement chart interactive controls (layer toggles, dual Y-axis).
5. Comparison overlay chart (aggregate timeline).
6. Interactive station heatmap.
7. Reference station map (methodology page).

## Guidance for Future Contributors / Agents
- When changing thresholds (e.g., persistence period), update: this file, README, methodology.html, export_web_data.py, event.js, compare.js.
- Maintain bilingual attributes (`data-en` / `data-zh`) for all new UI text.
- Keep JSON schemas stable; version if breaking changes occur.
- Prefer pathlib in Python scripts; avoid hard-coded OS-specific paths.

## Pending Questions
None – proceed autonomously.


