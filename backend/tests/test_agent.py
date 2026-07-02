"""Unit tests for architecture analysis agent."""

import tempfile
import os
from app.agents.architecture_agent import ArchitectureAnalysisAgent
from app.llm.ollama_client import OllamaClient


def test_ollama_connection():
    """Test Ollama is running."""
    client = OllamaClient()
    assert client.health_check(), "Ollama server is not running"


def test_agent_initialization():
    """Test agent initializes correctly."""
    agent = ArchitectureAnalysisAgent()
    assert agent.llm is not None
    assert agent.workflow is not None


def test_agent_on_sample_repo():
    """Test agent on a sample repository."""
    # Create temp repo
    tmpdir = tempfile.mkdtemp()
    
    # Create a simple file
    src_dir = os.path.join(tmpdir, "src")
    os.makedirs(src_dir)
    
    with open(os.path.join(src_dir, "main.js"), "w") as f:
        f.write("""
export function hello() {
  console.log("Hello");
}
""")
    
    # Run agent
    agent = ArchitectureAnalysisAgent()
    result = agent.run(tmpdir)
    
    assert result.status in ["completed", "analyzing", "parsing"]
    assert result.file_count > 0
    
    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_ollama_connection()
    print("✅ Ollama connection test passed")
    
    test_agent_initialization()
    print("✅ Agent initialization test passed")
    
    test_agent_on_sample_repo()
    print("✅ Agent on sample repo test passed")