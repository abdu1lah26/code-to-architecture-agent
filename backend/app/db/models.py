"""SQLAlchemy database models."""

from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.db.connection import Base


class AnalysisJob(Base):
    """Represents a code analysis job."""
    __tablename__ = "analysis_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    repo_url = Column(String(500), nullable=False)
    repo_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="pending")  # pending, processing, completed, failed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<AnalysisJob(id={self.id}, status={self.status}, repo_url={self.repo_url})>"


class GeneratedDocs(Base):
    """Represents generated documentation for an analysis."""
    __tablename__ = "generated_docs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    markdown_content = Column(Text, nullable=False)
    mermaid_diagram = Column(Text, nullable=True)
    tech_stack = Column(JSON, nullable=True)  # {frameworks: [], databases: [], ...}
    modules = Column(JSON, nullable=True)  # {module_name: description, ...}
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<GeneratedDocs(id={self.id}, job_id={self.job_id})>"


class CodeChunk(Base):
    """Represents a chunk of code for Q&A retrieval."""
    __tablename__ = "code_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    filename = Column(String(500), nullable=True)
    chunk_text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=True)
    language = Column(String(20), nullable=True)  # 'javascript', 'python', etc.
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CodeChunk(id={self.id}, filename={self.filename})>"


class QAInteraction(Base):
    """Represents a Q&A interaction for an analysis."""
    __tablename__ = "qa_interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    retrieved_chunks = Column(JSON, nullable=True)  # metadata of code chunks used
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<QAInteraction(id={self.id}, job_id={self.job_id})>"