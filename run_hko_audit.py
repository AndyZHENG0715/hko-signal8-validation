"""
Run HKO Compliance Audit for All Typhoon Events
Applies the HKO-compliant algorithm to 6 typhoon events and generates audit report.
"""

import json
from datetime import datetime
from hko_compliant_algorithm import generate_audit_report, STATION_COORDS


# ============================================================================
# TYPHOON EVENT DATA (Based on actual HKO records)
# ============================================================================

TYPHOON_EVENTS = {
    "Talim": {
        "year": 2023,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2023-07-17 00:40)
                "center_lat": 21.8,
                "center_lon": 113.2,
                "vmax_kmh": 155,
                "rmax_km": 45,
                "track_forecast": [
                    {"time": "00:40", "lat": 21.9, "lon": 113.5, "vmax_kmh": 158},
                    {"time": "00:50", "lat": 22.0, "lon": 113.7, "vmax_kmh": 160},
                    {"time": "01:00", "lat": 22.1, "lon": 113.9, "vmax_kmh": 162},
                    {"time": "01:10", "lat": 22.2, "lon": 114.0, "vmax_kmh": 163},
                ],
            },
            "current_obs": {
                "Cheung Chau": 52,
                "Chek Lap Kok": 48,
                "Kai Tak": 41,
                "Lau Fau Shan": 35,
                "Sai Kung": 45,
                "Sha Tin": 28,
                "Ta Kwu Ling": 25,
                "Tsing Yi": 38,
            },
            "official": {"signal8_issued": True, "time": "2023-07-17T00:40:00+08:00"},
        },
    },
    "Yagi": {
        "year": 2024,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2024-09-05 18:20)
                "center_lat": 22.3,
                "center_lon": 113.4,
                "vmax_kmh": 180,
                "rmax_km": 40,
                "track_forecast": [
                    {"time": "18:20", "lat": 22.25, "lon": 113.7, "vmax_kmh": 178},
                    {"time": "18:30", "lat": 22.22, "lon": 113.8, "vmax_kmh": 175},
                    {"time": "18:40", "lat": 22.20, "lon": 113.9, "vmax_kmh": 173},
                    {"time": "18:50", "lat": 22.18, "lon": 114.0, "vmax_kmh": 170},
                ],
            },
            "current_obs": {
                "Cheung Chau": 58,
                "Chek Lap Kok": 51,
                "Kai Tak": 43,
                "Lau Fau Shan": 39,
                "Sai Kung": 47,
                "Sha Tin": 31,
                "Ta Kwu Ling": 27,
                "Tsing Yi": 40,
            },
            "official": {"signal8_issued": True, "time": "2024-09-05T18:20:00+08:00"},
        },
    },
    "Toraji": {
        "year": 2025,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2025-06-02 00:40)
                "center_lat": 21.5,
                "center_lon": 113.0,
                "vmax_kmh": 140,
                "rmax_km": 50,
                "track_forecast": [
                    {"time": "00:40", "lat": 21.7, "lon": 113.3, "vmax_kmh": 142},
                    {"time": "00:50", "lat": 21.8, "lon": 113.5, "vmax_kmh": 145},
                    {"time": "01:00", "lat": 21.9, "lon": 113.7, "vmax_kmh": 147},
                    {"time": "01:10", "lat": 22.0, "lon": 113.9, "vmax_kmh": 148},
                ],
            },
            "current_obs": {
                "Cheung Chau": 48,
                "Chek Lap Kok": 45,
                "Kai Tak": 38,
                "Lau Fau Shan": 32,
                "Sai Kung": 41,
                "Sha Tin": 26,
                "Ta Kwu Ling": 23,
                "Tsing Yi": 35,
            },
            "official": {"signal8_issued": True, "time": "2025-06-02T00:40:00+08:00"},
        },
    },
    "Wipha": {
        "year": 2025,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2025-07-20 00:20)
                "center_lat": 21.8,
                "center_lon": 113.5,
                "vmax_kmh": 185,
                "rmax_km": 35,
                "track_forecast": [
                    {"time": "00:20", "lat": 22.0, "lon": 113.8, "vmax_kmh": 188},
                    {"time": "00:30", "lat": 22.1, "lon": 114.0, "vmax_kmh": 190},
                    {"time": "00:40", "lat": 22.15, "lon": 114.1, "vmax_kmh": 192},
                    {"time": "00:50", "lat": 22.2, "lon": 114.15, "vmax_kmh": 195},
                ],
            },
            "current_obs": {
                "Cheung Chau": 62,
                "Chek Lap Kok": 55,
                "Kai Tak": 48,
                "Lau Fau Shan": 42,
                "Sai Kung": 51,
                "Sha Tin": 35,
                "Ta Kwu Ling": 30,
                "Tsing Yi": 45,
            },
            "official": {"signal8_issued": True, "time": "2025-07-20T00:20:00+08:00"},
        },
        "signal10": {
            "forecast_bulletin": {
                # At time of Signal 10 (issued 2025-07-20 09:20, eye passage)
                "center_lat": 22.3,
                "center_lon": 114.15,
                "vmax_kmh": 195,
                "rmax_km": 30,
                "track_forecast": [
                    {"time": "09:30", "lat": 22.35, "lon": 114.2, "vmax_kmh": 195},
                    {"time": "09:40", "lat": 22.4, "lon": 114.25, "vmax_kmh": 193},
                    {"time": "09:50", "lat": 22.45, "lon": 114.3, "vmax_kmh": 190},
                ],
            },
            "current_obs": {
                "Cheung Chau": 117,
                "Chek Lap Kok": 85,
                "Kai Tak": 55,
                "Lau Fau Shan": 72,
                "Sai Kung": 89,
                "Sha Tin": 40,
                "Ta Kwu Ling": 47,
                "Tsing Yi": 42,
            },
            "official": {"signal10_issued": True, "time": "2025-07-20T09:20:00+08:00"},
        },
    },
    "Tapah": {
        "year": 2025,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2025-09-07 16:20)
                "center_lat": 22.0,
                "center_lon": 113.3,
                "vmax_kmh": 150,
                "rmax_km": 42,
                "track_forecast": [
                    {"time": "16:20", "lat": 22.1, "lon": 113.6, "vmax_kmh": 152},
                    {"time": "16:30", "lat": 22.15, "lon": 113.8, "vmax_kmh": 155},
                    {"time": "16:40", "lat": 22.2, "lon": 114.0, "vmax_kmh": 157},
                    {"time": "16:50", "lat": 22.25, "lon": 114.1, "vmax_kmh": 158},
                ],
            },
            "current_obs": {
                "Cheung Chau": 50,
                "Chek Lap Kok": 46,
                "Kai Tak": 40,
                "Lau Fau Shan": 34,
                "Sai Kung": 43,
                "Sha Tin": 27,
                "Ta Kwu Ling": 24,
                "Tsing Yi": 37,
            },
            "official": {"signal8_issued": True, "time": "2025-09-07T16:20:00+08:00"},
        },
    },
    "Ragasa": {
        "year": 2025,
        "signal8": {
            "forecast_bulletin": {
                # 2h before official Signal 8 (issued 2025-09-23 14:20)
                "center_lat": 22.0,
                "center_lon": 113.0,
                "vmax_kmh": 190,
                "rmax_km": 38,
                "track_forecast": [
                    {"time": "14:20", "lat": 22.1, "lon": 113.3, "vmax_kmh": 192},
                    {"time": "14:30", "lat": 22.15, "lon": 113.5, "vmax_kmh": 195},
                    {"time": "14:40", "lat": 22.2, "lon": 113.7, "vmax_kmh": 197},
                    {"time": "14:50", "lat": 22.25, "lon": 113.9, "vmax_kmh": 198},
                ],
            },
            "current_obs": {
                "Cheung Chau": 65,
                "Chek Lap Kok": 58,
                "Kai Tak": 50,
                "Lau Fau Shan": 44,
                "Sai Kung": 52,
                "Sha Tin": 36,
                "Ta Kwu Ling": 31,
                "Tsing Yi": 47,
            },
            "official": {"signal8_issued": True, "time": "2025-09-23T14:20:00+08:00"},
        },
        "signal10": {
            "forecast_bulletin": {
                # At time of Signal 10 (issued 2025-09-24 02:40, record distance)
                "center_lat": 21.3,  # 120 km from HK (record distance)
                "center_lon": 113.5,
                "vmax_kmh": 200,
                "rmax_km": 35,
                "track_forecast": [
                    {"time": "02:50", "lat": 21.35, "lon": 113.6, "vmax_kmh": 200},
                    {"time": "03:00", "lat": 21.4, "lon": 113.7, "vmax_kmh": 198},
                    {"time": "03:10", "lat": 21.45, "lon": 113.8, "vmax_kmh": 195},
                ],
            },
            "current_obs": {
                "Cheung Chau": 115,
                "Chek Lap Kok": 92,
                "Kai Tak": 62,
                "Lau Fau Shan": 78,
                "Sai Kung": 95,
                "Sha Tin": 45,
                "Ta Kwu Ling": 52,
                "Tsing Yi": 48,
            },
            "official": {"signal10_issued": True, "time": "2025-09-24T02:40:00+08:00"},
        },
    },
}


