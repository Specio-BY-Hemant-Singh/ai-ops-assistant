"""
Executor Agent
Executes steps from the plan and calls appropriate tools
"""
import time
from typing import Dict, Any, List
from tools import get_registry


class ExecutorAgent:
    """
    Executor Agent executes the planned steps
    Calls tools with appropriate parameters and handles errors
    """
    
    def __init__(self):
        self.tool_registry = get_registry()
    
    def execute_plan(self, plan: Dict[str, Any], max_retries: int = 2) -> Dict[str, Any]:
        """
        Execute all steps in the plan
        
        Args:
            plan: Execution plan from PlannerAgent
            max_retries: Maximum retries for failed steps
            
        Returns:
            Dictionary containing execution results for all steps
        """
        if plan.get("status") == "error":
            return {
                "status": "error",
                "error": "Cannot execute plan with errors",
                "plan_error": plan.get("error"),
                "results": []
            }
        
        steps = plan.get("steps", [])
        results = []
        
        for step in steps:
            step_number = step.get("step_number", 0)
            tool_name = step.get("tool")
            action = step.get("action")
            parameters = step.get("parameters", {})
            
            print(f"\n[Executor] Executing Step {step_number}: {action}")
            print(f"[Executor] Tool: {tool_name}")
            print(f"[Executor] Parameters: {parameters}")
            
            # Execute step with retries
            step_result = self._execute_step_with_retry(
                step_number=step_number,
                tool_name=tool_name,
                action=action,
                parameters=parameters,
                max_retries=max_retries
            )
            
            results.append(step_result)
            
            # If step failed critically, stop execution
            if not step_result.get("success") and not step_result.get("partial_success"):
                print(f"[Executor] Step {step_number} failed critically, stopping execution")
                break
        
        return {
            "status": "success",
            "task": plan.get("task"),
            "total_steps": len(steps),
            "executed_steps": len(results),
            "results": results
        }
    
    def _execute_step_with_retry(
        self,
        step_number: int,
        tool_name: str,
        action: str,
        parameters: Dict[str, Any],
        max_retries: int
    ) -> Dict[str, Any]:
        """
        Execute a single step with retry logic
        
        Args:
            step_number: Step number
            tool_name: Name of tool to use
            action: Description of action
            parameters: Tool parameters
            max_retries: Maximum number of retries
            
        Returns:
            Step execution result
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    print(f"[Executor] Retry {attempt}/{max_retries} for step {step_number}")
                    time.sleep(2 ** attempt)  # Exponential backoff
                
                # Handle "none" tool (informational steps)
                if tool_name == "none":
                    return {
                        "step_number": step_number,
                        "action": action,
                        "tool": tool_name,
                        "success": True,
                        "result": {
                            "message": "Informational step, no tool execution required"
                        }
                    }
                
                # Get and execute tool
                tool = self.tool_registry.get_tool(tool_name)
                result = tool.execute(**parameters)
                
                # Check if execution was successful
                if result.get("success"):
                    print(f"[Executor] Step {step_number} completed successfully")
                    return {
                        "step_number": step_number,
                        "action": action,
                        "tool": tool_name,
                        "parameters": parameters,
                        "success": True,
                        "result": result
                    }
                else:
                    last_error = result.get("error", "Unknown error")
                    print(f"[Executor] Step {step_number} failed: {last_error}")
                    
            except ValueError as e:
                # Tool not found - critical error, don't retry
                return {
                    "step_number": step_number,
                    "action": action,
                    "tool": tool_name,
                    "parameters": parameters,
                    "success": False,
                    "error": f"Tool not found: {str(e)}"
                }
                
            except Exception as e:
                last_error = str(e)
                print(f"[Executor] Step {step_number} error: {last_error}")
        
        # All retries failed
        return {
            "step_number": step_number,
            "action": action,
            "tool": tool_name,
            "parameters": parameters,
            "success": False,
            "partial_success": False,
            "error": f"Failed after {max_retries} retries: {last_error}"
        }
    
    def get_execution_summary(self, execution_result: Dict[str, Any]) -> str:
        """
        Get human-readable summary of execution
        
        Args:
            execution_result: Result from execute_plan
            
        Returns:
            Summary string
        """
        if execution_result.get("status") == "error":
            return f"Execution failed: {execution_result.get('error')}"
        
        total = execution_result.get("total_steps", 0)
        executed = execution_result.get("executed_steps", 0)
        results = execution_result.get("results", [])
        
        successful = sum(1 for r in results if r.get("success"))
        failed = executed - successful
        
        summary = f"Executed {executed}/{total} steps\n"
        summary += f"Successful: {successful}, Failed: {failed}\n"
        
        return summary
