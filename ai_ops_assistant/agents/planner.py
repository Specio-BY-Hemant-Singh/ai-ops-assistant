"""
Planner Agent
Converts natural language input into structured execution plan
"""
from typing import Dict, Any, List
from llm import get_llm_client
from tools import get_registry


class PlannerAgent:
    """
    Planner Agent converts user requests into step-by-step execution plans
    Uses LLM to analyze task and select appropriate tools
    """
    
    def __init__(self):
        self.llm = get_llm_client()
        self.tool_registry = get_registry()
    
    def create_plan(self, user_input: str) -> Dict[str, Any]:
        """
        Create execution plan from user input
        
        Args:
            user_input: Natural language task description
            
        Returns:
            Dictionary containing the execution plan with steps
        """
        # Get available tools description
        tools_description = self.tool_registry.get_tools_description()
        
        # Create system instruction
        system_instruction = """You are a task planning agent. Your job is to analyze user requests and create detailed execution plans.

You have access to these tools:
{tools}

Your output must be valid JSON with this exact structure:
{{
    "task": "brief description of the user's request",
    "steps": [
        {{
            "step_number": 1,
            "action": "detailed description of what to do",
            "tool": "tool_name",
            "parameters": {{
                "param1": "value1",
                "param2": "value2"
            }}
        }}
    ]
}}

Guidelines:
1. Break complex tasks into simple, sequential steps
2. Each step should use exactly one tool
3. Parameters must match the tool's expected parameters
4. Be specific with parameter values
5. Steps should be ordered logically
6. If a task doesn't need any tools, create a step with tool "none"
""".format(tools=tools_description)
        
        # Create prompt
        prompt = f"""Analyze this user request and create an execution plan:

User Request: {user_input}

Create a detailed step-by-step plan to accomplish this task. Consider:
- What information needs to be gathered?
- Which tools are needed?
- What order makes sense?
- What parameters are required?

Remember to output ONLY valid JSON matching the schema provided."""
        
        try:
            # Get structured plan from LLM
            plan = self.llm.get_json_completion(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.3
            )
            
            # Validate plan structure
            self._validate_plan(plan)
            
            plan["status"] = "success"
            return plan
            
        except Exception as e:
            return {
                "status": "error",
                "error": f"Failed to create plan: {str(e)}",
                "task": user_input,
                "steps": []
            }
    
    def _validate_plan(self, plan: Dict[str, Any]) -> None:
        """
        Validate that the plan has the correct structure
        
        Args:
            plan: Plan dictionary to validate
            
        Raises:
            ValueError: If plan structure is invalid
        """
        if "task" not in plan:
            raise ValueError("Plan missing 'task' field")
        
        if "steps" not in plan or not isinstance(plan["steps"], list):
            raise ValueError("Plan missing 'steps' list")
        
        if len(plan["steps"]) == 0:
            raise ValueError("Plan has no steps")
        
        for i, step in enumerate(plan["steps"]):
            if "step_number" not in step:
                raise ValueError(f"Step {i} missing 'step_number'")
            if "action" not in step:
                raise ValueError(f"Step {i} missing 'action'")
            if "tool" not in step:
                raise ValueError(f"Step {i} missing 'tool'")
            if "parameters" not in step:
                raise ValueError(f"Step {i} missing 'parameters'")
            
            # Validate tool exists (unless it's "none")
            tool_name = step["tool"]
            if tool_name != "none":
                try:
                    self.tool_registry.get_tool(tool_name)
                except ValueError:
                    raise ValueError(f"Step {i} references unknown tool: {tool_name}")
