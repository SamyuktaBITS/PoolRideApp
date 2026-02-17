from __future__ import annotations
from .settings import settings


def emission_factor(vehicle_type: str) -> float:
    v = (vehicle_type or "").strip().lower()
    return float(settings.VEHICLE_TYPE_FACTORS.get(v, settings.DEFAULT_EMISSION_FACTOR_KG_PER_KM))


def estimate_co2_saved(distance_km: float, vehicle_type: str, passengers_total: int) -> float:
    """
    Very simple MVP estimate:
    - Solo emission = distance * factor
    - Shared per person = (distance * factor) / passengers_total
    - Saved per rider = solo - shared
    """
    factor = emission_factor(vehicle_type)
    solo = distance_km * factor
    shared_per_person = (distance_km * factor) / max(passengers_total, 1)
    saved = max(solo - shared_per_person, 0.0)
    return round(saved, 3)
