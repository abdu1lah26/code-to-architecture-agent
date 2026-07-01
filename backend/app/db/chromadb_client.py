"""ChromaDB client setup for embeddings and retrieval."""

import chromadb
from chromadb.config import Settings

# Use persistent storage (in a `chroma_data` directory)
CHROMA_DATA_DIR = "./chroma_data"

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DATA_DIR)


def get_or_create_collection(job_id: str, collection_name: str = None):
    """
    Get or create a ChromaDB collection for a specific job.
    
    Args:
        job_id: Unique identifier for the analysis job
        collection_name: Optional custom name (defaults to job_id)
    
    Returns:
        ChromaDB collection object
    """
    if collection_name is None:
        collection_name = f"job_{job_id}"
    
    try:
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        print(f"✅ ChromaDB collection '{collection_name}' ready")
        return collection
    except Exception as e:
        print(f"❌ Error creating ChromaDB collection: {e}")
        raise


def delete_collection(collection_name: str):
    """Delete a ChromaDB collection."""
    try:
        client.delete_collection(name=collection_name)
        print(f"✅ ChromaDB collection '{collection_name}' deleted")
    except Exception as e:
        print(f"❌ Error deleting ChromaDB collection: {e}")


def test_chromadb():
    """Test ChromaDB connection."""
    try:
        # Try to create/get a test collection
        test_collection = client.get_or_create_collection(name="test_collection")
        
        # Add a test document
        test_collection.add(
            ids=["test_1"],
            documents=["This is a test document for ChromaDB"],
            metadatas=[{"source": "test"}]
        )
        
        # Query it back
        results = test_collection.query(
            query_texts=["test document"],
            n_results=1
        )
        
        print("✅ ChromaDB connection successful")
        
        # Cleanup
        client.delete_collection(name="test_collection")
        return True
    except Exception as e:
        print(f"❌ ChromaDB connection failed: {e}")
        return False


if __name__ == "__main__":
    test_chromadb()