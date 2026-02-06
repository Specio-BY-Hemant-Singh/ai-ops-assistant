# AI Operations Assistant - Architecture Documentation

## System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         USER INPUT                          │
│              Natural Language Task Description              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                             │
│              (AIOperationsAssistant)                        │
│                                                             │
│  Coordinates the three-agent workflow:                      │
│  1. Call Planner → Get Plan                                 │
│  2. Call Executor → Execute Plan                            │
│  3. Call Verifier → Verify & Format                         │
└────────────────────────┬────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌────────┐     ┌─────────┐    ┌──────────┐
    │PLANNER │     │EXECUTOR │    │VERIFIER  │
    │ AGENT  │────▶│  AGENT  │───▶│  AGENT   │
    └────────┘     └─────────┘    └──────────┘
         │               │               │
         │               │               │
    Uses LLM      Calls Tools      Uses LLM
         │               │               │
         ▼               ▼               ▼
    JSON Plan     API Results    Final Output
```

## Component Details

### 1. Planner Agent (`agents/planner.py`)

**Purpose:** Convert natural language into structured execution plan

**LLM Usage:** YES ✅
- Uses Google Gemini to analyze user intent
- Generates structured JSON plan
- Temperature: 0.3 (for consistency)

**Input:**
- User's natural language task
- Available tools description

**Output:**
```json
{
  "task": "description",
  "status": "success",
  "steps": [
    {
      "step_number": 1,
      "action": "what to do",
      "tool": "tool_name",
      "parameters": {"key": "value"}
    }
  ]
}
```

**Key Features:**
- Tool selection based on task analysis
- Parameter extraction from natural language
- Sequential step planning
- Validation of plan structure

**Not a Monolithic Prompt:**
- Focused solely on planning
- Separate from execution logic
- Distinct from verification logic

---

### 2. Executor Agent (`agents/executor.py`)

**Purpose:** Execute the planned steps and call external APIs

**LLM Usage:** NO ❌
- Pure execution engine
- No reasoning or decision making
- Follows plan exactly

**Input:**
- JSON plan from Planner
- Max retry count

**Output:**
```json
{
  "status": "success",
  "total_steps": 3,
  "executed_steps": 3,
  "results": [
    {
      "step_number": 1,
      "success": true,
      "result": {...}
    }
  ]
}
```

**Key Features:**
- Sequential step execution
- Tool registry lookup
- Retry logic with exponential backoff
- Error handling and recovery
- Partial success support

**Workflow:**
1. Iterate through plan steps
2. Get tool from registry
3. Execute tool with parameters
4. Collect results
5. Handle failures gracefully

---

### 3. Verifier Agent (`agents/verifier.py`)

**Purpose:** Validate results and create final formatted output

**LLM Usage:** YES ✅
- Uses Google Gemini to assess completeness
- Generates human-readable summaries
- Temperature: 0.2 (for consistency)

**Input:**
- Original plan
- Execution results

**Output:**
```json
{
  "status": "complete|partial|incomplete",
  "completeness_score": 0-100,
  "summary": "human-readable summary",
  "findings": {
    "key_results": ["..."],
    "data_quality": "...",
    "missing_information": ["..."]
  },
  "recommendations": ["..."],
  "data": {...}
}
```

**Key Features:**
- Result completeness checking
- Missing data identification
- Quality assessment
- Summary generation
- Recommendation creation
- Fallback mode if LLM fails

**Not a Monolithic Prompt:**
- Focused solely on verification
- Separate from planning logic
- Distinct from execution logic

---

## Tool System

### Tool Registry (`tools/base_tool.py`)

```
┌─────────────────────────────────┐
│       Tool Registry             │
│                                 │
│  register(tool)                 │
│  get_tool(name)                 │
│  get_all_tools()                │
│  get_tools_description()        │
└─────────────────────────────────┘
              │
              │ manages
              ▼
    ┌─────────────────┐
    │   BaseTool      │
    │   (Abstract)    │
    ├─────────────────┤
    │ + name          │
    │ + description   │
    │ + parameters    │
    │ + execute()     │
    └─────────────────┘
              △
              │ inherits
      ┌───────┴────────┐
      │                │
┌─────────────┐  ┌─────────────┐
│ GitHubTool  │  │ WeatherTool │
├─────────────┤  ├─────────────┤
│ • search    │  │ • current   │
│ • get_repo  │  │ • forecast  │
│ • get_user  │  └─────────────┘
└─────────────┘
```

### Adding New Tools

1. Create class inheriting from `BaseTool`
2. Implement required properties: `name`, `description`, `parameters`
3. Implement `execute(**kwargs)` method
4. Register in `tools/__init__.py`

Example:
```python
class NewTool(BaseTool):
    @property
    def name(self) -> str:
        return "new_tool"
    
    @property
    def description(self) -> str:
        return "What this tool does"
    
    @property
    def parameters(self) -> Dict[str, str]:
        return {"param1": "description"}
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "data": ...}
```

---

## LLM Integration

### LLM Client (`llm/client.py`)

```
┌─────────────────────────────────────┐
│         LLM Client                  │
│    (Google Gemini Wrapper)          │
├─────────────────────────────────────┤
│                                     │
│  get_completion(prompt, system)     │
│  • Basic text completion            │
│  • Retry logic                      │
│  • Error handling                   │
│                                     │
│  get_json_completion(prompt)        │
│  • Structured JSON output           │
│  • JSON parsing                     │
│  • Schema validation                │
│                                     │
│  parse_json_response(text)          │
│  • Markdown cleanup                 │
│  • JSON extraction                  │
│  • Error recovery                   │
└─────────────────────────────────────┘
```

**Key Features:**
- Singleton pattern for efficiency
- Automatic retry with exponential backoff
- JSON parsing with markdown handling
- Temperature control
- System instruction support

**Usage in Planner:**
```python
plan = llm.get_json_completion(
    prompt=task_analysis_prompt,
    system_instruction=planning_schema,
    temperature=0.3
)
```

**Usage in Verifier:**
```python
verification = llm.get_json_completion(
    prompt=results_analysis_prompt,
    system_instruction=verification_schema,
    temperature=0.2
)
```

---

## Data Flow

### Complete Execution Flow

```
1. User Input
   │
   ▼
