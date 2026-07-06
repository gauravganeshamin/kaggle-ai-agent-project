import json
from datetime import datetime
from typing import Optional, Dict, Any, Callable

class Agent:
    """Base agent with memory, tool registry, and logging."""
    
    def __init__(self, name: str, role: str, tools: Dict[str, Callable] = None):
        """
        Initialize agent.
        
        Args:
            name: Agent name (e.g., "DataAgent")
            role: Agent role/responsibility
            tools: Dictionary of {tool_name: callable_function}
        """
        self.name = name
        self.role = role
        self.tools = tools or {}
        self.conversation_history = []
    
    def call_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Execute a tool and log the call.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Arguments to pass to the tool
            
        Returns:
            Result from tool execution
        """
        if tool_name not in self.tools:
            error_msg = f"Error: tool '{tool_name}' not found. Available tools: {list(self.tools.keys())}"
            self.log_call(tool_name, kwargs, {"error": error_msg})
            return {"error": error_msg}
        
        try:
            result = self.tools[tool_name](**kwargs)
            self.log_call(tool_name, kwargs, result)
            return result
        except Exception as e:
            error_msg = f"Error executing {tool_name}: {str(e)}"
            self.log_call(tool_name, kwargs, {"error": error_msg})
            return {"error": error_msg}
    
    def log_call(self, tool_name: str, inputs: Dict, output: Any):
        """
        Log tool execution for observability.
        
        Args:
            tool_name: Name of tool executed
            inputs: Input arguments
            output: Output result
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "tool": tool_name,
            "inputs": inputs,
            "output": output
        }
        self.conversation_history.append(entry)
        
        # Print summary
        output_str = json.dumps(output, indent=2)[:150] if isinstance(output, dict) else str(output)[:150]
        print(f"[{self.name}] {tool_name}(): {output_str}...")
    
    def get_history(self):
        """Return conversation history."""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []