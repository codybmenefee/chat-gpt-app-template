"""
Core utilities for OneAgent MCP server.
Contains configuration management and GraphQL client functionality.
"""

from .config import (
    get_api_key,
    get_graphql_endpoint,
    get_organization_id,
    get_user_id,
    is_configured
)

from .graphql_client import execute_graphql_mutation

__all__ = [
    'get_api_key',
    'get_graphql_endpoint', 
    'get_organization_id',
    'get_user_id',
    'is_configured',
    'execute_graphql_mutation'
]
