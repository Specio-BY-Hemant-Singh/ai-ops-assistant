# AI Operations Assistant

A multi-agent AI system that accepts natural-language tasks, plans execution steps, calls real APIs, and returns structured results.

## 🎯 Overview

This project implements a sophisticated AI Operations Assistant using a **multi-agent architecture**:
- **Planner Agent**: Converts user input into structured execution plans
- **Executor Agent**: Executes planned steps and calls external APIs
- **Verifier Agent**: Validates results and formats final output

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Input                           │
│            "Find Python repos and get weather"          │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              PLANNER AGENT (LLM)                        │
│  • Analyzes user request                                │
│  • Selects appropriate tools                            │
│  • Creates step-by-step execution plan                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
              ┌──────────┐
              │   PLAN   │  (JSON)
              └────┬─────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────┐
│              EXECUTOR AGENT                             │
│  • Executes each step sequentially                      │
│  • Calls external APIs (GitHub, Weather, etc.)          │
│  • Handles errors and retries                           │
│  • Collects results                                     │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  RAW RESULTS   │
            └────────┬───────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              VERIFIER AGENT (LLM)                       │
│  • Validates completeness                               │
│  • Checks for missing data                              │
│  • Formats final structured output                      │
│  • Provides recommendations                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              FINAL RESULT                               │
│  • Status and completeness score                        │
│  • Human-readable summary                               │
│  • Structured data                                      │
│  • Key findings                                         │
└─────────────────────────────────────────────────────────┘
```

## ✨ Features

- ✅ **Multi-agent architecture** (Planner, Executor, Verifier)
- ✅ **LLM-powered reasoning** using Google Gemini
- ✅ **Real API integrations** (GitHub, OpenWeather)
- ✅ **Structured JSON outputs** throughout the pipeline
- ✅ **Error handling and retry logic**
- ✅ **Multiple interfaces** (CLI, REST API)
- ✅ **Extensible tool system**

## 🔧 Technology Stack

- **LLM**: Google Gemini (via AI Studio)
- **APIs**: GitHub API, OpenWeatherMap API
- **Framework**: FastAPI for REST API
- **Language**: Python 3.8+

## 📋 Prerequisites

Detailed project requirements, functional specifications, and implementation roadmap can be found in the [REQUIREMENTS.md](file:///c:/Users/heman/Downloads/truemadly/assessment/ai_ops_assistant/REQUIREMENTS.md) file.

- Python 3.8 or higher
- Google AI Studio API key ([Get one here](https://makersuite.google.com/app/apikey))
- OpenWeatherMap API key ([Get one here](https://openweathermap.org/api))
- GitHub token (optional, for higher rate limits)

## 🚀 Installation

### 1. Clone or download this repository

```bash
cd ai_ops_assistant
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
GOOGLE_API_KEY=your_google_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
GITHUB_TOKEN=your_github_token_here  # Optional
```

## 💻 Usage

### Option 1: Command Line Interface (CLI)

#### Interactive Mode

```bash
python main.py
```

This starts an interactive session where you can enter tasks:

```
> Find the top 3 Python web frameworks on GitHub
> What's the weather like in London?
> Search for machine learning repositories with over 1000 stars
```

#### Single Task Mode

```bash
python main.py "Find popular Python repositories on GitHub"
```

### Option 2: REST API

#### Start the API server

```bash
python api.py
```

The API will be available at `http://localhost:8000`

Interactive documentation: `http://localhost:8000/docs`

#### API Endpoints

**POST /process** - Process a task
```bash
curl -X POST "http://localhost:8000/process" \
  -H "Content-Type: application/json" \
  -d '{"task": "Find Python web frameworks on GitHub", "verbose": false}'
```

**GET /tools** - List available tools
```bash
curl "http://localhost:8000/tools"
```

**GET /health** - Health check
```bash
curl "http://localhost:8000/health"
```

## 📝 Example Usage

### Example 1: Simple GitHub Search

**Input:**
```
Find the top 3 Python repositories on GitHub
```

**Process:**
1. Planner creates plan to search GitHub for Python repos
2. Executor calls GitHub API
3. Verifier formats results

**Output:**
```json
{
  "status": "complete",
  "completeness_score": 100,
  "summary": "Found 3 popular Python repositories...",
  "findings": {
    "key_results": [
      "Django: 75,000+ stars",
      "Flask: 65,000+ stars",
      "FastAPI: 60,000+ stars"
    ]
  }
}
```

