"""
JavaScript/TypeScript AST Parser wrapper.
Calls the Node.js Babel parser and returns parsed structure.
"""

import json
import subprocess
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Path to the Node.js parser script
PARSER_DIR = Path(__file__).parent / "js_parser"
PARSER_SCRIPT = PARSER_DIR / "parser.js"


def parse_js_file(file_path: str) -> Dict[str, Any]:
    """
    Parse a JavaScript/TypeScript file and extract its structure.
    
    Args:
        file_path: Path to the .js, .ts, .jsx, or .tsx file
    
    Returns:
        Dict with structure: {success, error, data}
    """
    if not os.path.exists(file_path):
        return {
            "success": False,
            "error": f"File not found: {file_path}",
            "data": None,
        }

    try:
        # Call Node.js parser
        result = subprocess.run(
            ["node", str(PARSER_SCRIPT), file_path],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": result.stderr,
                "data": None,
            }

        # Parse JSON output
        output = json.loads(result.stdout)
        return output

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Parser timeout for {file_path}",
            "data": None,
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": f"JSON parsing error: {e}",
            "data": None,
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "data": None,
        }


def parse_directory(directory_path: str, extensions: Optional[list] = None) -> Dict[str, Dict[str, Any]]:
    """
    Parse all JS/TS files in a directory recursively.
    
    Args:
        directory_path: Path to the directory
        extensions: List of file extensions to parse (default: ['.js', '.ts', '.jsx', '.tsx'])
    
    Returns:
        Dict mapping file paths to their parsed structure
    """
    if extensions is None:
        extensions = [".js", ".ts", ".jsx", ".tsx"]

    if not os.path.isdir(directory_path):
        return {"error": f"Directory not found: {directory_path}"}

    results = {}

    for root, dirs, files in os.walk(directory_path):
        # Skip node_modules and other common exclusions
        dirs[:] = [d for d in dirs if d not in ["node_modules", ".git", "dist", "build", ".next", "coverage"]]

        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                file_path = os.path.join(root, file)
                parsed = parse_js_file(file_path)
                results[file_path] = parsed

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python js_parser.py <file-or-directory>")
        sys.exit(1)

    path = sys.argv[1]

    if os.path.isfile(path):
        result = parse_js_file(path)
    else:
        result = parse_directory(path)

    print(json.dumps(result, indent=2))