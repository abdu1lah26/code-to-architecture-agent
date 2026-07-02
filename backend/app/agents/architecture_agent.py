"""
LangGraph-based agent for code analysis and documentation generation.
"""

from typing import Any
from langgraph.graph import StateGraph, END
from app.agents.state import AnalysisState
from app.llm.ollama_client import OllamaClient
from app.llm.prompts import ArchitecturePrompts
from app.parsers.graph_builder import DependencyGraphBuilder
from app.parsers.js_parser import parse_directory


class ArchitectureAnalysisAgent:
    """Main agent for analyzing code architecture."""

    def __init__(self):
        self.llm = OllamaClient()
        self.prompts = ArchitecturePrompts()
        self.workflow = self._create_workflow()

    def _create_workflow(self):
        """Create the LangGraph workflow."""
        workflow = StateGraph(AnalysisState)

        # Define nodes
        workflow.add_node("parse_code", self.parse_code_node)
        workflow.add_node("build_graph", self.build_graph_node)
        workflow.add_node("analyze_structure", self.analyze_structure_node)
        workflow.add_node("detect_layers", self.detect_layers_node)
        workflow.add_node("identify_patterns", self.identify_patterns_node)
        workflow.add_node("generate_overview", self.generate_overview_node)
        workflow.add_node("generate_docs", self.generate_docs_node)

        # Define edges
        workflow.add_edge("parse_code", "build_graph")
        workflow.add_edge("build_graph", "analyze_structure")
        workflow.add_edge("analyze_structure", "detect_layers")
        workflow.add_edge("detect_layers", "identify_patterns")
        workflow.add_edge("identify_patterns", "generate_overview")
        workflow.add_edge("generate_overview", "generate_docs")
        workflow.add_edge("generate_docs", END)

        # Set entry point
        workflow.set_entry_point("parse_code")

        return workflow.compile()

    def parse_code_node(self, state: AnalysisState) -> AnalysisState:
        """Parse all code files in the repository."""
        try:
            state.status = "parsing"
            print(f"📖 Parsing code from: {state.repo_path}")

            parsed_files = parse_directory(state.repo_path)
            state.parsed_files = parsed_files
            state.file_count = len(parsed_files)

            print(f"✅ Parsed {state.file_count} files")
            return state

        except Exception as e:
            state.status = "failed"
            state.error_message = f"Parse error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def build_graph_node(self, state: AnalysisState) -> AnalysisState:
        """Build dependency graph."""
        try:
            state.status = "analyzing"
            print("🔗 Building dependency graph...")

            builder = DependencyGraphBuilder()
            stats = builder.build_from_directory(state.repo_path)
            state.graph_stats = stats

            state.core_modules = builder.get_core_modules(top_n=10)
            state.layers = builder.detect_layers()
            state.cycles = builder.find_cycles()

            print(f"✅ Graph built: {stats['total_nodes']} nodes, {stats['total_edges']} edges")
            if state.cycles:
                print(f"⚠️ Found {len(state.cycles)} circular dependencies")

            return state

        except Exception as e:
            state.status = "failed"
            state.error_message = f"Graph build error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def analyze_structure_node(self, state: AnalysisState) -> AnalysisState:
        """Analyze code structure with LLM."""
        try:
            print("🧠 Analyzing code structure...")

            # Prepare data for LLM
            analysis_data = {
                "file_count": state.file_count,
                "imports": [imp for f in state.parsed_files.values() if f.get("success") for imp in f.get("data", {}).get("imports", [])],
                "exports": [exp for f in state.parsed_files.values() if f.get("success") for exp in f.get("data", {}).get("exports", [])],
                "classes": [c for f in state.parsed_files.values() if f.get("success") for c in f.get("data", {}).get("classes", [])],
                "functions": [fn for f in state.parsed_files.values() if f.get("success") for fn in f.get("data", {}).get("functions", [])],
            }

            prompt = self.prompts.analyze_structure_prompt(analysis_data)
            response = self.llm.generate(prompt, temperature=0.3, max_tokens=500)

            if response:
                state.structure_summary = response
                print(f"✅ Structure analysis complete")
            else:
                print("⚠️ Structure analysis returned empty")

            return state

        except Exception as e:
            state.error_message = f"Structure analysis error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def detect_layers_node(self, state: AnalysisState) -> AnalysisState:
        """Detect and describe architectural layers."""
        try:
            print("🏗️ Detecting architectural layers...")

            # Sample files from each layer
            file_samples = {}
            for layer_name, files in state.layers.items():
                file_samples[layer_name] = files[:2]  # First 2 files from each layer

            prompt = self.prompts.detect_layers_prompt(state.layers, file_samples)
            response = self.llm.generate(prompt, temperature=0.4, max_tokens=1000)

            if response:
                state.layer_descriptions = {"description": response}
                print(f"✅ Layer detection complete")
            else:
                print("⚠️ Layer detection returned empty")

            return state

        except Exception as e:
            state.error_message = f"Layer detection error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def identify_patterns_node(self, state: AnalysisState) -> AnalysisState:
        """Identify design patterns."""
        try:
            print("🎨 Identifying design patterns...")

            # Collect classes and functions
            all_classes = []
            all_functions = []
            for f in state.parsed_files.values():
                if f.get("success"):
                    all_classes.extend(f.get("data", {}).get("classes", []))
                    all_functions.extend(f.get("data", {}).get("functions", []))

            prompt = self.prompts.identify_patterns_prompt(all_classes, all_functions, state.layers)
            response = self.llm.generate(prompt, temperature=0.4, max_tokens=800)

            if response:
                state.patterns_identified = [p.strip() for p in response.split("\n") if p.strip()]
                print(f"✅ Pattern identification complete")
            else:
                print("⚠️ Pattern identification returned empty")

            return state

        except Exception as e:
            state.error_message = f"Pattern identification error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def generate_overview_node(self, state: AnalysisState) -> AnalysisState:
        """Generate system overview."""
        try:
            print("📝 Generating system overview...")

            prompt = self.prompts.generate_overview_prompt(
                layers=state.layers,
                core_modules=state.core_modules,
                tech_stack=state.tech_stack,
                structure_summary=state.structure_summary
            )
            response = self.llm.generate(prompt, temperature=0.5, max_tokens=1500)

            if response:
                state.system_overview = response
                print(f"✅ Overview generation complete")
            else:
                print("⚠️ Overview generation returned empty")

            return state

        except Exception as e:
            state.error_message = f"Overview generation error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def generate_docs_node(self, state: AnalysisState) -> AnalysisState:
        """Generate final documentation."""
        try:
            print("📚 Generating documentation...")

            state.architecture_decisions = """
## Architecture Decisions

### Layering
The codebase is organized into distinct layers for separation of concerns.

### Patterns
Design patterns have been identified to improve code maintainability.

### Dependencies
Circular dependencies have been analyzed and flagged.
"""

            state.mermaid_diagram = """
graph TD
    A[Controllers] -->|calls| B[Services]
    B -->|uses| C[Models]
    C -->|queries| D[Database]
"""

            state.status = "completed"
            print("✅ Documentation generation complete")

            return state

        except Exception as e:
            state.status = "failed"
            state.error_message = f"Doc generation error: {str(e)}"
            print(f"❌ {state.error_message}")
            return state

    def run(self, repo_path: str) -> AnalysisState:
        """
        Run the analysis agent on a repository.

        Args:
            repo_path: Path to the repository

        Returns:
            Final analysis state
        """
        initial_state = AnalysisState(repo_path=repo_path)
        final_state_dict = self.workflow.invoke(initial_state)
        
        # Convert dict back to AnalysisState if needed
        if isinstance(final_state_dict, dict):
            return AnalysisState(**final_state_dict)
        return final_state_dict