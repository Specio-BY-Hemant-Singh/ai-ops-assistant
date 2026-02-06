"""
Verifier Agent
Validates execution results, checks completeness, and formats final output
"""
from typing import Dict, Any, List
from llm import get_llm_client


class VerifierAgent:
    """
    Verifier Agent validates execution results and creates final output
    Uses LLM to check completeness and format results
    """
    
    def __init__(self):
        self.llm = get_llm_client()
    
    def verify_and_format(
        self,
        plan: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Verify execution results and create formatted final output
        
        Args:
            plan: Original execution plan
            execution_result: Results from ExecutorAgent
            
        Returns:
            Verified and formatted final output
        """
        print("\n[Verifier] Verifying execution results...")
        
        # Check if execution failed
        if execution_result.get("status") == "error":
            return {
                "status": "error",
                "error": "Execution failed",
                "details": execution_result.get("error"),
                "summary": "Unable to complete the task due to execution errors"
            }
        
        # Extract results from each step
        step_results = execution_result.get("results", [])
        
        # Check for failed steps
        failed_steps = [r for r in step_results if not r.get("success")]
        successful_steps = [r for r in step_results if r.get("success")]
        
        if len(successful_steps) == 0:
            return {
                "status": "failed",
                "error": "All steps failed",
                "summary": "Unable to complete any part of the task",
                "failed_steps": failed_steps
            }
        
        # Prepare data for LLM verification
        task = plan.get("task", "Unknown task")
        
        # Create verification prompt
        verification_result = self._verify_with_llm(
            task=task,
            plan=plan,
            step_results=step_results,
            successful_steps=successful_steps,
            failed_steps=failed_steps
        )
        
        return verification_result
    
    def _verify_with_llm(
        self,
        task: str,
        plan: Dict[str, Any],
        step_results: List[Dict[str, Any]],
        successful_steps: List[Dict[str, Any]],
        failed_steps: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Use LLM to verify results and create final formatted output
        
        Args:
            task: Original user task
            plan: Execution plan
            step_results: All step results
            successful_steps: Successfully executed steps
            failed_steps: Failed steps
            
        Returns:
            Verified and formatted output
        """
        system_instruction = """You are a results verification agent. Your job is to:
1. Analyze execution results from multiple steps
2. Check if the original task was completed successfully
3. Identify any missing or incomplete data
4. Create a comprehensive, user-friendly summary

Your output must be valid JSON with this structure:
{
    "status": "complete" | "partial" | "incomplete",
    "completeness_score": 0-100,
    "summary": "Human-readable summary of results",
    "findings": {
        "key_results": ["list of main findings"],
        "data_quality": "assessment of data quality",
        "missing_information": ["list of missing data, if any"]
    },
    "recommendations": ["suggestions if task was incomplete"],
    "data": {
        // Structured data from successful steps
    }
}"""
        
        # Prepare step results summary
        steps_summary = []
        for step in step_results:
            steps_summary.append({
                "step_number": step.get("step_number"),
                "action": step.get("action"),
                "tool": step.get("tool"),
                "success": step.get("success"),
                "result_preview": self._extract_result_preview(step.get("result", {}))
            })
        
        # Create full results data
        full_results = {}
        for step in successful_steps:
            step_num = step.get("step_number")
            full_results[f"step_{step_num}"] = step.get("result", {})
        
        prompt = f"""Verify the execution results for this task:

Original Task: {task}

Planned Steps: {len(plan.get('steps', []))}
Executed Steps: {len(step_results)}
Successful Steps: {len(successful_steps)}
Failed Steps: {len(failed_steps)}

Step Results Summary:
{self._format_steps_summary(steps_summary)}

Full Results Data:
{self._format_full_results(full_results)}

Analyze these results and provide a comprehensive verification report.
Focus on:
- Was the original task completed?
- Is the data complete and accurate?
- What are the key findings?
- What, if anything, is missing?

Output valid JSON only."""
        
        try:
            # Get structured verification from LLM
            verification = self.llm.get_json_completion(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.2
            )
            
            # Add raw data to verification result
            verification["raw_data"] = full_results
            verification["failed_steps"] = failed_steps if failed_steps else None
            
            return verification
            
        except Exception as e:
            # Fallback if LLM verification fails
            return self._create_fallback_verification(
                task=task,
                successful_steps=successful_steps,
                failed_steps=failed_steps,
                full_results=full_results,
                error=str(e)
            )
    
    def _extract_result_preview(self, result: Dict[str, Any]) -> str:
        """Extract a brief preview of result data"""
        if not result:
            return "No data"
        
        if "error" in result:
            return f"Error: {result['error']}"
        
        # Extract key information based on result type
        if "repositories" in result:
            repos = result["repositories"]
            return f"Found {len(repos)} repositories"
        elif "weather" in result:
            weather = result["weather"]
            return f"Temperature: {weather.get('temperature')}°, {weather.get('condition')}"
        elif "user" in result:
            user = result["user"]
            return f"User: {user.get('username')}"
        else:
            return "Data available"
    
    def _format_steps_summary(self, steps: List[Dict[str, Any]]) -> str:
        """Format steps summary for LLM"""
        lines = []
        for step in steps:
            status = "✓" if step.get("success") else "✗"
            lines.append(
                f"{status} Step {step.get('step_number')}: {step.get('action')} "
                f"[{step.get('tool')}] - {step.get('result_preview')}"
            )
        return "\n".join(lines)
    
    def _format_full_results(self, results: Dict[str, Any]) -> str:
        """Format full results data for LLM (with truncation)"""
        import json
        formatted = json.dumps(results, indent=2)
        
        # Truncate if too long
        if len(formatted) > 2000:
            formatted = formatted[:2000] + "\n... (truncated)"
        
        return formatted
    
    def _create_fallback_verification(
        self,
        task: str,
        successful_steps: List[Dict[str, Any]],
        failed_steps: List[Dict[str, Any]],
        full_results: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """
        Create fallback verification when LLM verification fails
        
        Args:
            task: Original task
            successful_steps: Successful step results
            failed_steps: Failed step results
            full_results: Collected results data
            error: LLM error message
            
        Returns:
            Basic verification result
        """
        total_steps = len(successful_steps) + len(failed_steps)
        completeness = (len(successful_steps) / total_steps * 100) if total_steps > 0 else 0
        
        status = "complete" if len(failed_steps) == 0 else "partial"
        
        return {
            "status": status,
            "completeness_score": completeness,
            "summary": f"Completed {len(successful_steps)} out of {total_steps} steps for: {task}",
            "findings": {
                "key_results": [f"Executed {len(successful_steps)} successful steps"],
                "data_quality": "Unable to verify automatically",
                "missing_information": [f"Verification failed: {error}"]
            },
            "recommendations": ["Review raw data for complete information"],
            "data": full_results,
            "raw_data": full_results,
            "failed_steps": failed_steps if failed_steps else None,
            "verification_error": error
        }