### Example 2: Multi-step Task

**Input:**
```
Find machine learning repositories on GitHub and tell me the weather in San Francisco
```

**Process:**
1. Planner creates 2-step plan:
   - Step 1: Search GitHub for ML repos
   - Step 2: Get weather for San Francisco
2. Executor runs both steps
3. Verifier combines and formats results

**Output:**
```json
{
  "status": "complete",
  "completeness_score": 100,
  "summary": "Found 5 ML repositories and current weather in San Francisco",
  "findings": {
    "key_results": [
      "Top ML repositories: tensorflow, pytorch, scikit-learn",
      "San Francisco weather: 18°C, Clear skies"
    ]
  },
  "data": {
    "step_1": { "repositories": [...] },
    "step_2": { "weather": {...} }
  }
}
```

## 🛠️ Project Structure

```
ai_ops_assistant/
├── agents/
│   ├── __init__.py
│   ├── planner.py          # Planner Agent (LLM-based planning)
│   ├── executor.py         # Executor Agent (tool execution)
│   └── verifier.py         # Verifier Agent (result validation)
├── tools/
│   ├── __init__.py
│   ├── base_tool.py        # Base tool class and registry
│   ├── github_tool.py      # GitHub API integration
│   └── weather_tool.py     # Weather API integration
├── llm/
│   ├── __init__.py
│   └── client.py           # Google Gemini LLM client
├── main.py                 # Main orchestrator and CLI
├── api.py                  # FastAPI REST API server
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## 🔌 Available Tools

### 1. GitHub Tool
- **Actions**: `search_repos`, `get_repo_info`, `get_user_info`
- **Parameters**:
  - `query`: Search query
  - `language`: Filter by programming language
  - `sort`: Sort by stars, forks, or updated
  - `limit`: Maximum results (default: 5)

### 2. Weather Tool
- **Actions**: `current`, `forecast`
- **Parameters**:
  - `city`: City name
  - `country`: Country code (optional)
  - `units`: metric or imperial (default: metric)

## 🧪 Testing

### Test with sample queries:

```python
# In Python or interactive mode
assistant = AIOperationsAssistant()

# Simple query
result = assistant.process_task("What's the weather in Tokyo?")

# Complex query
result = assistant.process_task(
    "Find the top 5 JavaScript frameworks on GitHub and get weather for Seattle"
)
```

### Test API endpoints:

```bash
# Test health
curl http://localhost:8000/health

# Test tools listing
curl http://localhost:8000/tools

# Test task processing
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"task": "Search for Python web frameworks"}'
```


## 🎓 Key Design Decisions

### 1. Multi-Agent Architecture
- **Separation of Concerns**: Each agent has a single, well-defined responsibility
- **No Monolithic Prompts**: Each agent uses LLM independently for its specific task
- **Modularity**: Agents can be improved or replaced independently

### 2. LLM Integration
- **Structured Outputs**: All LLM calls use JSON schemas for consistency
- **Error Handling**: Robust parsing with fallback mechanisms
- **Temperature Control**: Lower temperature (0.2-0.3) for planning/verification

### 3. Tool System
- **Extensible**: Easy to add new tools by inheriting from `BaseTool`
- **Registry Pattern**: Centralized tool management
- **Error Recovery**: Retry logic with exponential backoff

### 4. Execution Pipeline
- **Sequential Processing**: Steps execute in order with dependencies
- **Partial Success**: System continues even if some steps fail
- **Rich Logging**: Detailed progress information for debugging


## 🐛 Troubleshooting

### "GOOGLE_API_KEY not found"
- Make sure you created a `.env` file
- Verify the API key is correct
- Check the file is in the same directory as `main.py`

### "GitHub API rate limit exceeded"
- Add a `GITHUB_TOKEN` to your `.env` file
- This increases rate limits from 60 to 5000 requests/hour

### "Weather tool returns demo data"
- This is normal if `OPENWEATHER_API_KEY` is not set
- Add your API key to `.env` for real weather data

### Import errors
- Make sure you activated the virtual environment
- Run `pip install -r requirements.txt` again

## 🙋 Support

For questions or issues:
1. Check the troubleshooting section above
2. Review the code comments and docstrings
3. Test with the example queries provided

## ✨ Acknowledgments

- Google Gemini for LLM capabilities
- GitHub API for repository data
- OpenWeatherMap for weather data
- FastAPI for the excellent web framework
