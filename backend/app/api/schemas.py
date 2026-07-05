"""
Pydantic schemas for API requests/responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID

class QuestionRequest(BaseModel):
    """Request to ask a question about the code."""
    question: str = Field(..., description="Question about the codebase")
    top_k: int = Field(5, description="Number of code chunks to retrieve")

    class Config:
        example = {
            "question": "How does authentication work in this system?",
            "top_k": 5
        }


class CodeChunkInfo(BaseModel):
    """Information about a retrieved code chunk."""
    filename: str
    snippet: str
    distance: Optional[float] = None

    class Config:
        from_attributes = True


class AnswerResponse(BaseModel):
    """Response with an answer to a question."""
    success: bool
    answer: str
    retrieved_chunks: List[CodeChunkInfo] = []
    error: Optional[str] = None

    class Config:
        from_attributes = True


class QAHistoryItem(BaseModel):
    """Q&A history item."""
    question: str
    answer: str
    retrieved_chunks: Optional[list] = None
    created_at: Optional[str] = None

    class Config:
        from_attributes = True

class AnalyzeRequest(BaseModel):
    """Request to analyze a repository."""
    repo_url: Optional[str] = Field(None, description="GitHub repo URL")
    repo_path: Optional[str] = Field(None, description="Local path to repository")

    class Config:
        example = {
            "repo_url": "https://github.com/user/repo",
            "repo_path": "/path/to/repo"
        }

class JobResponse(BaseModel):
    """Response for job creation/status."""
    job_id: UUID
    status: str
    repo_url: Optional[str] = None
    created_at: str = None

    class Config:
        from_attributes = True


class StatusResponse(BaseModel):
    """Response for job status."""
    job_id: UUID
    status: str
    progress: int = 0
    error_message: Optional[str] = None
    docs_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class DocsResponse(BaseModel):
    """Response for generated documentation."""
    docs_id: UUID
    job_id: UUID
    markdown: str
    mermaid_diagram: Optional[str] = None
    tech_stack: Optional[dict] = None
    modules: Optional[dict] = None

    class Config:
        from_attributes = True