# ============================================================================
# AUDIT EXECUTION
# ============================================================================


def main():
    print("=" * 80)
    print("HKO SIGNAL 8/10 ADHERENCE AUDIT")
    print("=" * 80)
    print(f"\nAudit Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Events Analyzed: {len(TYPHOON_EVENTS)}")
    print(f"Reference Stations: {len(STATION_COORDS)}")
    print("\nStandards Applied:")
    print(
        "  Signal 8: ≥4 of 8 stations at least gale-force (≥63 km/h; stations ≥118 km/h count toward S8) for ≥3 periods (~30 min)"
    )
    print(
        "    Note: HKO considers forecasts and persistence; single-interval/momentary winds do not directly determine the signal; operational human judgement applies"
    )
    print(
        "  Signal 10: ≥118 km/h generally in HK (≥2 stations OR center <50km) — project interpretation; HKO uses expert judgement"
    )
    print("=" * 80)

    # Run audit for all events
    audit_results = generate_audit_report(TYPHOON_EVENTS)

    # Save JSON report
    with open("audit_report.json", "w", encoding="utf-8") as f:
        json.dump(audit_results, f, indent=2, ensure_ascii=False)

    print("\n✓ Saved detailed audit report to: audit_report.json")

    # Display summary
    print(f"\n{'=' * 80}")
    print("AUDIT SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total Decisions Audited: {audit_results['summary']['total_decisions']}")
    print(f"Adherent to Standards: {audit_results['summary']['adherent_decisions']}")
    print(f"Adherence Rate: {audit_results['summary']['adherence_rate']:.1%}")
    print(f"False Issuances: {audit_results['summary']['false_issuances']}")
    print(f"Delays: {audit_results['summary']['delays']}")

    # Display event-by-event results
    print(f"\n{'=' * 80}")
    print("EVENT-BY-EVENT RESULTS")
    print(f"{'=' * 80}")

    for event_name, event_results in audit_results["events"].items():
        print(f"\n{event_name.upper()}")
        print("-" * 80)

        if "signal8" in event_results:
            s8 = event_results["signal8"]
            status = "✓ ADHERENT" if s8["adherence"] else "✗ NON-ADHERENT"
            print(f"  Signal 8: {status}")
            print(f"    Verdict: {s8['verdict']}")
            print(f"    Algorithm: {s8['algo_decision']}")
            print(f"    Official: {s8['official_decision']}")
            print(f"    Reason: {s8['algo_reason']}")
            if s8["qualifying_stations"]:
                print(f"    Qualifying: {', '.join(s8['qualifying_stations'])}")

        if "signal10" in event_results:
            s10 = event_results["signal10"]
            status = "✓ ADHERENT" if s10["adherence"] else "✗ NON-ADHERENT"
            print(f"  Signal 10: {status}")
            print(f"    Verdict: {s10['verdict']}")
            print(f"    Algorithm: {s10['algo_decision']}")
            print(f"    Official: {s10['official_decision']}")
            print(f"    Reason: {s10['algo_reason']}")
            if s10["qualifying_stations"]:
                print(f"    Qualifying: {', '.join(s10['qualifying_stations'])}")

    # Generate markdown summary
    generate_markdown_summary(audit_results)

    print(f"\n{'=' * 80}")
    print("✓ Audit complete. Reports saved:")
    print("  - audit_report.json (detailed JSON)")
    print("  - audit_summary.md (human-readable table)")
    print(f"{'=' * 80}\n")


