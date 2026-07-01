"""Unit tests for JavaScript/TypeScript parser."""

import json
import os
from pathlib import Path
from app.parsers.js_parser import parse_js_file, parse_directory


def test_parse_simple_function():
    """Test parsing a simple function."""
    test_file = Path(__file__).parent.parent / "test_sample.js"
    result = parse_js_file(str(test_file))

    assert result["success"] == True
    assert result["error"] is None
    assert result["data"] is not None
    assert "imports" in result["data"]
    assert "exports" in result["data"]


def test_parse_imports():
    """Test that imports are correctly extracted."""
    test_file = Path(__file__).parent.parent / "test_sample.js"
    result = parse_js_file(str(test_file))

    imports = result["data"]["imports"]
    assert len(imports) > 0
    assert imports[0]["source"] == "express"


def test_parse_exports():
    """Test that exports are correctly extracted."""
    test_file = Path(__file__).parent.parent / "test_sample.js"
    result = parse_js_file(str(test_file))

    exports = result["data"]["exports"]
    assert len(exports) > 0

    # Check for function export
    function_exports = [e for e in exports if e["type"] == "function"]
    assert len(function_exports) > 0

    # Check for class export
    class_exports = [e for e in exports if e["type"] == "class"]
    assert len(class_exports) > 0


def test_parse_classes():
    """Test that class declarations are extracted."""
    test_file = Path(__file__).parent.parent / "test_sample.js"
    result = parse_js_file(str(test_file))

    classes = result["data"]["classes"]
    assert len(classes) > 0
    assert classes[0]["name"] == "AuthService"


def test_parse_nonexistent_file():
    """Test parsing a non-existent file."""
    result = parse_js_file("/nonexistent/path/file.js")
    assert result["success"] == False
    assert result["error"] is not None


if __name__ == "__main__":
    test_parse_simple_function()
    test_parse_imports()
    test_parse_exports()
    test_parse_classes()
    test_parse_nonexistent_file()
    print("✅ All tests passed!")