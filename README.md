# 🏗️ Code-to-Architecture Agent

Automatically generate architecture documentation from your codebase using AI-powered analysis.

![Status](https://img.shields.io/badge/status-active-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Node.js](https://img.shields.io/badge/node.js-20+-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Overview

**Code-to-Architecture Agent** is a multi-agent system that analyzes JavaScript/TypeScript codebases and automatically generates:

- 📄 Architecture documentation (Markdown)
- 🔗 Dependency graphs and diagrams (Mermaid)
- 🎨 Design pattern identification
- 💾 Technology stack detection
- 🤖 Interactive Q&A about your codebase (RAG-powered)

### Key Features

✅ **AST-Based Code Analysis** - Precise parsing using Babel  
✅ **Dependency Graph** - NetworkX-powered dependency analysis  
✅ **LangGraph Orchestration** - Multi-agent workflow coordination  
✅ **Local LLM Support** - Ollama integration (no API costs)  
✅ **RAG Q&A** - Ask questions, get code-grounded answers  
✅ **Full Stack** - FastAPI backend + React frontend  
✅ **Dockerized** - Ready for deployment  

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 20+**
- **PostgreSQL 16+**
- **Ollama** (with Mistral 7B model)
- **Docker & Docker Compose** (optional, for containerized deployment)

### 1. Setup Ollama

Download and install Ollama from [ollama.ai](https://ollama.ai)

Pull the Mistral model:
```bash
ollama pull mistral
ollama serve  # Keep running in background
```

Verify Ollama is running:
```bash
curl http://localhost:11434/api/tags
```

### 2. Clone Repository

```bash
git clone https://github.com/abdu1lah26/code-to-architecture-agent.git
cd code-to-architecture-agent
```

### 3. Environment Setup

Copy the example environment file:
```bash
cp .env.example .env
```

Update `.env` with your configuration (especially database credentials):
```env
DB_USER=abdu1lah
DB_PASSWORD=your_password
DATABASE_URL=postgresql://abdu1lah:your_password@localhost:5432/code_to_arch_db
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

### 4. Start PostgreSQL

Using Docker:
```bash
docker-compose up postgres -d
```

Or install PostgreSQL locally and create the database:
```bash
createdb -U postgres code_to_arch_db
```

### 5. Install Backend Dependencies

```bash
cd backend
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 6. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 7. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Runs on http://localhost:3000
```

### 8. Access the Application

Open your browser and navigate to: **http://localhost:3000**

---

## Usage

### Analyzing a Repository

1. **Enter Repository Path**
   - Provide the local path to your JavaScript/TypeScript repository
   - Example: `D:/projects/my-app` or `/home/user/projects/my-app`

2. **Start Analysis**
   - Click "Start Analysis"
   - Monitor progress in real-time

3. **View Results**
   - **Markdown Tab**: Read the generated architecture documentation
   - **Diagram Tab**: See the Mermaid architecture diagram
   - **Q&A Tab**: Ask questions about your codebase

### Asking Questions

Once analysis is complete, switch to the **Q&A Tab** and ask questions like:

- "What is the main purpose of this codebase?"
- "How does authentication work?"
- "What design patterns are used?"
- "What are the core modules?"
- "What's the technology stack?"

Answers are grounded in your actual code with references to specific files and code snippets.

---

## Architecture

### System Overview

```text
┌─────────────────────────────────────────────────┐
│         React Frontend (TypeScript)              │
│  - Repo input form                              │
│  - Progress tracking                            │
│  - Docs viewer                                  │
│  - Interactive Q&A chat                         │
└────────────────────┬────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────┐
│          FastAPI Backend (Python)               │
│  - /api/analyze (start analysis)                │
│  - /api/status/{job_id} (track progress)        │
│  - /api/docs/{docs_id} (get documentation)      │
│  - /api/ask/{job_id} (ask questions)            │
└────────────────────┬────────────────────────────┘
                     │
          ┌──────────┼──────────┐
          │          │          │
      ┌───▼───┐  ┌───▼───┐  ┌──▼────┐
      │ Code  │  │  LLM  │  │ Embed │
      │Parser │  │ Agent │  │ Store │
      │ (AST) │  │ (RAG) │  │ (QA)  │
      └───┬───┘  └───┬───┘  └───┬───┘
          │          │          │
      ┌───▼───┐  ┌───▼─────┐    ├─ ChromaDB
      │ Graph │  │ Ollama  │    │
      │ Build │  │(Mistral)│    └─ Embeddings
      └───────┘  └─────────┘
```

### Technology Stack

**Backend:**

* FastAPI - REST API framework
* SQLAlchemy - ORM
* PostgreSQL - Metadata storage
* ChromaDB - Vector database for embeddings
* NetworkX - Graph algorithms
* LangGraph - Multi-agent orchestration
* Ollama - Local LLM inference
* Babel Parser - JavaScript/TypeScript AST parsing

**Frontend:**

* React 18 - UI framework
* TypeScript - Type safety
* Tailwind CSS - Styling
* Vite - Build tool

**Infrastructure:**

* Docker & Docker Compose - Containerization
* PostgreSQL 16 - Database
* Ollama - Local LLM

---

## Docker Deployment

### Using Docker Compose

Ensure Ollama is running first:

```bash
ollama serve
```

Start all services:

```bash
docker-compose up -d
```

View logs:

```bash
docker-compose logs -f
```

Stop services:

```bash
docker-compose down
```

Access the application:

* Frontend: `http://localhost:3000`
* Backend: `http://localhost:8000`

---

## API Documentation

### Endpoints

#### 1. Analyze Repository

**POST** `/api/analyze`

Request:

```json
{
  "repo_path": "D:/projects/my-app"
}
```

Response:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "repo_url": "D:/projects/my-app",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

#### 2. Get Job Status

**GET** `/api/status/{job_id}`

Response:

```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 45,
  "error_message": null,
  "docs_id": null
}
```

Status values: `pending`, `processing`, `completed`, `failed`

---

#### 3. Get Documentation

**GET** `/api/docs/{docs_id}`

Response:

```json
{
  "docs_id": "550e8400-e29b-41d4-a716-446655440001",
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "markdown": "# Architecture\n\n## Overview\n...",
  "mermaid_diagram": "graph TD\n  A[Controllers] --> B[Services]",
  "tech_stack": {
    "frameworks": ["Express", "React"],
    "databases": ["PostgreSQL"]
  },
  "modules": {
    "controllers": 5,
    "services": 3,
    "models": 4
  }
}
```

---

#### 4. Ask Question (Q&A)

**POST** `/api/ask/{job_id}`

Request:

```json
{
  "question": "How does authentication work?",
  "top_k": 5
}
```

Response:

```json
{
  "success": true,
  "answer": "Authentication is handled in src/middleware/auth.js using JWT tokens. The system validates tokens on every protected route...",
  "retrieved_chunks": [
    {
      "filename": "src/middleware/auth.js",
      "snippet": "function verifyJWT(token) { ... }",
      "distance": 0.15
    }
  ],
  "error": null
}
```

---

#### 5. Get Q&A History

**GET** `/api/qa-history/{job_id}`

Response:

```json
[
  {
    "question": "How does authentication work?",
    "answer": "Authentication is handled using JWT tokens...",
    "retrieved_chunks": [...],
    "created_at": "2024-01-15T10:35:00Z"
  }
]
```

---

#### 6. List Jobs

**GET** `/api/jobs?limit=20&offset=0`

Response:

```json
[
  {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "completed",
    "repo_url": "D:/projects/my-app",
    "created_at": "2024-01-15T10:30:00Z"
  }
]
```

---

#### 7. Health Check

**GET** `/health`

Response:

```json
{
  "status": "ok",
  "message": "Backend is running"
}
```

---

## Project Structure

```text
code-to-architecture-agent/
├── backend/
│   ├── app/
│   │   ├── api/              # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── parsers/          # Code parsers (JS/TS, Python)
│   │   ├── agents/           # LangGraph agents
│   │   ├── db/               # Database models & connection
│   │   ├── llm/              # LLM client (Ollama)
│   │   └── main.py           # App entry point
│   ├── tests/                # Unit & integration tests
│   ├── requirements.txt      # Python dependencies
│   ├── Dockerfile            # Docker build config
│   └── .env                  # Environment variables
├── frontend/
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── types/            # TypeScript types
│   │   ├── utils/            # Utility functions
│   │   └── App.tsx           # App entry point
│   ├── package.json          # Node dependencies
│   ├── Dockerfile            # Docker build config
│   └── .env.local            # Environment variables
├── docker-compose.yml        # Docker Compose config
├── .env.example              # Example environment file
├── README.md                 # This file
└── start-docker.sh           # Docker startup script
```

---

## Testing

### Backend Tests

```bash
cd backend

# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_js_parser.py -v

# Run with coverage
python -m pytest tests/ --cov=app
```

### Test Coverage

Current test suites:

* ✅ JavaScript/TypeScript AST parser
* ✅ Dependency graph builder
* ✅ LangGraph agent
* ✅ FastAPI endpoints
* ✅ Q&A service

---

## Performance & Scalability

### Current Limitations

* **File Count:** Tested up to 500+ files
* **Analysis Time:** ~2-5 minutes for a typical project
* **LLM Model:** Mistral 7B (optimized for speed)

### Optimization Tips

1. **Speed up analysis:**

   * Use a smaller model (Mistral 7B recommended)
   * Increase the Ollama timeout if needed
   * Filter large `node_modules` directories

2. **Improve Q&A quality:**

   * Use a larger model (Llama 2 13B) for better answers
   * Increase the `top_k` parameter for more context

3. **Scale infrastructure:**

   * PostgreSQL: Add indexes for faster queries
   * ChromaDB: Use persistent storage
   * Backend: Deploy multiple instances with a load balancer

---

## Troubleshooting

### Issue: "Ollama is not running"

**Solution:**

```bash
ollama serve
```

Wait for:

```text
Listening on 127.0.0.1:11434
```

### Issue: "Database connection failed"

**Solution:**

```bash
# Check PostgreSQL is running
psql -U code_user -d code_to_arch_db -c "SELECT 1"

# Verify DATABASE_URL in .env is correct
# Format: postgresql://user:password@host:port/database
```

### Issue: "Port 3000 already in use"

**Solution:**

```bash
# Windows
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# macOS/Linux
lsof -i :3000
kill -9 <PID>
```

### Issue: "Parser timeout"

**Solution:**

* Increase `timeout` in `backend/app/llm/ollama_client.py` (default: 300s)
* Skip large files or `node_modules` directories

---

## Future Enhancements

* [ ] GitHub repository cloning (auto-clone from URL)
* [ ] Support for more languages (Python, Go, Java, Rust)
* [ ] Web-based deployment (Railway, Render, Fly.io)
* [ ] VS Code extension
* [ ] Architecture visualization (3D graph)
* [ ] Collaborative documentation editing
* [ ] API documentation generation (OpenAPI)
* [ ] Performance profiling analysis
* [ ] Security scanning integration

---

## Contributing

This is an educational project built by Abdullah, a 3rd-year CSE student at MMMUT Gorakhpur.

Feel free to fork, modify, and learn!

---

## License

MIT License - feel free to use this project for learning and personal projects.


---

## Acknowledgments

Built with:

* **Claude API** for initial design consultation
* **LangChain & LangGraph** for agent orchestration
* **Ollama** for local LLM inference
* **FastAPI** for the REST framework
* **React** for the frontend
* **NetworkX** for graph algorithms

---

---
