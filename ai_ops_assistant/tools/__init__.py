"""Tools module - API integrations"""
from .base_tool import BaseTool, ToolRegistry, get_registry
from .github_tool import GitHubTool
from .weather_tool import WeatherTool

# Initialize and register all tools
def initialize_tools():
    """Initialize and register all available tools"""
    registry = get_registry()
    
    # Register GitHub tool
    github_tool = GitHubTool()
    registry.register(github_tool)
    
    # Register Weather tool
    weather_tool = WeatherTool()
    registry.register(weather_tool)
    
    return registry

__all__ = [
    'BaseTool',
    'ToolRegistry', 
    'get_registry',
    'GitHubTool',
    'WeatherTool',
    'initialize_tools'
]
