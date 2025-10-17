"""
Main MCP server consolidating all OneAgent tools.
Migrated from TypeScript to Python with modular structure.
"""

from fastmcp import FastMCP
from tools.config_tools import register_config_tools
from tools.pdf_tools import register_pdf_tools
from tools.upload_tools import register_upload_tools
from tools.theme_tools import register_theme_tools
from tools.ux_widget import register_ux_widget_tools

# Create FastMCP instance
mcp = FastMCP()

# Register all tool modules
print("🔧 Registering configuration tools...")
register_config_tools(mcp)

print("📄 Registering PDF tools...")
register_pdf_tools(mcp)

print("📤 Registering upload tools...")
register_upload_tools(mcp)

print("🎨 Registering theme tools...")
register_theme_tools(mcp)

print("🖥️ Registering hello world widget...")
register_ux_widget_tools(mcp)

print("✅ All tools registered successfully!")
print("🚀 Starting OneAgent MCP Server...")

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8123
    )