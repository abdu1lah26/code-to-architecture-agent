"""
Pydantic schemas for API requests/responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


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