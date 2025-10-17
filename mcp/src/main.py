"""
Simple ChatGPT App Template - MCP Server
A minimal template for building ChatGPT apps with FastMCP.
"""

from fastmcp import FastMCP
from tools.math_tools import register_math_tools
from tools.ux_widget import register_ux_widget_tools

# Create FastMCP instance
mcp = FastMCP()

# Register tools
register_math_tools(mcp)
register_ux_widget_tools(mcp)

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8123
    )