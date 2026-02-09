import os
import shutil
import time
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from app.services.config_service import config_service
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

class CleanupService:
    """Service for periodic cleanup of temporary files and old artifacts."""
    
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.repos_dir = self.storage_path / "repos"
        self.artifacts_dir = self.storage_path / "artifacts"
        self.audit_dir = self.storage_path / "audit"
        self.temp_dir = self.storage_path / "temp"
        
        # Ensure directories exist
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def run_cleanup(self, max_age_days: int = 7):
        """
        Runs all cleanup tasks.
        
        Args:
        Args:
            max_age_days: Default max age if not in config.
        """
        # Get dynamic configuration
        db = SessionLocal()
        try:
            enabled = config_service.get_bool(db, "cleanup_enabled", True)
            if not enabled:
                logger.info("Cleanup is disabled in system config.")
                return

            # Override max_age_days from config if present
            config_days = config_service.get_int(db, "cleanup_interval_days", 0)
            if config_days > 0:
                max_age_days = config_days
        finally:
            db.close()

        logger.info(f"Starting periodic cleanup (max_age={max_age_days} days)...")
        
        self.cleanup_temp_files(max_age_days)
        self.cleanup_old_artifacts(max_age_days)
        self.cleanup_old_repos(max_age_days)
        self.cleanup_old_audit_logs(max_age_days)
        
        logger.info("Cleanup completed successfully.")

    def cleanup_temp_files(self, max_age_days: int):
        """Deletes files in the temp directory."""
        self._delete_old_files(self.temp_dir, max_age_days)

    def cleanup_old_artifacts(self, max_age_days: int):
        """Deletes old task artifact directories (patches, reviews, etc.)."""
        self._delete_old_dirs(self.artifacts_dir, max_age_days, prefix="task_")

    def cleanup_old_repos(self, max_age_days: int):
        """Prunes local repository clones that hasn't been used."""
        self._delete_old_dirs(self.repos_dir, max_age_days, prefix="repo_")

    def cleanup_old_audit_logs(self, max_age_days: int):
        """Deletes old agent state snapshots."""
        self._delete_old_dirs(self.audit_dir, max_age_days, prefix="task_")

    def _delete_old_files(self, directory: Path, max_age_days: int):
        """Helper to delete old files in a directory."""
        if not directory.exists():
            return

        now = time.time()
        cutoff = now - (max_age_days * 86400)
        
        count = 0
        for item in directory.glob("*"):
            if item.is_file() and item.stat().st_mtime < cutoff:
                try:
                    item.unlink()
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to delete {item}: {e}")
        
        if count > 0:
            logger.info(f"Deleted {count} files from {directory}")

    def _delete_old_dirs(self, directory: Path, max_age_days: int, prefix: str = ""):
        """Helper to delete old subdirectories matching a prefix."""
        if not directory.exists():
            return

        now = time.time()
        cutoff = now - (max_age_days * 86400)
        
        count = 0
        for item in directory.glob(f"{prefix}*"):
            if item.is_dir() and item.stat().st_mtime < cutoff:
                try:
                    shutil.rmtree(item)
                    count += 1
                except Exception as e:
                    logger.error(f"Failed to delete directory {item}: {e}")
        
        if count > 0:
            logger.info(f"Deleted {count} directories from {directory}")

cleanup_service = CleanupService()
