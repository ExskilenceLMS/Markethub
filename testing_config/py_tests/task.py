import os
import sys
from pathlib import Path

import pytest

# Path setup: project root = three levels up from this file (testing_config/py_tests/task.py)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
exskilence_path = os.path.join(project_root, "exskilence_project")
sys.path.insert(0, exskilence_path)
os.chdir(exskilence_path)

os.environ["FLASK_ENV"] = "testing"

from app import app
from models import db

app.config["TESTING"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"


@pytest.fixture
def client():
    """Test client with a fresh in-memory database."""
    with app.test_client() as c:
        with app.app_context():
            db.create_all()
            yield c
            db.drop_all()


def test_api_health_returns_200_with_standard_success_response(client):
    """GET /api/health returns 200 and the standard success JSON envelope (Task 1 wiring)."""
    try:
        response = client.get("/api/health")
        assert response.status_code == 200
        payload = response.get_json()
        assert payload is not None
        assert payload.get("success") is True
        assert "message" in payload
        assert payload.get("data", {}).get("status") == "ok"
    except Exception as error:
        pytest.fail(f"Health endpoint standard success response check failed: {error}")


def test_task_one_layered_structure_present():
    """Task 1: required layered packages and standard response helper exist on disk."""
    try:
        root = Path(project_root) / "exskilence_project"
        required_dirs = ("routes", "services", "repositories", "models", "config")
        for name in required_dirs:
            d = root / name
            assert d.is_dir(), f"Missing directory: {name}"
            assert (d / "__init__.py").is_file(), f"Missing {name}/__init__.py"

        assert (root / "utils" / "response.py").is_file(), "Missing utils/response.py"
        assert (root / "routes" / "health.py").is_file(), "Missing routes/health.py"
        assert (root / "services" / "health_service.py").is_file(), (
            "Missing services/health_service.py"
        )
    except Exception as error:
        pytest.fail(f"Layered structure check failed: {error}")
