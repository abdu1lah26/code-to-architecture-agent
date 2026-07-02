"""
Prompts for architecture analysis agents.
All prompts are designed to be grounded in actual code.
"""


class ArchitecturePrompts:
    """Collection of prompts for architecture analysis."""

    @staticmethod
    def system_prompt() -> str:
        """System prompt for architecture agent."""
        return """You are an expert software architect specializing in code analysis and documentation generation.

Your role is to:
1. Analyze code structure and dependencies
2. Identify architectural patterns and layers
3. Generate clear, concise architecture documentation
4. Explain architectural decisions based on actual code
5. Always ground your analysis in the provided code snippets

IMPORTANT RULES:
- Never hallucinate or make assumptions beyond what the code shows
- Always cite specific files/functions when making claims
- Be concrete and specific, not vague
- Focus on what the code actually does, not what it should do
"""

    @staticmethod
    def analyze_structure_prompt(parsed_data: dict) -> str:
        """Prompt for analyzing code structure."""
        return f"""Analyze this code structure and provide a brief 2-3 sentence description of what this codebase does:

PARSED CODE STRUCTURE:
- Total Files: {parsed_data.get('file_count', 'unknown')}
- Imports Found: {len(parsed_data.get('imports', []))}
- Exports Found: {len(parsed_data.get('exports', []))}
- Classes Found: {len(parsed_data.get('classes', []))}
- Functions Found: {len(parsed_data.get('functions', []))}

KEY FILES (imports/exports):
{json_to_readable(parsed_data.get('key_files', []))}

TECHNOLOGY STACK (from imports):
{json_to_readable(parsed_data.get('tech_stack', {}))}

Based on this structure, what is the primary purpose of this codebase? Be specific and cite file names/frameworks.
"""

    @staticmethod
    def detect_layers_prompt(layers: dict, file_samples: dict) -> str:
        """Prompt for detecting architectural layers."""
        return f"""Analyze the following code organization and architectural layers.

DETECTED LAYERS:
{json_to_readable(layers)}

SAMPLE CODE FROM EACH LAYER:
{json_to_readable(file_samples)}

For each layer, provide:
1. Layer name and purpose
2. Key responsibilities
3. Example files and what they do

Format as a structured breakdown. Be specific about what code is in each layer."""

    @staticmethod
    def identify_patterns_prompt(classes: list, functions: list, structure: dict) -> str:
        """Prompt for identifying design patterns."""
        return f"""Identify design patterns in this code.

CLASSES:
{json_to_readable(classes[:10])}  {' ...' if len(classes) > 10 else ''}

FUNCTIONS:
{json_to_readable(functions[:10])}  {' ...' if len(functions) > 10 else ''}

CODE ORGANIZATION:
{json_to_readable(structure)}

Identify any design patterns you can see (e.g., Singleton, Factory, Observer, Service Locator, etc.).
For each pattern, explain:
1. Which classes/functions implement it
2. How it's used in the codebase
3. Why it's beneficial here

Be specific and cite actual code elements."""

    @staticmethod
    def generate_overview_prompt(
        layers: dict,
        core_modules: list,
        tech_stack: dict,
        structure_summary: str
    ) -> str:
        """Prompt for generating system overview."""
        return f"""Generate a comprehensive but concise system overview (3-4 paragraphs) for this architecture.

SYSTEM PURPOSE:
{structure_summary}

ARCHITECTURAL LAYERS:
{json_to_readable(layers)}

CORE MODULES (by importance):
{json_to_readable(core_modules[:5])}

TECHNOLOGY STACK:
{json_to_readable(tech_stack)}

Write a clear, professional system overview that:
1. Explains what the system does
2. Describes the layered architecture
3. Highlights core modules and their role
4. Mentions the tech stack
5. Is suitable for documentation (README, architecture.md)

Write in markdown format with proper headers."""

    @staticmethod
    def qa_system_prompt() -> str:
        """System prompt for Q&A agent."""
        return """You are an AI assistant specialized in answering questions about code architecture.

You have access to:
1. Code snippets from the analyzed codebase
2. Dependency information
3. Layer and module metadata

When answering questions:
1. Always cite specific files and line numbers when referencing code
2. Provide code snippets as evidence
3. Never speculate beyond what the code shows
4. Be clear and explain technical concepts in simple terms
5. If unsure, say "This information is not clearly shown in the codebase"
"""

    @staticmethod
    def qa_question_prompt(question: str, context: str) -> str:
        """Prompt for Q&A with code context."""
        return f"""Based on the following code context, answer this question:

QUESTION: {question}

CODE CONTEXT:
{context}

Provide a clear, concise answer that:
1. Directly addresses the question
2. References specific code files/functions
3. Includes relevant code snippets if helpful
4. Explains the "why" behind the implementation
"""


def json_to_readable(data) -> str:
    """Convert JSON/dict data to readable text."""
    import json
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2)[:1000]  # Truncate to 1000 chars
    return str(data)[:1000]