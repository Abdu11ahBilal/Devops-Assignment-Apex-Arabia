import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "configure_env.py"


def configure(directory, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], cwd=directory,
        capture_output=True, text=True, check=False,
    )


def test_setup_creates_private_configuration(tmp_path):
    result = configure(tmp_path)
    assert result.returncode == 0
    path = tmp_path / ".env"
    config = dict(line.split("=", 1) for line in path.read_text().splitlines())
    assert config["POSTGRES_USER"] != config["APP_DB_USER"]
    assert len(config["POSTGRES_PASSWORD"]) == 48
    assert config["POSTGRES_PASSWORD"] != config["APP_DB_PASSWORD"]
    assert config["POSTGRES_PASSWORD"] not in result.stdout
    assert path.stat().st_mode & 0o777 == 0o600


def test_setup_preserves_existing_credentials(tmp_path):
    assert configure(tmp_path).returncode == 0
    before = (tmp_path / ".env").read_text()
    assert configure(tmp_path).returncode == 0
    assert (tmp_path / ".env").read_text() == before


def test_setup_changes_only_selected_image(tmp_path):
    assert configure(tmp_path).returncode == 0
    before = (tmp_path / ".env").read_text()
    assert configure(tmp_path, "--image", "example:release").returncode == 0
    assert (tmp_path / ".env").read_text() == before + "API_IMAGE=example:release\n"


def test_setup_rejects_shared_admin_and_app_user(tmp_path):
    (tmp_path / ".env").write_text("POSTGRES_USER=apex\nAPP_DB_USER=apex\n")
    result = configure(tmp_path)
    assert result.returncode != 0
    assert "must differ" in result.stderr
