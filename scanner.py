"""
Digital Archaeologist - Git Repo Scanner

Phase 1: Scan repos, detect stalls, score resurrection viability
"""

import os
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import json


class Project:
    """Represents a discovered project"""
    
    def __init__(self, path: str):
        self.path = path
        self.name = Path(path).name
        self.last_commit = None
        self.days_stalled = None
        self.dependencies = {}
        self.score = 0
    
    def __repr__(self):
        return f"Project(name={self.name}, score={self.score}, stalled={self.days_stalled}d)"


def find_git_repos(root_path: str, max_depth: int = 3) -> List[str]:
    """
    Find all git repositories under root_path.
    """
    repos = []
    root = Path(root_path).expanduser()
    
    if not root.exists():
        return repos
    
    for item in root.rglob('.git'):
        if item.is_dir():
            repo_path = str(item.parent)
            # Check depth
            depth = len(Path(repo_path).relative_to(root).parts)
            if depth <= max_depth:
                repos.append(repo_path)
    
    return repos


def get_last_commit_date(repo_path: str) -> Optional[datetime]:
    """
    Get the date of the last commit in a git repo.
    """
    try:
        result = subprocess.run(
            ['git', '-C', repo_path, 'log', '-1', '--format=%ct'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0 and result.stdout.strip():
            timestamp = int(result.stdout.strip())
            return datetime.fromtimestamp(timestamp)
    except (subprocess.TimeoutExpired, ValueError):
        pass
    
    return None


def analyze_dependencies(repo_path: str) -> Dict:
    """
    Analyze project dependencies and their age.
    Phase 1: Simple detection of package.json / requirements.txt
    """
    deps = {
        'has_package_json': False,
        'has_requirements': False,
        'has_cargo': False,
        'count': 0,
    }
    
    package_json = Path(repo_path) / 'package.json'
    requirements = Path(repo_path) / 'requirements.txt'
    cargo = Path(repo_path) / 'Cargo.toml'
    
    if package_json.exists():
        deps['has_package_json'] = True
        try:
            with open(package_json) as f:
                data = json.load(f)
                deps['count'] = len(data.get('dependencies', {}))
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    
    if requirements.exists():
        deps['has_requirements'] = True
        try:
            with open(requirements) as f:
                deps['count'] = len([l for l in f if l.strip() and not l.startswith('#')])
        except FileNotFoundError:
            pass
    
    if cargo.exists():
        deps['has_cargo'] = True
    
    return deps


def score_resurrection(project: Project) -> int:
    """
    Score resurrection viability 0-100.
    
    Factors:
    - Recency: Projects stalled 1-3 years ago score highest (early but not ancient)
    - Dependencies: Having dependencies suggests it was non-trivial
    - Git history: Active repos are more likely to be revivable
    """
    score = 50  # Base score
    
    # Recency scoring
    if project.days_stalled:
        if 365 <= project.days_stalled <= 1095:  # 1-3 years
            score += 30  # Sweet spot
        elif project.days_stalled < 365:  # < 1 year
            score += 10  # Recently abandoned
        elif project.days_stalled < 1825:  # 3-5 years
            score += 20  # Old but revivable
        else:  # > 5 years
            score -= 10  # Ancient
    
    # Dependency scoring
    if project.dependencies.get('count', 0) > 0:
        score += 10  # Non-trivial project
    
    if project.dependencies.get('has_package_json') or project.dependencies.get('has_requirements'):
        score += 10  # Modern tech stack
    
    return max(0, min(100, score))


def scan_projects(root_path: str, depth: int = 3) -> List[Project]:
    """
    Scan directory for git repos, analyze each, score resurrection potential.
    """
    repos = find_git_repos(root_path, max_depth=depth)
    projects = []
    
    for repo_path in repos:
        project = Project(repo_path)
        
        # Get last commit
        last_commit = get_last_commit_date(repo_path)
        if last_commit:
            project.last_commit = last_commit
            project.days_stalled = (datetime.now() - last_commit).days
        
        # Analyze dependencies
        project.dependencies = analyze_dependencies(repo_path)
        
        # Score resurrection potential
        project.score = score_resurrection(project)
        
        projects.append(project)
    
    return sorted(projects, key=lambda p: p.score, reverse=True)
