import os
import shutil
import subprocess
from pathlib import Path
import logging
from typing import List

logger = logging.getLogger(__name__)

class RepoService:
    def __init__(self, storage_path: str = "./storage"):
        self.storage_path = Path(storage_path)
        self.repos_dir = self.storage_path / "repos"
        self.repos_dir.mkdir(parents=True, exist_ok=True)

    def get_repo_path(self, repo_id: int) -> Path:
        """Returns the local path for a repository ID."""
        return self.repos_dir / f"repo_{repo_id}"

    def clone_repo(self, repo_id: int, source_url: str) -> str:
        """Clones a repository into a task-specific directory."""
        target_path = self.get_repo_path(repo_id)
        
        if target_path.exists():
            logger.info(f"Repo {repo_id} already exists at {target_path}. Updating...")
            try:
                subprocess.run(["git", "fetch", "--all"], cwd=target_path, check=True)
                return str(target_path)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to update repo {repo_id}: {e}")
                shutil.rmtree(target_path)

        logger.info(f"Cloning {source_url} to {target_path}...")
        try:
            subprocess.run(["git", "clone", source_url, str(target_path)], check=True)
            return str(target_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to clone repo {repo_id}: {e}")
            raise RuntimeError(f"Git clone failed: {e}")

    def create_branch(self, repo_path: str, branch_name: str, base_branch: str = "main"):
        """Creates a new branch for a specific task and prunes others."""
        path = Path(repo_path)
        logger.info(f"Creating branch {branch_name} in {path}...")
        
        try:
            # 1. Fetch latest
            subprocess.run(["git", "fetch", "origin"], cwd=path, check=True)
            
            # 2. Prune branches not related to current task (very aggressive)
            # This is complex to do safely, for now we just ensure we are on the base branch
            subprocess.run(["git", "checkout", base_branch], cwd=path, check=True)
            subprocess.run(["git", "pull", "origin", base_branch], cwd=path, check=True)
            
            # 3. Create and checkout new branch
            subprocess.run(["git", "checkout", "-b", branch_name], cwd=path, check=True)
            
            # 4. Prune local branches that aren't base or current
            result = subprocess.run(["git", "branch"], cwd=path, capture_output=True, text=True)
            for branch in result.stdout.split('\n'):
                branch = branch.strip().replace('*', '').strip()
                if branch and branch not in [base_branch, branch_name, "master", "develop"]:
                    subprocess.run(["git", "branch", "-D", branch], cwd=path)
                    
        except subprocess.CalledProcessError as e:
            logger.error(f"Branch operation failed in {repo_path}: {e}")
            raise RuntimeError(f"Git branch operation failed: {e}")

    def prune_unrelated_branches(self, repo_path: str, current_branch: str, base_branch: str = "main"):
        """Utility to clean up branches."""
        path = Path(repo_path)
        result = subprocess.run(["git", "branch"], cwd=path, capture_output=True, text=True)
        for branch in result.stdout.split('\n'):
            branch = branch.strip().replace('*', '').strip()
            if branch and branch not in [base_branch, current_branch, "master", "develop"]:
                subprocess.run(["git", "branch", "-D", branch], cwd=path)

repo_service = RepoService()
