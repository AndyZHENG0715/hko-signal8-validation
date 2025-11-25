"""
HKO-Compliant Signal 8/10 Issuance Algorithm
Replicates HKO's forecast-based decision logic per official standards.

Standards:
- Signal 8: ≥4 of 8 reference stations "register or are expected to register" 63-117 km/h
- Signal 10: Hurricane-force winds (≥118 km/h) "expected or blowing generally in HK"
- Basis: Forecast + observation (forecast-driven issuance ~2h before conditions)
"""

import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional

# Project interpretation note for Signal 10 (documented in README and instructions):
# "Generally in Hong Kong" is approximated here as: ≥2 stations ≥118 km/h OR center <50 km.
# HKO applies expert judgement and may differ; rare far‑field exceptions exist (e.g., Ragasa 2025).
T10_INTERPRETATION_NOTE_SHORT = "Interpretation: ≥2 stations ≥118 km/h or center <50 km; HKO expert judgement may differ"

# ============================================================================
# REFERENCE STATION COORDINATES (Official HKO 8 stations)
# ============================================================================

STATION_COORDS = {
    "Cheung Chau": {"lat": 22.2011, "lon": 114.0267, "elevation_m": 99},
    "Chek Lap Kok": {"lat": 22.3094, "lon": 113.9219, "elevation_m": 14},
    "Kai Tak": {"lat": 22.3078, "lon": 114.1814, "elevation_m": 16},
    "Lau Fau Shan": {"lat": 22.4694, "lon": 113.9864, "elevation_m": 50},
    "Sai Kung": {"lat": 22.3825, "lon": 114.2742, "elevation_m": 32},
    "Sha Tin": {"lat": 22.4033, "lon": 114.1956, "elevation_m": 16},
    "Ta Kwu Ling": {"lat": 22.5306, "lon": 114.1508, "elevation_m": 28},
    "Tsing Yi": {"lat": 22.3456, "lon": 114.1014, "elevation_m": 43},
}

# Hong Kong Observatory location (for reference)
HKO_COORDS = {"lat": 22.3019, "lon": 114.1742}

