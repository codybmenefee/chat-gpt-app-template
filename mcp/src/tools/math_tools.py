"""
Simple math tools for ChatGPT app template.
"""

from fastmcp import FastMCP

def register_math_tools(mcp: FastMCP):
    """Register math tools with FastMCP."""
    
    @mcp.tool(
        name="add_numbers",
        title="Add Two Numbers",
        description="Add two numbers together and return the result"
    )
    def add_numbers(a: float, b: float) -> str:
        """Add two numbers and return a formatted result."""
        result = a + b
        return f"The sum of {a} and {b} is {result}"
