"""
Database service layer for managing analysis jobs and docs.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.models import AnalysisJob, GeneratedDocs, CodeChunk, QAInteraction
from app.agents.state import AnalysisState

class QAInteractionService:
    """Service for managing Q&A interactions."""

    @staticmethod
    def create_interaction(
        db: Session,
        job_id: UUID,
        question: str,
        answer: str,
        retrieved_chunks: Optional[list] = None
    ):
        """Create a Q&A interaction record."""
        from app.db.models import QAInteraction

        interaction = QAInteraction(
            job_id=job_id,
            question=question,
            answer=answer,
            retrieved_chunks=retrieved_chunks
        )
        db.add(interaction)
        db.commit()
        db.refresh(interaction)
        return interaction

    @staticmethod
    def get_interactions(db: Session, job_id: UUID):
        """Get all Q&A interactions for a job."""
        from app.db.models import QAInteraction

        return db.query(QAInteraction).filter(QAInteraction.job_id == job_id).all()


class AnalysisJobService:
    """Service for managing analysis jobs."""

    @staticmethod
    def create_job(db: Session, repo_url: Optional[str] = None, repo_path: Optional[str] = None) -> AnalysisJob:
        """Create a new analysis job."""
        job = AnalysisJob(
            repo_url=repo_url or repo_path,
            repo_path=repo_path,
            status="pending"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return job

    @staticmethod
    def get_job(db: Session, job_id: UUID) -> Optional[AnalysisJob]:
        """Get a job by ID."""
        return db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()

    @staticmethod
    def update_job_status(db: Session, job_id: UUID, status: str, error_message: Optional[str] = None):
        """Update job status."""
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if job:
            job.status = status
            if status == "completed":
                job.completed_at = datetime.utcnow()
            if error_message:
                job.error_message = error_message
            db.commit()

    @staticmethod
    def list_jobs(db: Session, limit: int = 20, offset: int = 0):
        """List all jobs with pagination."""
        return db.query(AnalysisJob).order_by(AnalysisJob.created_at.desc()).offset(offset).limit(limit).all()


class GeneratedDocsService:
    """Service for managing generated documentation."""

    @staticmethod
    def create_docs(
        db: Session,
        job_id: UUID,
        markdown_content: str,
        mermaid_diagram: Optional[str] = None,
        tech_stack: Optional[dict] = None,
        modules: Optional[dict] = None
    ) -> GeneratedDocs:
        """Create generated documentation for a job."""
        docs = GeneratedDocs(
            job_id=job_id,
            markdown_content=markdown_content,
            mermaid_diagram=mermaid_diagram,
            tech_stack=tech_stack,
            modules=modules
        )
        db.add(docs)
        db.commit()
        db.refresh(docs)
        return docs

    @staticmethod
    def get_docs_by_job(db: Session, job_id: UUID) -> Optional[GeneratedDocs]:
        """Get docs for a specific job."""
        return db.query(GeneratedDocs).filter(GeneratedDocs.job_id == job_id).first()

    @staticmethod
    def get_docs(db: Session, docs_id: UUID) -> Optional[GeneratedDocs]:
        """Get docs by ID."""
        return db.query(GeneratedDocs).filter(GeneratedDocs.id == docs_id).first()


class CodeChunkService:
    """Service for managing code chunks."""

    @staticmethod
    def create_chunk(
        db: Session,
        job_id: UUID,
        filename: str,
        chunk_text: str,
        chunk_index: int,
        language: str
    ) -> CodeChunk:
        """Create a code chunk."""
        chunk = CodeChunk(
            job_id=job_id,
            filename=filename,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            language=language
        )
        db.add(chunk)
        db.commit()
        db.refresh(chunk)
        return chunk

    @staticmethod
    def get_chunks_by_job(db: Session, job_id: UUID):
        """Get all chunks for a job."""
        return db.query(CodeChunk).filter(CodeChunk.job_id == job_id).all()

    @staticmethod
    def bulk_create_chunks(db: Session, job_id: UUID, chunks: list):
        """Bulk create chunks."""
        chunk_objects = [
            CodeChunk(
                job_id=job_id,
                filename=chunk.get("filename"),
                chunk_text=chunk.get("chunk_text"),
                chunk_index=chunk.get("chunk_index"),
                language=chunk.get("language")
            )
            for chunk in chunks
        ]
        db.add_all(chunk_objects)
        db.commit()