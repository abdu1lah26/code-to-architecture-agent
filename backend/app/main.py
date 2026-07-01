from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.db.connection import test_connection, init_db
from app.db.chromadb_client import test_chromadb

# Lifespan events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 Starting application...")
    
    # Test & initialize PostgreSQL
    if test_connection():
        print("✅ PostgreSQL connection verified")
        init_db()
    else:
        print("⚠️ PostgreSQL not connected")
    
    # Test ChromaDB
    if test_chromadb():
        print("✅ ChromaDB ready")
    else:
        print("⚠️ ChromaDB connection failed")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application...")

app = FastAPI(
    title="Code-to-Architecture Agent",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)