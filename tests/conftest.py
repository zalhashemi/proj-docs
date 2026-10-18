import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "project-docs" / "scripts"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SCRIPTS))
collect_ignore_glob = ["fixtures/*"]  # fixture projects carry their own fake tests


@pytest.fixture
def fixture_copy(tmp_path):
    """Copy a fixture project into tmp so tests can write docs/ or git-init it."""
    def make(name: str) -> Path:
        dst = tmp_path / name
        shutil.copytree(FIXTURES / name, dst)
        return dst
    return make


@pytest.fixture
def git_repo(tmp_path):
    def make(path: Path) -> Path:
        run = lambda *a: subprocess.run(["git", "-C", str(path), *a], check=True, capture_output=True)
        run("init", "-q", "-b", "main")
        run("-c", "user.email=a@example.com", "-c", "user.name=A", "add", ".")
        run("-c", "user.email=a@example.com", "-c", "user.name=A", "commit", "-qm", "feat: initial")
        run("tag", "v0.1.0")
        run("remote", "add", "origin", "https://user:secret@example.com/acme/app.git")
        return path
    if not shutil.which("git"):
        pytest.skip("git not installed")
    return make
