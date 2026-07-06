"""
API endpoints for code analysis.
"""

import os
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.api.schemas import AnalyzeRequest, JobResponse, StatusResponse, DocsResponse
from app.db.connection import get_db
from app.services.db_service import AnalysisJobService, GeneratedDocsService
from app.services.analysis_service import AnalysisService
from app.services.qa_service import QAService, QAInteractionService
from app.api.schemas import QuestionRequest, AnswerResponse, QAHistoryItem

router = APIRouter(prefix="/api", tags=["analysis"])

@router.post("/ask/{job_id}", response_model=AnswerResponse)
async def ask_question(
    job_id: UUID,
    request: QuestionRequest,
    db: Session = Depends(get_db)
):
    """
    Ask a question about the analyzed codebase.
    
    Returns the answer grounded in code chunks from the repository.
    """
    # Verify job exists
    job = AnalysisJobService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not complete")

    # Get answer
    qa_service = QAService(db)
    result = qa_service.answer_question(job_id, request.question, top_k=request.top_k)

    return AnswerResponse(**result)


@router.get("/qa-history/{job_id}", response_model=list[QAHistoryItem])
async def get_qa_history(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get Q&A history for a job.
    """
    # Verify job exists
    job = AnalysisJobService.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    interactions = QAInteractionService.get_interactions(db, job_id)

    return [
        QAHistoryItem(
            question=interaction.question,
            answer=interaction.answer,
            retrieved_chunks=interaction.retrieved_chunks,
            created_at=interaction.created_at.isoformat() if interaction.created_at else None
        )
        for interaction in interactions
    ]


@router.post("/analyze", response_model=JobResponse)
async def analyze_repository(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start code analysis on a repository.

    Returns a job ID to track progress.
    """
    # Validate input
    if not request.repo_path and not request.repo_url:
        raise HTTPException(status_code=400, detail="Either repo_path or repo_url required")

    repo_path = request.repo_path

    # For now, only support local paths
    if not repo_path:
        raise HTTPException(status_code=400, detail="repo_path is required (repo_url support coming soon)")

    if not os.path.isdir(repo_path):
        raise HTTPException(status_code=404, detail=f"Directory not found: {repo_path}")

    # Create job
    job = AnalysisJobService.create_job(
        db,
        repo_url=request.repo_url,
        repo_path=repo_path
    )

    # Run analysis in background
    analysis_service = AnalysisService(db)
    background_tasks.add_task(analysis_service.run_analysis, job.id, repo_path)

    return JobResponse(
        job_id=job.id,
        status=job.status,
        repo_url=job.repo_url,
        created_at=job.created_at.isoformat()
    )


@router.get("/status/{job_id}", response_model=StatusResponse)
async def get_job_status(job_id: UUID, db: Session = Depends(get_db)):
    """
    Get the status of an analysis job.
    """
    job = AnalysisJobService.get_job(db, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Get docs if completed
    docs_id = None
    if job.status == "completed":
        docs = GeneratedDocsService.get_docs_by_job(db, job_id)
        if docs:
            docs_id = docs.id

    return StatusResponse(
        job_id=job.id,
        status=job.status,
        docs_id=docs_id,
        error_message=job.error_message
    )


@router.get("/docs/{docs_id}", response_model=DocsResponse)
async def get_documentation(docs_id: UUID, db: Session = Depends(get_db)):
    """
    Get generated documentation.
    """
    docs = GeneratedDocsService.get_docs(db, docs_id)

    if not docs:
        raise HTTPException(status_code=404, detail="Documentation not found")

    return DocsResponse(
        docs_id=docs.id,
        job_id=docs.job_id,
        markdown=docs.markdown_content,
        mermaid_diagram=docs.mermaid_diagram,
        tech_stack=docs.tech_stack,
        modules=docs.modules
    )


@router.get("/jobs", response_model=list)
async def list_jobs(limit: int = 20, offset: int = 0, db: Session = Depends(get_db)):
    """
    List all analysis jobs.
    """
    jobs = AnalysisJobService.list_jobs(db, limit=limit, offset=offset)
    return [
        JobResponse(
            job_id=job.id,
            status=job.status,
            repo_url=job.repo_url,
            created_at=job.created_at.isoformat()
        )
        for job in jobs
    ]