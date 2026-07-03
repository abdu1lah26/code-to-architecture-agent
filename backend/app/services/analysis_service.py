"""
Analysis service that runs the agent and saves results.
"""

import json
import os
from uuid import UUID
from sqlalchemy.orm import Session
from app.agents.architecture_agent import ArchitectureAnalysisAgent
from app.services.db_service import AnalysisJobService, GeneratedDocsService, CodeChunkService
from app.db.chromadb_client import get_or_create_collection
from app.parsers.js_parser import parse_directory


class AnalysisService:
    """Service for running code analysis."""

    def __init__(self, db: Session):
        self.db = db
        self.agent = ArchitectureAnalysisAgent()

    def run_analysis(self, job_id: UUID, repo_path: str) -> bool:
        """
        Run analysis on a repository and save results.

        Args:
            job_id: Analysis job ID
            repo_path: Path to repository

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update status to processing
            AnalysisJobService.update_job_status(self.db, job_id, "processing")

            print(f"🚀 Starting analysis for job {job_id}")
            print(f"📁 Repository: {repo_path}")

            # Run agent
            result = self.agent.run(repo_path)

            if result.status == "failed":
                AnalysisJobService.update_job_status(
                    self.db, job_id, "failed", result.error_message
                )
                return False

            # Generate markdown documentation
            markdown = self._generate_markdown(result)

            # Save to database
            docs = GeneratedDocsService.create_docs(
                self.db,
                job_id=job_id,
                markdown_content=markdown,
                mermaid_diagram=result.mermaid_diagram,
                tech_stack=result.tech_stack,
                modules={layer: len(files) for layer, files in result.layers.items()}
            )

            # Store code chunks for Q&A
            chunks = self._prepare_chunks(repo_path, job_id)
            CodeChunkService.bulk_create_chunks(self.db, job_id, chunks)

            # Store embeddings in ChromaDB
            self._store_embeddings(job_id, chunks)

            # Update status to completed
            AnalysisJobService.update_job_status(self.db, job_id, "completed")

            print(f"✅ Analysis complete for job {job_id}")
            return True

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            AnalysisJobService.update_job_status(self.db, job_id, "failed", error_msg)
            print(f"❌ {error_msg}")
            return False

    def _generate_markdown(self, state) -> str:
        """Generate markdown documentation from analysis state."""
        markdown = f"""# Architecture Documentation

## System Overview

{state.system_overview}

## Architecture Decisions

{state.architecture_decisions}

## Layers

"""
        for layer_name, files in state.layers.items():
            markdown += f"\n### {layer_name.capitalize()}\n"
            markdown += f"Files: {len(files)}\n"

        markdown += f"\n## Core Modules\n"
        for module, score in state.core_modules[:5]:
            markdown += f"- {os.path.basename(module)} (importance: {score:.2f})\n"

        if state.cycles:
            markdown += f"\n## ⚠️ Circular Dependencies\n"
            for cycle in state.cycles:
                markdown += f"- {' -> '.join([os.path.basename(p) for p in cycle])}\n"

        markdown += f"\n## Architecture Diagram\n\n```mermaid\n{state.mermaid_diagram}\n```\n"

        return markdown

    def _prepare_chunks(self, repo_path: str, job_id: UUID) -> list:
        """
        Prepare code chunks for embeddings.

        Args:
            repo_path: Path to repository
            job_id: Job ID

        Returns:
            List of chunk dictionaries
        """
        chunks = []
        parsed_files = parse_directory(repo_path)
        chunk_index = 0

        for file_path, parsed_result in parsed_files.items():
            if not parsed_result["success"]:
                continue

            # Read file content
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                # Split into chunks (1000 chars each)
                chunk_size = 1000
                for i in range(0, len(content), chunk_size):
                    chunk_text = content[i:i + chunk_size]
                    chunks.append({
                        "filename": file_path,
                        "chunk_text": chunk_text,
                        "chunk_index": chunk_index,
                        "language": "javascript"
                    })
                    chunk_index += 1

            except Exception as e:
                print(f"⚠️ Error reading {file_path}: {e}")
                continue

        return chunks

    def _store_embeddings(self, job_id: UUID, chunks: list):
        """Store code chunks in ChromaDB for Q&A retrieval."""
        try:
            collection = get_or_create_collection(str(job_id))

            for chunk in chunks:
                collection.add(
                    ids=[f"chunk_{chunk['chunk_index']}"],
                    documents=[chunk["chunk_text"]],
                    metadatas=[{
                        "filename": chunk["filename"],
                        "chunk_index": chunk["chunk_index"],
                        "language": chunk["language"]
                    }]
                )

            print(f"✅ Stored {len(chunks)} chunks in ChromaDB")

        except Exception as e:
            print(f"⚠️ Error storing embeddings: {e}")