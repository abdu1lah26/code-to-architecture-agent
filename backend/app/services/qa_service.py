"""
Q&A service for answering questions about architecture.
Uses ChromaDB for retrieval and Ollama for generation.
"""

from uuid import UUID
from sqlalchemy.orm import Session
from app.db.chromadb_client import get_or_create_collection
from app.services.db_service import CodeChunkService, QAInteractionService
from app.llm.ollama_client import OllamaClient
from app.llm.prompts import ArchitecturePrompts
from typing import Optional, List, Dict, Any


class QAService:
    """Service for Q&A interactions."""

    def __init__(self, db: Session):
        self.db = db
        self.llm = OllamaClient()
        self.prompts = ArchitecturePrompts()

    def answer_question(self, job_id: UUID, question: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Answer a question about the codebase.

        Args:
            job_id: Analysis job ID
            question: User's question
            top_k: Number of code chunks to retrieve

        Returns:
            Dict with answer and retrieved chunks
        """
        try:
            print(f"❓ Question: {question}")

            # Get ChromaDB collection
            collection = get_or_create_collection(str(job_id))

            # Retrieve relevant code chunks
            results = collection.query(
                query_texts=[question],
                n_results=top_k
            )

            if not results or not results.get("documents"):
                return {
                    "success": False,
                    "answer": "No relevant code found for this question.",
                    "retrieved_chunks": [],
                    "error": "No matching code chunks in retrieval"
                }

            # Format retrieved chunks
            retrieved_chunks = []
            context_text = ""

            if results["documents"] and len(results["documents"]) > 0:
                for i, doc in enumerate(results["documents"][0]):
                    metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                    retrieved_chunks.append({
                        "filename": metadata.get("filename", "unknown"),
                        "snippet": doc[:200],
                        "distance": float(results["distances"][0][i]) if results.get("distances") else None,
                    })
                    context_text += f"File: {metadata.get('filename', 'unknown')}\n{doc}\n\n"

            # Generate answer using LLM
            prompt = self.prompts.qa_question_prompt(question, context_text)
            answer = self.llm.generate(prompt, temperature=0.3, max_tokens=1000)

            if not answer:
                return {
                    "success": False,
                    "answer": "Failed to generate answer.",
                    "retrieved_chunks": retrieved_chunks,
                    "error": "LLM generation failed"
                }

            # Store interaction in database
            self._store_interaction(job_id, question, answer, retrieved_chunks)

            print(f"✅ Answer generated")

            return {
                "success": True,
                "answer": answer,
                "retrieved_chunks": retrieved_chunks,
                "error": None
            }

        except Exception as e:
            error_msg = f"QA error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "answer": "An error occurred while processing your question.",
                "retrieved_chunks": [],
                "error": error_msg
            }

    def _store_interaction(self, job_id: UUID, question: str, answer: str, chunks: List[Dict]):
        """Store Q&A interaction in database."""
        try:
            qa_service = QAInteractionService()
            qa_service.create_interaction(
                db=self.db,
                job_id=job_id,
                question=question,
                answer=answer,
                retrieved_chunks=[
                    {
                        "filename": chunk.get("filename"),
                        "snippet": chunk.get("snippet"),
                        "distance": chunk.get("distance")
                    }
                    for chunk in chunks
                ]
            )
        except Exception as e:
            print(f"⚠️ Failed to store interaction: {e}")


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