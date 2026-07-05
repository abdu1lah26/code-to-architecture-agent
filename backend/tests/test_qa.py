"""Unit tests for Q&A service."""

import tempfile
import os
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient
from app.main import app
from app.db.connection import SessionLocal
from app.services.db_service import AnalysisJobService
from app.services.analysis_service import AnalysisService

client = TestClient(app)


def test_ask_question_invalid_job():
    """Test asking question for non-existent job."""
    response = client.post(
        f"/api/ask/{uuid4()}",
        json={"question": "What is this codebase?"}
    )
    assert response.status_code == 404


def test_ask_question_incomplete_job():
    """Test asking question for incomplete job."""
    db = SessionLocal()
    
    # Create a pending job
    job = AnalysisJobService.create_job(db, repo_path="/tmp/test")
    
    response = client.post(
        f"/api/ask/{job.id}",
        json={"question": "What is this codebase?"}
    )
    assert response.status_code == 400
    
    db.close()


def test_ask_question_complete_job():
    """Test asking question for completed job."""
    db = SessionLocal()
    
    # Create a test repo
    tmpdir = tempfile.mkdtemp()
    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)
    
    with open(os.path.join(src_dir, "main.js"), "w") as f:
        f.write("export function authenticate(user) { return user.token; }")
    
    # Create and run analysis
    job = AnalysisJobService.create_job(db, repo_path=tmpdir)
    analysis_service = AnalysisService(db)
    analysis_service.run_analysis(job.id, tmpdir)
    
    # Ask a question
    response = client.post(
        f"/api/ask/{job.id}",
        json={"question": "How is authentication handled?", "top_k": 3}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "retrieved_chunks" in data
    assert data["success"] == True
    
    # Cleanup
    db.close()
    import shutil
    shutil.rmtree(tmpdir)


def test_get_qa_history():
    """Test getting Q&A history."""
    db = SessionLocal()
    
    # Create a test repo and run analysis
    tmpdir = tempfile.mkdtemp()
    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)
    
    with open(os.path.join(src_dir, "main.js"), "w") as f:
        f.write("export function getData() { return {}; }")
    
    job = AnalysisJobService.create_job(db, repo_path=tmpdir)
    analysis_service = AnalysisService(db)
    analysis_service.run_analysis(job.id, tmpdir)
    
    # Ask a question
    client.post(
        f"/api/ask/{job.id}",
        json={"question": "What is the main function?"}
    )
    
    # Get history
    response = client.get(f"/api/qa-history/{job.id}")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    
    # Cleanup
    db.close()
    import shutil
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_ask_question_invalid_job()
    print("✅ Invalid job test passed")
    
    test_ask_question_incomplete_job()
    print("✅ Incomplete job test passed")
    
    test_ask_question_complete_job()
    print("✅ Complete job test passed")
    
    test_get_qa_history()
    print("✅ QA history test passed")