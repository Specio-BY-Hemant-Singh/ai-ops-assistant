# AI Operations Assistant - Project Summary

## Overview
The AI Operations Assistant is a multi-agent system designed to automate tasks by processing natural language instructions, planning execution steps, and interacting with external APIs (GitHub and OpenWeather). It follows a modular architecture where distinct agents handle planning, execution, and verification.

## Project Structure
The project has been reorganized into a modular package structure:

```
ai_ops_assistant/
├── agents/             # Agent implementations
│   ├── planner.py      # Translates user input to JSON execution plans (LLM-based)
│   ├── executor.py     # Executes plan steps using tools (Pure Python)
│   └── verifier.py     # Validates execution results and formats output (LLM-based)
├── tools/              # Tool integrations
│   ├── base_tool.py    # Abstract base class and tool registry
│   ├── github_tool.py  # GitHub API interactions
│   └── weather_tool.py # OpenWeather API interactions
├── llm/                # LLM client utilities
│   └── client.py       # Wrapper for Google Gemini API with JSON parsing
├── main.py             # CLI entry point and orchestrator
├── api.py              # REST API entry point (FastAPI)
├── requirements.txt    # Project dependencies
└── .env.example        # Configuration template
```

## Key Components

### 1. Orchestrator (`main.py`)
The `AIOperationsAssistant` class in `main.py` coordinates the entire workflow. It initializes the tool registry and manages the handoffs between the Planner, Executor, and Verifier agents.

### 2. Planner Agent
Uses Google Gemini to analyze user requests and select appropriate tools. It outputs a structured JSON execution plan containing step-by-step actions and parameters.

### 3. Executor Agent
A rule-based engine that iterates through the steps provided by the Planner. it retrieves tools from the `ToolRegistry` and executes them with the specified parameters, handling retries and errors.

### 4. Verifier Agent
Uses LLM to assess if the execution results satisfy the original user request. It generates a human-readable summary, extracts key findings, and provides a completeness score.

### 5. Tool System
A registry-based system where each tool (e.g., GitHub, Weather) inherits from a `BaseTool` class. This makes the system highly extensible, allowing new tools to be added with minimal changes to the core logic.

### 6. LLM Client
A singleton wrapper for the Google Gemini API that handles structured output generation, JSON parsing, and automatic retries with exponential backoff.

## Relationships & Data Flow
1. **User Input** is received via CLI or REST API.
2. **Planner** analyzes input + tool descriptions → generates **Plan (JSON)**.
3. **Executor** takes Plan → calls **Tools** → collects **Results (JSON)**.
4. **Verifier** takes Plan + Results → validates → generates **Final Report (JSON)**.
5. **Final Report** is returned to the user.

## System Architecture Highlights
- **Separation of Concerns**: Each agent has a single, well-defined responsibility.
- **Structured Communication**: All internal data exchange between agents uses predefined JSON schemas.
- **Robustness**: Includes retry logic for both LLM calls and tool executions.
- **Extensibility**: New tools and agents can be added easily due to the modular design.
- **Multiple Interfaces**: Supports both interactive CLI and production-ready REST API.
