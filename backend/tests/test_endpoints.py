"""Unit tests for API endpoints."""

import tempfile
import os
from fastapi.testclient import TestClient
from app.main import app
from app.db.connection import SessionLocal

client = TestClient(app)


def test_health_check():
    """Test health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_analyze_no_input():
    """Test analyze endpoint with no input."""
    response = client.post("/api/analyze", json={})
    assert response.status_code == 400


def test_analyze_invalid_path():
    """Test analyze endpoint with invalid path."""
    response = client.post("/api/analyze", json={"repo_path": "/nonexistent"})
    assert response.status_code == 404


def test_analyze_valid_path():
    """Test analyze endpoint with valid path."""
    # Create temp repo
    tmpdir = tempfile.mkdtemp()
    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)
    
    with open(os.path.join(src_dir, "main.js"), "w") as f:
        f.write("export function hello() {}")

    # Analyze it
    response = client.post("/api/analyze", json={"repo_path": tmpdir})
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "pending"

    job_id = data["job_id"]

    # Check status
    status_response = client.get(f"/api/status/{job_id}")
    assert status_response.status_code == 200

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_list_jobs():
    """Test listing jobs."""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


if __name__ == "__main__":
    test_health_check()
    print("✅ Health check test passed")
    
    test_analyze_no_input()
    print("✅ Analyze no input test passed")
    
    test_analyze_invalid_path()
    print("✅ Analyze invalid path test passed")
    
    test_analyze_valid_path()
    print("✅ Analyze valid path test passed")
    
    test_list_jobs()
    print("✅ List jobs test passed")