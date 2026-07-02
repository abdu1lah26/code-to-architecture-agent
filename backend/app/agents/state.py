"""
LangGraph state definition for architecture analysis agent.
"""

from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field


@dataclass
class AnalysisState:
    """State for the architecture analysis agent."""

    # Input
    repo_path: str = ""
    repo_url: Optional[str] = None

    # Parsing results
    parsed_files: Dict[str, Any] = field(default_factory=dict)
    file_count: int = 0

    # Graph analysis
    graph_stats: Dict[str, Any] = field(default_factory=dict)
    core_modules: List[tuple] = field(default_factory=list)
    layers: Dict[str, List[str]] = field(default_factory=dict)
    cycles: List[List[str]] = field(default_factory=list)

    # LLM analysis results
    structure_summary: str = ""
    architecture_description: str = ""
    layer_descriptions: Dict[str, str] = field(default_factory=dict)
    patterns_identified: List[str] = field(default_factory=list)
    tech_stack: Dict[str, List[str]] = field(default_factory=dict)

    # Generated documentation
    system_overview: str = ""
    mermaid_diagram: str = ""
    module_breakdown: str = ""
    architecture_decisions: str = ""

    # Metadata
    status: str = "initialized"  # initialized, parsing, analyzing, generating, completed, failed
    error_message: Optional[str] = None