# ============================================================================
# GEOSPATIAL UTILITIES
# ============================================================================


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate great circle distance between two points in kilometers.

    Args:
        lat1, lon1: First point (degrees)
        lat2, lon2: Second point (degrees)

    Returns:
        Distance in kilometers
    """
    R = 6371.0  # Earth radius in km

    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)

    a = (
        np.sin(dlat / 2) ** 2
        + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    )
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

    return R * c


def distance_to_point(
    center_lat: float, center_lon: float, point_lat: float, point_lon: float
) -> float:
    """Calculate distance from typhoon center to a point."""
    return haversine(center_lat, center_lon, point_lat, point_lon)


# ============================================================================
# PARAMETRIC WIND MODEL (Holland 2010)
# ============================================================================


def holland_wind_model(
    r_km: float, vmax_kmh: float, rmax_km: float, lat: float, center_lat: float
) -> float:
    """
    Compute gradient wind speed at radius r using Holland (2010) parametric model.

    Args:
        r_km: Distance from typhoon center (km)
        vmax_kmh: Maximum sustained wind speed (km/h)
        rmax_km: Radius of maximum wind (km)
        lat: Latitude of target point (degrees)
        center_lat: Latitude of typhoon center (degrees)

    Returns:
        Gradient wind speed in km/h (10-min mean)
    """
    if r_km < 0.1:
        return vmax_kmh  # At center

    # Convert to m/s for calculations
    vmax_ms = vmax_kmh / 3.6
    r_m = r_km * 1000
    rmax_m = rmax_km * 1000

    # Holland B parameter (shape parameter)
    # Typical range: 1.0-2.5; use 1.5 for mature typhoons
    B = 1.5

    # Coriolis parameter at typhoon center
    f = 2 * 7.2921e-5 * np.sin(np.radians(center_lat))

    # Holland (2010) wind profile
    if r_m <= rmax_m:
        # Inside radius of maximum wind (accelerating)
        ratio = r_m / rmax_m
        v_gradient = vmax_ms * ratio
    else:
        # Outside radius of maximum wind (decaying)
        ratio = rmax_m / r_m
        exponent = -B
        v_gradient = vmax_ms * (ratio**B) * np.exp(1 - ratio**B)

    # Account for asymmetry (right vs left of track)
    # Simplified: assume uniform for now (can add motion asymmetry later)

    # Convert back to km/h
    return v_gradient * 3.6


def apply_terrain_factor(
    gradient_wind_kmh: float, elevation_m: float, exposure: str = "auto"
) -> float:
    """
    Apply terrain reduction factor to convert gradient wind to 10m surface wind.

    Args:
        gradient_wind_kmh: Gradient wind speed (km/h)
        elevation_m: Station elevation above sea level (m)
        exposure: "exposed", "semi-sheltered", "inland" or "auto"

    Returns:
        Surface wind speed at 10m height (km/h)
    """
    # Determine exposure based on elevation if auto
    if exposure == "auto":
        if elevation_m >= 80:  # High elevation = exposed coastal
            exposure = "exposed"
        elif elevation_m >= 40:  # Medium = semi-sheltered
            exposure = "semi-sheltered"
        else:  # Low elevation = inland valleys
            exposure = "inland"

    # Terrain reduction factors (from WMO guidelines)
    factors = {
        "exposed": 0.85,  # Coastal headlands, offshore islands
        "semi-sheltered": 0.70,  # Urban areas, partial shelter
        "inland": 0.60,  # Valleys, heavily sheltered
    }

    factor = factors.get(exposure, 0.70)

    # Apply elevation correction (wind increases with height in surface layer)
    # Power law: v(z) = v(10m) * (z/10)^α, where α ≈ 0.15 for open terrain
    if elevation_m > 10:
        elevation_factor = (elevation_m / 10) ** 0.15
        factor *= elevation_factor

    return gradient_wind_kmh * factor


# ============================================================================
# FORECAST WIND COMPUTATION
# ============================================================================


def forecast_station_winds(
    center_lat: float,
    center_lon: float,
    vmax_kmh: float,
    rmax_km: float,
    stations: Dict = STATION_COORDS,
) -> Dict[str, float]:
    """
    For each reference station, compute expected 10-min mean wind speed.

    Args:
        center_lat, center_lon: Typhoon center position
        vmax_kmh: Maximum sustained wind (km/h)
        rmax_km: Radius of maximum wind (km)
        stations: Dictionary of station coordinates

    Returns:
        Dictionary mapping station name to forecast wind speed (km/h)
    """
    forecast_winds = {}

    for name, coords in stations.items():
        # Calculate distance from typhoon center to station
        distance_km = distance_to_point(
            center_lat, center_lon, coords["lat"], coords["lon"]
        )

        # Compute gradient wind using Holland model
        gradient_wind = holland_wind_model(
            distance_km, vmax_kmh, rmax_km, coords["lat"], center_lat
        )

        # Apply terrain reduction factor based on station elevation
        surface_wind = apply_terrain_factor(gradient_wind, coords["elevation_m"])

        forecast_winds[name] = surface_wind

    return forecast_winds


def check_persistence(
    track_forecast: List[Dict],
    vmax_kmh: float,
    rmax_km: float,
    stations: Dict,
    min_stations: int = 4,
    min_periods: int = 3,
) -> bool:
    """
    Check if forecast shows persistent wind conditions (≥4 stations for ≥3 periods).

    Args:
        track_forecast: List of forecast positions [{time, lat, lon, vmax}, ...]
        vmax_kmh: Current maximum wind
        rmax_km: Radius of maximum wind
        stations: Station coordinates
        min_stations: Minimum stations that must exceed threshold
        min_periods: Minimum consecutive 10-min periods

    Returns:
        True if persistence criteria met
    """
    if len(track_forecast) < min_periods:
        return False

    consecutive_count = 0

    for forecast_point in track_forecast[:6]:  # Check next 60 minutes (6 periods)
        # Use forecast vmax if provided, else use current
        fc_vmax = forecast_point.get("vmax_kmh", vmax_kmh)

        winds = forecast_station_winds(
            forecast_point["lat"], forecast_point["lon"], fc_vmax, rmax_km, stations
        )

        # Count stations ≥63 km/h
        qualifying_count = sum(1 for w in winds.values() if w >= 63)

        if qualifying_count >= min_stations:
            consecutive_count += 1
            if consecutive_count >= min_periods:
                return True
        else:
            consecutive_count = 0  # Reset if not consecutive

    return False


# ============================================================================
# HKO DECISION LOGIC
# ============================================================================


def hko_signal8_decision(
    forecast_bulletin: Dict,
    current_obs: Dict[str, float],
    stations: Dict = STATION_COORDS,
) -> Tuple[str, str, List[str]]:
    """
    Replicate HKO's Signal 8 decision logic.

    Standard: Issue when ≥4 of 8 stations "register or are expected to register"
    sustained winds 63-117 km/h AND wind condition is expected to persist.

    Args:
        forecast_bulletin: {center_lat, center_lon, vmax_kmh, rmax_km, track_forecast}
        current_obs: Dictionary of current observed winds {station: wind_kmh}
        stations: Reference station coordinates

    Returns:
        Tuple of (decision, reason, qualifying_stations)
        decision: "ISSUE" or "DONT_ISSUE"
    """
    # Get forecast winds for each station
    forecast_winds = forecast_station_winds(
        forecast_bulletin["center_lat"],
        forecast_bulletin["center_lon"],
        forecast_bulletin["vmax_kmh"],
        forecast_bulletin["rmax_km"],
        stations,
    )

    # Count stations meeting Signal 8 criteria (≥63 km/h). Note: Stations ≥118 km/h
    # still count toward the "at least gale force" condition; T10 is handled separately.
    forecast_signal8 = {s: w for s, w in forecast_winds.items() if w >= 63}
    current_signal8 = {s: w for s, w in current_obs.items() if w >= 63}

    forecast_count = len(forecast_signal8)
    current_count = len(current_signal8)

    # HKO standard: "register or are EXPECTED to register" (either/or)
    total_qualifying = set(list(forecast_signal8.keys()) + list(current_signal8.keys()))
    max_count = max(forecast_count, current_count)

    if max_count >= 4:
        # Check persistence requirement
        has_persistence = check_persistence(
            forecast_bulletin.get("track_forecast", []),
            forecast_bulletin["vmax_kmh"],
            forecast_bulletin["rmax_km"],
            stations,
        )

        if has_persistence:
            qualifying = list(total_qualifying)
            reason = (
                f"Forecast: {forecast_count} stations ≥63 km/h, "
                f"Current: {current_count} stations, "
                f"Persistence: ≥3 periods confirmed"
            )
            return ("ISSUE", reason, qualifying)
        else:
            reason = (
                f"Forecast: {forecast_count} stations ≥63 km/h, "
                f"Current: {current_count} stations, "
                f"Persistence: NOT confirmed (transient conditions)"
            )
            return ("DONT_ISSUE", reason, [])

    reason = (
        f"Forecast: {forecast_count} stations, "
        f"Current: {current_count} stations (need ≥4)"
    )
    return ("DONT_ISSUE", reason, [])


def hko_signal10_decision(
    forecast_bulletin: Dict,
    current_obs: Dict[str, float],
    stations: Dict = STATION_COORDS,
) -> Tuple[str, str, List[str]]:
    """
    Replicate HKO's Signal 10 decision logic.

    Standard: Issue when hurricane-force winds (≥118 km/h) "expected or blowing
    generally in Hong Kong near sea level".

    Args:
        forecast_bulletin: Typhoon forecast data
        current_obs: Current observed winds
        stations: Reference station coordinates

    Returns:
        Tuple of (decision, reason, qualifying_stations)
    """
    # Get forecast winds
    forecast_winds = forecast_station_winds(
        forecast_bulletin["center_lat"],
        forecast_bulletin["center_lon"],
        forecast_bulletin["vmax_kmh"],
        forecast_bulletin["rmax_km"],
        stations,
    )

    # Count stations with hurricane-force winds (≥118 km/h)
    forecast_hurricane = {s: w for s, w in forecast_winds.items() if w >= 118}
    current_hurricane = {s: w for s, w in current_obs.items() if w >= 118}

    forecast_count = len(forecast_hurricane)
    current_count = len(current_hurricane)
    max_forecast_wind = max(forecast_winds.values()) if forecast_winds else 0
    max_current_wind = max(current_obs.values()) if current_obs else 0

    # Distance from center to HKO
    distance_km = distance_to_point(
        forecast_bulletin["center_lat"],
        forecast_bulletin["center_lon"],
        HKO_COORDS["lat"],
        HKO_COORDS["lon"],
    )

    # "Generally in Hong Kong" = multiple stations OR very close center
    if (forecast_count >= 2) or (max_forecast_wind >= 118 and distance_km < 50):
        qualifying = list(forecast_hurricane.keys())
        reason = (
            f"Hurricane force expected: {forecast_count} stations ≥118 km/h, "
            f"max {max_forecast_wind:.0f} km/h, center {distance_km:.0f} km from HK | "
            f"{T10_INTERPRETATION_NOTE_SHORT}"
        )
        return ("ISSUE", reason, qualifying)

    if (current_count >= 2) or (max_current_wind >= 118 and distance_km < 50):
        qualifying = list(current_hurricane.keys())
        reason = (
            f"Hurricane force observed: {current_count} stations ≥118 km/h, "
            f"max {max_current_wind:.0f} km/h | {T10_INTERPRETATION_NOTE_SHORT}"
        )
        return ("ISSUE", reason, qualifying)

    reason = (
        f"Max forecast: {max_forecast_wind:.0f} km/h, "
        f"Max current: {max_current_wind:.0f} km/h, "
        f"Hurricane stations: {max(forecast_count, current_count)}/2 needed | "
        f"{T10_INTERPRETATION_NOTE_SHORT}"
    )
    return ("DONT_ISSUE", reason, [])


# ============================================================================
# AUDIT FUNCTIONS
# ============================================================================


def audit_event(
    event_name: str,
    forecast_bulletin: Dict,
    current_obs: Dict[str, float],
    official_issuance: Dict,
    signal_level: int = 8,
) -> Dict:
    """
    Compare HKO-compliant algorithm decision vs official HKO issuance.

    Args:
        event_name: Name of typhoon event
        forecast_bulletin: Forecast data at decision time
        current_obs: Observed winds at decision time
        official_issuance: {signal8_issued, signal10_issued, time}
        signal_level: 8 or 10

    Returns:
        Audit verdict dictionary
    """
    if signal_level == 8:
        algo_decision, algo_reason, algo_stations = hko_signal8_decision(
            forecast_bulletin, current_obs, STATION_COORDS
        )
        official_issued = official_issuance.get("signal8_issued", False)
        signal_name = "Signal 8"
    else:
        algo_decision, algo_reason, algo_stations = hko_signal10_decision(
            forecast_bulletin, current_obs, STATION_COORDS
        )
        official_issued = official_issuance.get("signal10_issued", False)
        signal_name = "Signal 10"

    # Determine adherence verdict
    if algo_decision == "ISSUE" and official_issued:
        verdict = "ADHERENT"
        explanation = f"Both algorithm and HKO issued {signal_name}. Standards met."
    elif algo_decision == "DONT_ISSUE" and not official_issued:
        verdict = "ADHERENT"
        explanation = f"Both algorithm and HKO correctly did not issue {signal_name}."
    elif algo_decision == "DONT_ISSUE" and official_issued:
        verdict = "FALSE_ISSUANCE"
        explanation = f"HKO issued {signal_name} but algorithm criteria not met."
    else:  # algo_decision == "ISSUE" and not official_issued
        verdict = "DELAYED"
        explanation = f"Algorithm criteria met but HKO did not issue {signal_name}."

    return {
        "event": event_name,
        "signal_level": signal_level,
        "verdict": verdict,
        "adherence": (verdict == "ADHERENT"),
        "algo_decision": algo_decision,
        "algo_reason": algo_reason,
        "qualifying_stations": algo_stations,
        "official_decision": "ISSUED" if official_issued else "NOT_ISSUED",
        "official_time": official_issuance.get("time"),
        "explanation": explanation,
    }


def generate_audit_report(events: Dict) -> Dict:
    """
    Generate comprehensive audit report for all events.

    Args:
        events: Dictionary of event data

    Returns:
        Structured audit report
    """
    report = {
        "audit_timestamp": datetime.now().isoformat(),
        "methodology": {
            "wind_model": "Holland (2010) parametric model",
            "terrain_factors": {
                "exposed_coastal": 0.85,
                "semi_sheltered": 0.70,
                "inland_valleys": 0.60,
            },
            # Note: Signal 8 counts stations with at least gale-force winds (≥63 km/h),
            # and stations ≥118 km/h also count toward the ≥63 criterion. Persistence window ≈30 min.
            "signal8_criteria": "≥4 of 8 stations ≥63 km/h (including ≥118) for ≥3 periods (~30 min)",
            "signal10_criteria": "≥118 km/h generally in HK (≥2 stations OR center <50km)",
        },
        "events": {},
        "summary": {},
    }

    adherent_count = 0
    total_count = 0

    for event_name, event_data in events.items():
        event_results = {}

        # Audit Signal 8
        if "signal8" in event_data:
            s8_result = audit_event(
                event_name,
                event_data["signal8"]["forecast_bulletin"],
                event_data["signal8"]["current_obs"],
                event_data["signal8"]["official"],
                signal_level=8,
            )
            event_results["signal8"] = s8_result
            if s8_result["adherence"]:
                adherent_count += 1
            total_count += 1

        # Audit Signal 10
        if "signal10" in event_data:
            s10_result = audit_event(
                event_name,
                event_data["signal10"]["forecast_bulletin"],
                event_data["signal10"]["current_obs"],
                event_data["signal10"]["official"],
                signal_level=10,
            )
            event_results["signal10"] = s10_result
            if s10_result["adherence"]:
                adherent_count += 1
            total_count += 1

        report["events"][event_name] = event_results

    report["summary"] = {
        "total_decisions": total_count,
        "adherent_decisions": adherent_count,
        "adherence_rate": adherent_count / total_count if total_count > 0 else 0,
        "false_issuances": sum(
            1
            for e in report["events"].values()
            for s in e.values()
            if s["verdict"] == "FALSE_ISSUANCE"
        ),
        "delays": sum(
            1
            for e in report["events"].values()
            for s in e.values()
            if s["verdict"] == "DELAYED"
        ),
    }

    return report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    # Example: Simulate Yagi Signal 8 decision
    print("=" * 70)
    print("HKO-Compliant Signal 8/10 Issuance Algorithm")
    print("=" * 70)

    # Example forecast bulletin (2h before official Signal 8)
    example_bulletin = {
        "center_lat": 22.3,
        "center_lon": 113.5,
        "vmax_kmh": 175,
        "rmax_km": 40,
        "track_forecast": [
            {"time": "18:00", "lat": 22.25, "lon": 113.7, "vmax_kmh": 170},
            {"time": "18:10", "lat": 22.22, "lon": 113.8, "vmax_kmh": 168},
            {"time": "18:20", "lat": 22.20, "lon": 113.9, "vmax_kmh": 165},
            {"time": "18:30", "lat": 22.18, "lon": 114.0, "vmax_kmh": 163},
        ],
    }

    # Example current observations
    example_obs = {
        "Cheung Chau": 55,
        "Chek Lap Kok": 48,
        "Kai Tak": 42,
        "Lau Fau Shan": 38,
        "Sai Kung": 45,
        "Sha Tin": 32,
        "Ta Kwu Ling": 28,
        "Tsing Yi": 35,
    }

    print("\nForecast Bulletin:")
    print(
        f"  Center: {example_bulletin['center_lat']}°N, {example_bulletin['center_lon']}°E"
    )
    print(f"  Max Wind: {example_bulletin['vmax_kmh']} km/h")
    print(f"  RMW: {example_bulletin['rmax_km']} km")

    # Compute forecast winds
    forecast_winds = forecast_station_winds(
        example_bulletin["center_lat"],
        example_bulletin["center_lon"],
        example_bulletin["vmax_kmh"],
        example_bulletin["rmax_km"],
    )

    print("\nForecast Winds at Reference Stations:")
    for station, wind in sorted(
        forecast_winds.items(), key=lambda x: x[1], reverse=True
    ):
        distance = distance_to_point(
            example_bulletin["center_lat"],
            example_bulletin["center_lon"],
            STATION_COORDS[station]["lat"],
            STATION_COORDS[station]["lon"],
        )
        marker = "✓" if wind >= 63 else " "
        print(
            f"  {marker} {station:15s}: {wind:5.1f} km/h (distance: {distance:5.1f} km)"
        )

    # Signal 8 decision
    decision, reason, qualifying = hko_signal8_decision(example_bulletin, example_obs)

    print(f"\nSignal 8 Decision: {decision}")
    print(f"Reason: {reason}")
    if qualifying:
        print(f"Qualifying Stations: {', '.join(qualifying)}")

    print("\n" + "=" * 70)
