"""
Main Orchestrator
Coordinates Planner, Executor, and Verifier agents
"""
import os
import json
from typing import Dict, Any
from dotenv import load_dotenv

from agents import PlannerAgent, ExecutorAgent, VerifierAgent
from tools import initialize_tools


class AIOperationsAssistant:
    """
    Main orchestrator for the AI Operations Assistant
    Coordinates the multi-agent workflow
    """
    
    def __init__(self):
        """Initialize the assistant and all agents"""
        # Load environment variables
        load_dotenv()
        
        # Initialize tools registry
        print("[System] Initializing tools...")
        self.tool_registry = initialize_tools()
        
        # Initialize agents
        print("[System] Initializing agents...")
        self.planner = PlannerAgent()
        self.executor = ExecutorAgent()
        self.verifier = VerifierAgent()
        
        print("[System] AI Operations Assistant ready!")
    
    def process_task(self, user_input: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Process a user task through the complete pipeline
        
        Args:
            user_input: Natural language task description
            verbose: Whether to print progress information
            
        Returns:
            Final verified results
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"PROCESSING TASK: {user_input}")
            print(f"{'='*60}\n")
        
        # Step 1: Planning
        if verbose:
            print("[1/3] PLANNING PHASE")
            print("-" * 60)
        
        plan = self.planner.create_plan(user_input)
        
        if verbose:
            print(f"Task: {plan.get('task', 'Unknown')}")
            print(f"Steps planned: {len(plan.get('steps', []))}")
            if plan.get('status') == 'error':
                print(f"Planning error: {plan.get('error')}")
            else:
                for step in plan.get('steps', []):
                    print(f"  - Step {step['step_number']}: {step['action']} [{step['tool']}]")
        
        # Step 2: Execution
        if verbose:
            print(f"\n[2/3] EXECUTION PHASE")
            print("-" * 60)
        
        execution_result = self.executor.execute_plan(plan)
        
        if verbose:
            summary = self.executor.get_execution_summary(execution_result)
            print(summary)
        
        # Step 3: Verification
        if verbose:
            print(f"\n[3/3] VERIFICATION PHASE")
            print("-" * 60)
        
        final_result = self.verifier.verify_and_format(plan, execution_result)
        
        if verbose:
            print(f"Status: {final_result.get('status')}")
            print(f"Completeness: {final_result.get('completeness_score', 0)}%")
            print(f"\nSummary:\n{final_result.get('summary', 'No summary available')}")
            
            if final_result.get('findings'):
                findings = final_result['findings']
                if findings.get('key_results'):
                    print(f"\nKey Results:")
                    for result in findings['key_results']:
                        print(f"  • {result}")
        
        if verbose:
            print(f"\n{'='*60}")
            print("TASK COMPLETED")
            print(f"{'='*60}\n")
        
        return final_result
    
    def process_task_simple(self, user_input: str) -> str:
        """
        Process task and return simple text summary
        
        Args:
            user_input: Natural language task description
            
        Returns:
            Text summary of results
        """
        result = self.process_task(user_input, verbose=False)
        return result.get('summary', 'Task completed')
    
    def get_available_tools(self) -> str:
        """Get description of available tools"""
        return self.tool_registry.get_tools_description()


def main():
    """Main entry point for CLI usage"""
    import sys
    
    # Check if API keys are set
    if not os.getenv("GOOGLE_API_KEY"):
        print("ERROR: GOOGLE_API_KEY environment variable not set")
        print("Please create a .env file with your API keys")
        print("See .env.example for template")
        sys.exit(1)
    
    # Initialize assistant
    assistant = AIOperationsAssistant()
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        # Run task from command line argument
        task = " ".join(sys.argv[1:])
        result = assistant.process_task(task)
        
        # Print final result as JSON
        print("\n" + "="*60)
        print("FINAL RESULT (JSON)")
        print("="*60)
        print(json.dumps(result, indent=2))
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("AI OPERATIONS ASSISTANT - Interactive Mode")
        print("="*60)
        print("\nAvailable tools:")
        print(assistant.get_available_tools())
        print("\nEnter your tasks (type 'exit' to quit):\n")
        
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    print("Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                result = assistant.process_task(user_input)
                
            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")


if __name__ == "__main__":
    import sys
    
    # Load environment variables FIRST
    load_dotenv()
    
    if len(sys.argv) > 1:
        task = sys.argv[1]
        assistant = AIOperationsAssistant()
        assistant.process_task(task)
    else:
        print("Usage: python main.py \"<task_description>\"")
        print("Example: python main.py \"Find top 3 python repos on GitHub\"")
