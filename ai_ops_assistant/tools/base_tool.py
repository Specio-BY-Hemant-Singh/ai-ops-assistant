"""
Base Tool Class and Tool Registry
All tools must inherit from BaseTool
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List


class BaseTool(ABC):
    """Abstract base class for all tools"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the tool"""
        pass
    
    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does"""
        pass
    
    @property
    @abstractmethod
    def parameters(self) -> Dict[str, str]:
        """
        Dictionary of parameter names and their descriptions
        Example: {"query": "Search query string", "limit": "Max number of results"}
        """
        pass
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with given parameters
        
        Returns:
            Dictionary with execution results
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert tool to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class ToolRegistry:
    """Registry to manage all available tools"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a new tool"""
        self._tools[tool.name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get list of all registered tools"""
        return list(self._tools.values())
    
    def get_tools_description(self) -> str:
        """Get formatted description of all tools for LLM"""
        descriptions = []
        for tool in self._tools.values():
            params_str = ", ".join([f"{k}: {v}" for k, v in tool.parameters.items()])
            descriptions.append(
                f"- {tool.name}: {tool.description}\n  Parameters: {params_str}"
            )
        return "\n".join(descriptions)
    
    def get_tools_dict(self) -> List[Dict[str, Any]]:
        """Get all tools as list of dictionaries"""
        return [tool.to_dict() for tool in self._tools.values()]


# Global registry instance
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return _registry
