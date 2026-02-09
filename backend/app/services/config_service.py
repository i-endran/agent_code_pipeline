"""
Configuration Service

Reads and writes dynamic system settings from the SystemConfig DB table.
"""

import logging
from typing import Optional, Dict
from sqlalchemy.orm import Session

from app.models.system_config import SystemConfig

logger = logging.getLogger(__name__)

# Default values seeded on first startup
DEFAULTS = {
    "cleanup_interval_days": "30",
    "cleanup_enabled": "true",
}


class ConfigService:
    """Manages dynamic system configuration stored in the database."""

    def get(self, db: Session, key: str) -> Optional[str]:
        """Get a config value by key. Returns None if not found."""
        row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        return row.value if row else DEFAULTS.get(key)

    def get_int(self, db: Session, key: str, default: int = 0) -> int:
        """Get a config value as integer."""
        val = self.get(db, key)
        try:
            return int(val) if val is not None else default
        except (ValueError, TypeError):
            return default

    def get_bool(self, db: Session, key: str, default: bool = False) -> bool:
        """Get a config value as boolean."""
        val = self.get(db, key)
        if val is None:
            return default
        return val.lower() in ("true", "1", "yes")

    def set(self, db: Session, key: str, value: str) -> SystemConfig:
        """Set a config value. Creates or updates."""
        row = db.query(SystemConfig).filter(SystemConfig.key == key).first()
        if row:
            row.value = value
        else:
            row = SystemConfig(key=key, value=value)
            db.add(row)
        db.commit()
        db.refresh(row)
        logger.info(f"Config updated: {key} = {value}")
        return row

    def get_all(self, db: Session) -> Dict[str, str]:
        """Get all config values as a dict."""
        rows = db.query(SystemConfig).all()
        result = dict(DEFAULTS)  # Start with defaults
        for row in rows:
            result[row.key] = row.value
        return result

    def seed_defaults(self, db: Session):
        """Seed default values if they don't exist yet."""
        for key, value in DEFAULTS.items():
            existing = db.query(SystemConfig).filter(SystemConfig.key == key).first()
            if not existing:
                db.add(SystemConfig(key=key, value=value))
        db.commit()
        logger.info("Seeded default system config values")


config_service = ConfigService()
