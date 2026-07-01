"""Unit tests for Dependency Graph Builder."""

import os
import tempfile
from pathlib import Path
from app.parsers.graph_builder import DependencyGraphBuilder


def create_test_repo():
    """Create a temporary test repository with sample files."""
    tmpdir = tempfile.mkdtemp()

    # Create files
    files = {
        "src/main.js": """
import { UserService } from "./services/UserService";
import { authMiddleware } from "./middleware/auth";

export function initApp() {
  return new UserService();
}
""",
        "src/services/UserService.js": """
import { User } from "../models/User";
import { logger } from "../utils/logger";

export class UserService {
  constructor() {
    this.model = new User();
  }
}
""",
        "src/models/User.js": """
import { Database } from "../db/Database";

export class User {
  constructor() {
    this.db = new Database();
  }
}
""",
        "src/middleware/auth.js": """
export function authMiddleware(req, res, next) {
  next();
}
""",
        "src/utils/logger.js": """
export function log(message) {
  console.log(message);
}
""",
        "src/db/Database.js": """
export class Database {
  connect() {}
}
""",
    }

    for file_path, content in files.items():
        full_path = os.path.join(tmpdir, file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            f.write(content)

    return tmpdir


def test_graph_build():
    """Test building a dependency graph."""
    tmpdir = create_test_repo()

    builder = DependencyGraphBuilder()
    stats = builder.build_from_directory(tmpdir)

    assert stats["total_nodes"] > 0
    assert stats["total_edges"] > 0

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_layer_detection():
    """Test layer detection."""
    tmpdir = create_test_repo()

    builder = DependencyGraphBuilder()
    builder.build_from_directory(tmpdir)
    layers = builder.detect_layers()

    assert "services" in layers or "models" in layers or "middleware" in layers

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_core_modules():
    """Test core module detection."""
    tmpdir = create_test_repo()

    builder = DependencyGraphBuilder()
    builder.build_from_directory(tmpdir)
    core_modules = builder.get_core_modules(top_n=5)

    assert isinstance(core_modules, list)
    assert len(core_modules) > 0

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


def test_cycles_detection():
    """Test circular dependency detection."""
    tmpdir = create_test_repo()

    builder = DependencyGraphBuilder()
    builder.build_from_directory(tmpdir)
    cycles = builder.find_cycles()

    # Should be a list (even if empty)
    assert isinstance(cycles, list)

    # Cleanup
    import shutil
    shutil.rmtree(tmpdir)


if __name__ == "__main__":
    test_graph_build()
    test_layer_detection()
    test_core_modules()
    test_cycles_detection()
    print("✅ All tests passed!")