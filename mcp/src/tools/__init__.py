"""
Tool modules for OneAgent MCP server.
Contains all MCP tool implementations organized by functionality.
"""

from .config_tools import register_config_tools
from .pdf_tools import register_pdf_tools
from .upload_tools import register_upload_tools
from .theme_tools import register_theme_tools

__all__ = [
    'register_config_tools',
    'register_pdf_tools', 
    'register_upload_tools',
    'register_theme_tools'
]
