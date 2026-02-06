# AI Operations Assistant - Detailed Requirements

This document outlines the functional, technical, and operational requirements for the AI Operations Assistant project, derived from the evaluation criteria and project specifications.

## 1. Functional Specifications

### 1.1 Natural Language Processing
- **Requirement**: The system must accept natural language tasks via CLI or API.
- **Acceptance Criteria**: Successfully parse tasks like "Find the top 3 Python repos on GitHub and get weather for London."
- **Priority**: High

### 1.2 Multi-Agent Orchestration
- **Requirement**: Implement a three-agent workflow (Planner, Executor, Verifier).
- **Acceptance Criteria**:
  - **Planner**: Must produce a valid JSON plan constrained by a specific schema.
  - **Executor**: Must iterate through plan steps and call tools sequentially or in parallel.
  - **Verifier**: Must check for completeness, handle retries for missing data, and format the final output.
- **Priority**: High

### 1.3 Tool Integration
- **Requirement**: Integrate at least two external APIs.
- **Acceptance Criteria**:
  - **GitHub Tool**: Support searching repositories, fetching stars, and descriptions.
  - **Weather Tool**: Support fetching current weather by city.
- **Priority**: High

### 1.4 Output Formatting
- **Requirement**: Final output must be structured, human-readable, and schema-compliant.
- **Acceptance Criteria**: Verifier ensures the final JSON response matches the defined output schema.
- **Priority**: Medium

---

## 2. Technical Constraints

### 2.1 Language & Framework
- **Requirement**: Implementation must be in Python 3.8+.
- **Requirement**: REST API must use FastAPI.
- **Priority**: High

### 2.2 LLM Usage
- **Requirement**: Use Google Gemini (or equivalent) for reasoning.
- **Constraint**: Prompts must be constrained to JSON schemas to ensure reliability.
- **Priority**: High

### 2.3 Error Handling & Resilience
- **Requirement**: Implement retry logic for API failures.
- **Requirement**: Implement graceful fallback mechanisms when only partial data is available.
- **Priority**: High

---

## 3. Performance Criteria

### 3.1 Latency
- **Requirement**: System should provide feedback for each phase (Planning, Execution, Verification).
- **Acceptance Criteria**: Total processing time for a standard two-step task should ideally be under 15 seconds.
- **Priority**: Medium

### 3.2 Reliability
- **Requirement**: 90% success rate for planning valid JSON from clear natural language instructions.
- **Priority**: Medium

---

## 4. Security Requirements

### 4.1 Secret Management
- **Requirement**: API keys (Google, GitHub, OpenWeather) must not be hardcoded.
- **Acceptance Criteria**: Use `.env` files and `python-dotenv` for configuration.
- **Priority**: High

### 4.2 Data Privacy
- **Requirement**: Ensure no sensitive user data is leaked in logs or LLM prompts.
- **Priority**: Medium

---

## 5. Integration Needs

### 5.1 API Interfaces
- **Requirement**: Provide a `/process` endpoint for task submission.
- **Requirement**: Provide a `/tools` endpoint to list available capabilities.
- **Priority**: High

### 5.2 Documentation
- **Requirement**: Auto-generated API documentation (Swagger/ReDoc) must be accessible.
- **Priority**: Medium

---

## 6. Evaluation Criteria (Metric-Based)

The project is evaluated based on the following weights:

| Category | Weight | Target |
| :--- | :--- | :--- |
| **Agent Design** | 25% | Distinct separation of concerns between agents. |
| **LLM Usage** | 20% | Schema-constrained prompts and high-quality reasoning. |
| **API Integration** | 20% | Robust handling of GitHub and Weather APIs. |
| **Code Clarity** | 15% | PEP8 compliance, docstrings, and type hints. |
| **Working Demo** | 10% | Fully functional CLI and API interfaces. |
| **Documentation** | 10% | Comprehensive README and architecture docs. |

**Passing Score**: 70/100

---

## 7. Implementation Roadmap (Prioritized)

1.  **Phase 1: Core Architecture (High)**
    - Reorganize directory structure.
    - Implement LLM Client with JSON parsing.
    - Set up Tool Registry and Base classes.

2.  **Phase 2: Agent Implementation (High)**
    - Develop Planner Agent with schema-constrained prompts.
    - Develop Executor Agent with retry logic.
    - Develop Verifier Agent with completeness checking.

3.  **Phase 3: Tool Development (High)**
    - Finalize GitHub and Weather API integrations.

4.  **Phase 4: API & CLI (Medium)**
    - Build FastAPI wrappers and interactive CLI.

5.  **Phase 5: Optimization (Low - Future)**
    - Implement caching for API responses.
    - Add cost tracking per request.
    - Enable parallel tool execution.
