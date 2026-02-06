"""
FastAPI Server for AI Operations Assistant
Provides REST API endpoints
"""
import os
from typing import Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from main import AIOperationsAssistant

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="AI Operations Assistant",
    description="Multi-agent AI system for task automation",
    version="1.0.0"
)

# Initialize assistant (will be done on startup)
assistant = None


class TaskRequest(BaseModel):
    """Request model for task processing"""
    task: str
    verbose: bool = False


class TaskResponse(BaseModel):
    """Response model for task results"""
    status: str
    summary: str
    completeness_score: int = None
    findings: Dict[str, Any] = None
    data: Dict[str, Any] = None
    recommendations: list = None
    error: str = None


@app.on_event("startup")
async def startup_event():
    """Initialize the assistant on startup"""
    global assistant
    
    # Check for required API key
    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY environment variable not set. "
            "Please create a .env file with your API keys."
        )
    
    print("Initializing AI Operations Assistant...")
    assistant = AIOperationsAssistant()
    print("Assistant ready!")


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "AI Operations Assistant",
        "version": "1.0.0",
        "description": "Multi-agent AI system for task automation",
        "endpoints": {
            "POST /process": "Process a natural language task",
            "GET /tools": "List available tools",
            "GET /health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "assistant_ready": assistant is not None
    }


@app.get("/tools")
async def get_tools():
    """Get information about available tools"""
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    tools = assistant.tool_registry.get_tools_dict()
    return {
        "count": len(tools),
        "tools": tools
    }


@app.post("/process", response_model=TaskResponse)
async def process_task(request: TaskRequest):
    """
    Process a natural language task
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        TaskResponse with results
    """
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    
    try:
        result = assistant.process_task(request.task, verbose=request.verbose)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")


@app.post("/process/simple")
async def process_task_simple(request: TaskRequest):
    """
    Process task and return simple text response
    
    Args:
        request: TaskRequest with task description
        
    Returns:
        Simple text summary
    """
    if assistant is None:
        raise HTTPException(status_code=503, detail="Assistant not initialized")
    
    if not request.task or not request.task.strip():
        raise HTTPException(status_code=400, detail="Task cannot be empty")
    
    try:
        summary = assistant.process_task_simple(request.task)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing task: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    
    # Run the server
    print("Starting AI Operations Assistant API Server...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs at: http://localhost:8000/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