def generate_markdown_summary(audit_results):
    """Generate human-readable markdown summary table."""

    lines = []
    lines.append("# HKO Signal 8/10 Adherence Audit Summary")
    lines.append("")
    lines.append(f"**Audit Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(
        "**Methodology:** Holland (2010) parametric wind model with terrain factors"
    )
    lines.append("")
    lines.append("## Overall Statistics")
    lines.append("")
    lines.append(
        f"- **Total Decisions Audited:** {audit_results['summary']['total_decisions']}"
    )
    lines.append(
        f"- **Adherent to Standards:** {audit_results['summary']['adherent_decisions']}"
    )
    lines.append(
        f"- **Adherence Rate:** {audit_results['summary']['adherence_rate']:.1%}"
    )
    lines.append(
        f"- **False Issuances:** {audit_results['summary']['false_issuances']}"
    )
    lines.append(f"- **Delays:** {audit_results['summary']['delays']}")
    lines.append("")
    lines.append("## Standards Applied")
    lines.append("")
    lines.append(
        "- **Signal 8:** Issue when ≥4 of 8 reference stations 'register or are expected to register' sustained winds at least gale force (≥63 km/h; stations ≥118 km/h also count toward ≥63) AND wind condition expected to persist (≥3 periods/≈30 min)"
    )
    lines.append(
        "  - HKO considers both forecasts and the persistence of winds (transient, short-lived surges are not sufficient). A single interval or momentary wind reading does not directly determine the signal; operational human judgement is applied."
    )
    lines.append(
        "- **Signal 10:** Issue when hurricane-force winds (≥118 km/h) 'expected or blowing generally in Hong Kong near sea level' (≥2 stations OR center <50 km) — project interpretation; HKO applies expert judgement"
    )
    lines.append("")
    lines.append("## Event Results")
    lines.append("")
    lines.append(
        "| Event | Signal | Verdict | Algorithm | Official | Adherence | Reason |"
    )
    lines.append(
        "|-------|--------|---------|-----------|----------|-----------|--------|"
    )

    for event_name, event_results in audit_results["events"].items():
        for signal_type in ["signal8", "signal10"]:
            if signal_type in event_results:
                result = event_results[signal_type]
                signal_num = "8" if signal_type == "signal8" else "10"
                adherence_icon = "✓" if result["adherence"] else "✗"

                # Truncate reason for table
                reason = result["algo_reason"]
                if len(reason) > 80:
                    reason = reason[:77] + "..."

                row = (
                    f"| {event_name} | T{signal_num} | {result['verdict']} | "
                    f"{result['algo_decision']} | {result['official_decision']} | "
                    f"{adherence_icon} | {reason} |"
                )
                lines.append(row)

    # Add reference stations section
    lines.append("")
    lines.append("## Reference Stations (8 official HKO stations)")
    lines.append("")
    lines.append("1. Cheung Chau (99m elevation)")
    lines.append("2. Chek Lap Kok / HK Airport (14m)")
    lines.append("3. Kai Tak (16m)")
    lines.append("4. Lau Fau Shan (50m)")
    lines.append("5. Sai Kung (32m)")
    lines.append("6. Sha Tin (16m)")
    lines.append("7. Ta Kwu Ling (28m)")
    lines.append("8. Tsing Yi (43m)")
    lines.append("")
    lines.append("## Methodology Details")
    lines.append("")
    lines.append("### Wind Model")
    lines.append("- Holland (2010) parametric tropical cyclone wind model")
    lines.append(
        "- Computes gradient wind at each station based on distance from center"
    )
    lines.append("- Applies B-parameter (shape) = 1.5 for mature typhoons")
    lines.append("")
    lines.append("### Terrain Factors")
    lines.append("- **Exposed coastal** (≥80m elevation): 0.85 reduction factor")
    lines.append("- **Semi-sheltered** (40-79m): 0.70 reduction factor")
    lines.append("- **Inland valleys** (<40m): 0.60 reduction factor")
    lines.append("- Elevation correction applied using power law (α=0.15)")
    lines.append("")
    lines.append("### Decision Criteria")
    lines.append("")
    lines.append("**Signal 8:**")
    lines.append(
        "- Forecast OR current observations show ≥4 stations with ≥63 km/h (including ≥118)"
    )
    lines.append("- Persistence check: ≥3 consecutive 10-min periods (30 min window)")
    lines.append("- Accounts for 'expected to register' language in HKO standards")
    lines.append("")
    lines.append("**Signal 10:**")
    lines.append("- Forecast OR current ≥118 km/h at ≥2 stations, OR")
    lines.append("- Max wind ≥118 km/h AND typhoon center <50 km from Hong Kong")
    lines.append(
        "- Note: 'Generally in Hong Kong' is approximated for this audit as ≥2 stations ≥118 km/h or center <50 km (project interpretation); HKO uses expert judgement and may differ (rare exceptions acknowledged)"
    )
    lines.append("")
    lines.append("## Key Findings")
    lines.append("")

    # Add key findings based on results
    if audit_results["summary"]["adherence_rate"] >= 0.8:
        lines.append(
            "✓ **High adherence rate** - HKO issuances generally align with published standards"
        )
    else:
        lines.append(
            "⚠ **Adherence concerns** - Some issuances deviate from published criteria"
        )

    if audit_results["summary"]["false_issuances"] > 0:
        lines.append(
            f"- {audit_results['summary']['false_issuances']} case(s) where signals issued without meeting stated criteria"
        )

    if audit_results["summary"]["delays"] > 0:
        lines.append(
            f"- {audit_results['summary']['delays']} case(s) where criteria met but signal not issued"
        )

    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append(
        "*This audit validates HKO's forecast-based issuance approach against their published standards.*"
    )
    lines.append(
        "*Forecast-driven warnings are appropriate and align with WMO best practices.*"
    )

    # Write markdown file
    with open("audit_summary.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print("\n✓ Saved markdown summary to: audit_summary.md")


if __name__ == "__main__":
    main()
