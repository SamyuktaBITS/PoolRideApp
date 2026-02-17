from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


def _project_root() -> Path:
    # backend/lib/settings.py -> backend/lib -> backend -> project root
    return Path(__file__).resolve().parents[2]


def _load_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _env_bool(key: str, default: bool) -> bool:
    val = os.getenv(key, "").strip().lower()
    if val in ("true", "1", "yes", "y", "on"):
        return True
    if val in ("false", "0", "no", "n", "off"):
        return False
    return default


@dataclass(frozen=True)
class Settings:
    # App
    APP_NAME: str
    ENVIRONMENT: str

    # User access
    ENABLE_CAMPUS_VERIFICATION: bool
    ALLOWED_CAMPUS_DOMAINS: List[str]
    GUEST_VERIFICATION_METHOD: str  # "otp"

    # Ride rules
    ALLOW_GUESTS_BY_DEFAULT: bool
    GUEST_DROP_POLICY: str  # "GATE_ONLY"
    DEFAULT_GATE_NAME: str

    # Emissions
    DEFAULT_EMISSION_FACTOR_KG_PER_KM: float
    VEHICLE_TYPE_FACTORS: Dict[str, float]

    # Limits
    MAX_BOOKINGS_PER_DAY: int
    MAX_CANCELLATIONS_PER_WEEK: int
    OTP_EXPIRY_MINUTES: int

    # Notifications
    ENABLE_IN_APP_NOTIFICATIONS: bool
    ENABLE_PUSH_NOTIFICATIONS: bool

    # DB
    DB_TYPE: str
    DB_PATH: str

    # Runtime flags
    DEV_MODE: bool

    @property
    def db_path_abs(self) -> Path:
        root = _project_root()
        return (root / self.DB_PATH).resolve()


def load_settings() -> Settings:
    root = _project_root()
    cfg = _load_json(root / "config" / "config.json")

    # Config values
    app_cfg = cfg.get("app", {})
    user_cfg = cfg.get("user_access", {})
    ride_cfg = cfg.get("ride_rules", {})
    emissions_cfg = cfg.get("emissions", {})
    limits_cfg = cfg.get("limits", {})
    notif_cfg = cfg.get("notifications", {})
    db_cfg = cfg.get("database", {})

    # ENV overrides
    env_environment = os.getenv("ENV", app_cfg.get("environment", "development"))
    dev_mode = _env_bool("DEV_MODE", env_environment != "production")

    db_type = os.getenv("DB_TYPE", db_cfg.get("type", "sqlite"))
    db_path = os.getenv("DB_PATH", db_cfg.get("path", "backend/data/carpool.db"))

    otp_exp = int(os.getenv("OTP_EXPIRY_MINUTES", limits_cfg.get("otp_expiry_minutes", 10)))
    max_bookings = int(os.getenv("MAX_BOOKINGS_PER_DAY", limits_cfg.get("max_bookings_per_day", 5)))
    max_cancels = int(os.getenv("MAX_CANCELLATIONS_PER_WEEK", limits_cfg.get("max_cancellations_per_week", 3)))

    return Settings(
        APP_NAME=app_cfg.get("name", "PoolRide"),
        ENVIRONMENT=env_environment,

        ENABLE_CAMPUS_VERIFICATION=bool(user_cfg.get("enable_campus_verification", True)),
        ALLOWED_CAMPUS_DOMAINS=list(user_cfg.get("allowed_campus_domains", [])),
        GUEST_VERIFICATION_METHOD=str(user_cfg.get("guest_verification_method", "otp")),

        ALLOW_GUESTS_BY_DEFAULT=bool(ride_cfg.get("allow_guests_by_default", False)),
        GUEST_DROP_POLICY=str(ride_cfg.get("guest_drop_policy", "GATE_ONLY")),
        DEFAULT_GATE_NAME=str(ride_cfg.get("default_gate_name", "Main Campus Gate")),

        DEFAULT_EMISSION_FACTOR_KG_PER_KM=float(emissions_cfg.get("default_emission_factor_kg_per_km", 0.21)),
        VEHICLE_TYPE_FACTORS=dict(emissions_cfg.get("vehicle_type_factors", {})),

        MAX_BOOKINGS_PER_DAY=max_bookings,
        MAX_CANCELLATIONS_PER_WEEK=max_cancels,
        OTP_EXPIRY_MINUTES=otp_exp,

        ENABLE_IN_APP_NOTIFICATIONS=bool(notif_cfg.get("enable_in_app_notifications", True)),
        ENABLE_PUSH_NOTIFICATIONS=bool(notif_cfg.get("enable_push_notifications", False)),

        DB_TYPE=str(db_type),
        DB_PATH=str(db_path),

        DEV_MODE=dev_mode,
    )


settings = load_settings()