2. Orchestrator.process_task()
   │
   ├─▶ Initialize tools registry
   │
   ├─▶ PHASE 1: PLANNING
   │   │
   │   ▼
   │   PlannerAgent.create_plan()
   │   ├─ Get tools description
   │   ├─ Build LLM prompt
   │   ├─ Call Gemini API
   │   ├─ Parse JSON response
   │   └─ Validate plan structure
   │
   ├─▶ PHASE 2: EXECUTION
   │   │
   │   ▼
   │   ExecutorAgent.execute_plan()
   │   ├─ For each step:
   │   │  ├─ Get tool from registry
   │   │  ├─ Execute with retries
   │   │  └─ Collect results
   │   └─ Return all results
   │
   └─▶ PHASE 3: VERIFICATION
       │
       ▼
       VerifierAgent.verify_and_format()
       ├─ Check completeness
       ├─ Build LLM prompt
       ├─ Call Gemini API
       ├─ Parse verification
       └─ Format final output
   │
   ▼
3. Final Result
```

---

## Error Handling Strategy

### Executor Retry Logic
```python
for attempt in range(max_retries + 1):
    try:
        result = tool.execute(**params)
        if result["success"]:
            return result
    except Exception as e:
        if attempt < max_retries:
            sleep(2 ** attempt)  # Exponential backoff
        else:
            return error_result
```

### Verifier Fallback
```python
try:
    verification = llm.get_json_completion(...)
except Exception as e:
    # Create basic verification without LLM
    return fallback_verification()
```

### Graceful Degradation
- Tools can return partial results
- Missing API keys trigger demo mode
- LLM failures use fallback formatting
- Individual step failures don't stop execution

---

## Interfaces

### 1. CLI Interface (`main.py`)

**Interactive Mode:**
```bash
$ python main.py
> Find Python repos
[Processing...]
```

**Single Command:**
```bash
$ python main.py "task description"
```

### 2. REST API (`api.py`)

**Endpoints:**
- `GET /` - API information
- `GET /health` - Health check
- `GET /tools` - List tools
- `POST /process` - Process task
- `POST /process/simple` - Simple text response

**FastAPI Features:**
- Auto-generated docs at `/docs`
- Request validation with Pydantic
- Error handling middleware
- Async support

---

## Scalability Considerations

### Current Implementation
- Sequential step execution
- Synchronous API calls
- Single LLM instance

### Future Enhancements
1. **Parallel Execution**: Independent steps run concurrently
2. **Caching**: Cache API responses to reduce calls
3. **Load Balancing**: Multiple LLM instances
4. **Streaming**: Stream results as they become available
5. **Database**: Persist results and history

---

## Security & Best Practices

### API Key Management
- Environment variables only
- Never commit `.env` files
- Example file provided (`.env.example`)

### Input Validation
- Pydantic models for API requests
- Plan structure validation
- Parameter type checking

### Error Information
- Detailed errors in development
- Generic errors in production
- No API key exposure in logs

### Rate Limiting
- Respect API rate limits
- Exponential backoff on retries
- Demo mode when APIs unavailable

---

## Testing Strategy

### Unit Tests (Future)
- Test each agent independently
- Mock LLM responses
- Mock API calls
- Validate JSON schemas

### Integration Tests (Future)
- Test full pipeline
- Real API calls (with test keys)
- Edge cases and error scenarios

### Current Testing
- Manual testing via CLI
- Demo script with example outputs
- API endpoint testing with curl

---

## Performance Metrics

### Typical Execution Times
- Planner: 2-3 seconds (LLM)
- Executor: 1-5 seconds per step (APIs)
- Verifier: 2-3 seconds (LLM)
- **Total**: 5-15 seconds (depends on steps)

### Resource Usage
- Memory: ~100-200 MB
- CPU: Minimal (I/O bound)
- Network: Depends on API calls

---

## Extension Points

### Add New Agent
1. Create agent class
2. Define interface
3. Integrate in orchestrator
4. Update documentation

### Add New Tool
1. Inherit from BaseTool
2. Implement required methods
3. Register in tool system
4. Update Planner's tool knowledge

### Add New Interface
1. Create interface file
2. Import orchestrator
3. Call process_task()
4. Format output appropriately

### Add New LLM Provider
1. Create provider client
2. Implement same interface
3. Update configuration
4. Test compatibility
