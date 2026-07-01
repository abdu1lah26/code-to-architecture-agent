"""
Dependency Graph Builder using NetworkX.
Constructs a directed graph of code dependencies.
"""

import os
import json
from pathlib import Path
from typing import Dict, Set, Tuple, List, Optional
import networkx as nx
from app.parsers.js_parser import parse_directory, parse_js_file


class DependencyGraphBuilder:
    """Builds and analyzes dependency graphs from code."""

    def __init__(self):
        self.graph = nx.DiGraph()
        self.file_map = {}  # Maps normalized paths to actual paths
        self.parsed_files = {}  # Stores parsed results

    def _normalize_path(self, path: str) -> str:
        """Normalize path for consistent comparison."""
        return os.path.normpath(path).lower()

    def _resolve_import(
        self, import_source: str, importer_file: str, repo_root: str
    ) -> Optional[str]:
        """
        Resolve an import path to an actual file.

        Args:
            import_source: The import path (e.g., './services', 'express', '../models/User')
            importer_file: The file doing the importing
            repo_root: Root directory of the repository

        Returns:
            Absolute path to the imported file, or None if external/not found
        """
        # External packages (node_modules, built-ins)
        if not import_source.startswith("."):
            return None

        # Resolve relative import
        importer_dir = os.path.dirname(importer_file)
        resolved_path = os.path.normpath(os.path.join(importer_dir, import_source))

        # Try with different extensions
        extensions = [".js", ".ts", ".jsx", ".tsx", "/index.js", "/index.ts"]

        for ext in extensions:
            candidate = resolved_path + ext if not resolved_path.endswith(ext) else resolved_path
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

        # Try as directory with index
        if os.path.isdir(resolved_path):
            for ext in [".js", ".ts"]:
                index_file = os.path.join(resolved_path, f"index{ext}")
                if os.path.isfile(index_file):
                    return os.path.abspath(index_file)

        return None

    def add_file(self, file_path: str) -> bool:
        """
        Parse a file and add it to the graph.

        Args:
            file_path: Path to the JavaScript/TypeScript file

        Returns:
            True if successful, False otherwise
        """
        abs_path = os.path.abspath(file_path)
        norm_path = self._normalize_path(abs_path)

        # Add node
        self.graph.add_node(abs_path)
        self.file_map[norm_path] = abs_path

        # Parse file
        parsed = parse_js_file(abs_path)
        self.parsed_files[abs_path] = parsed

        if not parsed["success"]:
            return False

        return True

    def build_from_directory(self, directory: str, repo_root: Optional[str] = None) -> Dict:
        """
        Parse all JS/TS files in a directory and build dependency graph.

        Args:
            directory: Directory to scan
            repo_root: Root of the repository (for relative path resolution)

        Returns:
            Dict with graph stats
        """
        if repo_root is None:
            repo_root = directory

        # Parse all files
        parsed_files = parse_directory(directory)

        for file_path, parsed_result in parsed_files.items():
            self.add_file(file_path)

        # Build edges (dependencies)
        for file_path, parsed_result in self.parsed_files.items():
            if not parsed_result["success"]:
                continue

            imports = parsed_result["data"].get("imports", [])

            for import_item in imports:
                import_source = import_item["source"]

                # Resolve import to actual file
                resolved_target = self._resolve_import(
                    import_source, file_path, repo_root
                )

                if resolved_target and resolved_target in self.graph.nodes:
                    self.graph.add_edge(file_path, resolved_target)

        return self.get_stats()

    def get_stats(self) -> Dict:
        """Get graph statistics."""
        return {
            "total_nodes": len(self.graph.nodes),
            "total_edges": len(self.graph.edges),
            "density": nx.density(self.graph),
            "is_dag": nx.is_directed_acyclic_graph(self.graph),
        }

    def find_cycles(self) -> List[List[str]]:
        """Find circular dependencies."""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []

    def get_centrality(self) -> Dict[str, float]:
        """
        Get betweenness centrality (important nodes that connect others).
        Higher value = more important for overall structure.
        """
        return nx.betweenness_centrality(self.graph)

    def get_in_degree_centrality(self) -> Dict[str, float]:
        """Get in-degree centrality (most imported files)."""
        return nx.in_degree_centrality(self.graph)

    def get_out_degree_centrality(self) -> Dict[str, float]:
        """Get out-degree centrality (files that import the most)."""
        return nx.out_degree_centrality(self.graph)

    def get_core_modules(self, top_n: int = 10) -> List[Tuple[str, float]]:
        """
        Get the most central/important modules.

        Args:
            top_n: Number of top modules to return

        Returns:
            List of (file_path, centrality_score) tuples
        """
        centrality = self.get_centrality()
        sorted_modules = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_modules[:top_n]

    def detect_layers(self) -> Dict[str, List[str]]:
        """
        Detect architectural layers based on directory structure.

        Returns:
            Dict mapping layer names to files
        """
        layers = {
            "controllers": [],
            "services": [],
            "models": [],
            "utils": [],
            "middleware": [],
            "routes": [],
            "config": [],
            "other": [],
        }

        layer_patterns = {
            "controllers": r".*[/\\](controllers?|handlers?)[/\\]",
            "services": r".*[/\\](services?|business)[/\\]",
            "models": r".*[/\\](models?|entities?|schemas?)[/\\]",
            "middleware": r".*[/\\](middleware?)[/\\]",
            "routes": r".*[/\\](routes?|pages?)[/\\]",
            "config": r".*[/\\](config|configuration|env)[/\\]",
            "utils": r".*[/\\](utils?|helpers?|common|lib)[/\\]",
        }

        import re

        for file_path in self.graph.nodes:
            categorized = False
            for layer, pattern in layer_patterns.items():
                if re.match(pattern, file_path):
                    layers[layer].append(file_path)
                    categorized = True
                    break

            if not categorized:
                layers["other"].append(file_path)

        # Remove empty layers
        return {k: v for k, v in layers.items() if v}

    def get_graph_as_dict(self) -> Dict:
        """
        Convert graph to JSON-serializable dictionary.

        Returns:
            Dict with nodes and edges
        """
        return {
            "nodes": list(self.graph.nodes),
            "edges": list(self.graph.edges),
        }

    def export_to_json(self, output_path: str):
        """Export graph to JSON file."""
        data = {
            "stats": self.get_stats(),
            "graph": self.get_graph_as_dict(),
            "layers": self.detect_layers(),
            "core_modules": self.get_core_modules(),
            "cycles": self.find_cycles(),
        }

        with open(output_path, "w") as f:
            json.dump(data, f, indent=2, default=str)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python graph_builder.py <directory>")
        sys.exit(1)

    repo_dir = sys.argv[1]
    builder = DependencyGraphBuilder()
    stats = builder.build_from_directory(repo_dir)

    print(f"✅ Graph built: {stats}")
    print(f"📊 Layers detected: {list(builder.detect_layers().keys())}")
    print(f"🎯 Core modules: {builder.get_core_modules(top_n=5)}")

    cycles = builder.find_cycles()
    if cycles:
        print(f"⚠️ Circular dependencies found: {cycles}")