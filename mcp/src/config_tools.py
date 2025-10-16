"""
Configuration management tools for OneAgent MCP server.
Migrated from TypeScript config-tools.ts with simplified functionality.
"""

import os
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

def get_api_key() -> str:
    """Get API key from environment variables."""
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in .env.local file")
    return api_key

def get_graphql_endpoint() -> str:
    """Get GraphQL endpoint from environment variables."""
    endpoint = os.getenv('GRAPHQL_ENDPOINT')
    if not endpoint:
        raise ValueError("GRAPHQL_ENDPOINT not found in .env.local file")
    return endpoint

def get_organization_id() -> str:
    """Get organization ID from environment variables."""
    org_id = os.getenv('ORGANIZATION_ID')
    if not org_id:
        raise ValueError("ORGANIZATION_ID not found in .env.local file")
    return org_id

def get_user_id() -> str:
    """Get user ID from environment variables."""
    user_id = os.getenv('USER_ID')
    if not user_id:
        raise ValueError("USER_ID not found in .env.local file")
    return user_id

def is_configured() -> bool:
    """Check if all required configuration is present."""
    try:
        get_api_key()
        get_graphql_endpoint()
        get_organization_id()
        get_user_id()
        return True
    except ValueError:
        return False

def mask_api_key(api_key: str) -> str:
    """Mask API key for safe display (show only last 4 chars)."""
    if not api_key:
        return ''
    if len(api_key) <= 4:
        return '***'
    return '***' + api_key[-4:]

def read_env_file() -> Dict[str, str]:
    """Read .env.local file and return as dictionary."""
    env_file = '.env.local'
    if not os.path.exists(env_file):
        return {}
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars

def write_env_file(env_vars: Dict[str, str]) -> None:
    """Write environment variables to .env.local file."""
    env_file = '.env.local'
    with open(env_file, 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")

def register_config_tools(mcp):
    """Register all configuration management tools with FastMCP."""
    
    @mcp.tool()
    def config_get() -> str:
        """Get the current MCP server configuration"""
        try:
            env_vars = read_env_file()
            
            # Create safe config for display
            safe_config = {
                'apiKey': mask_api_key(env_vars.get('API_KEY', '')),
                'graphqlEndpoint': env_vars.get('GRAPHQL_ENDPOINT', ''),
                'organizationId': env_vars.get('ORGANIZATION_ID', ''),
                'userId': env_vars.get('USER_ID', ''),
                'timeout': env_vars.get('TIMEOUT', '30000'),
                'retries': env_vars.get('RETRIES', '3')
            }
            
            return f"""Current MCP Server Configuration:

API Key: {safe_config['apiKey']}
GraphQL Endpoint: {safe_config['graphqlEndpoint']}
Organization ID: {safe_config['organizationId']}
User ID: {safe_config['userId']}
Timeout: {safe_config['timeout']}ms
Retries: {safe_config['retries']}

Configuration Status: {'Complete' if is_configured() else 'Incomplete'}"""
            
        except Exception as e:
            return f"Error reading configuration: {str(e)}"

    @mcp.tool()
    def config_set(
        api_key: Optional[str] = None,
        timeout: Optional[int] = None,
        retries: Optional[int] = None,
        organization_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> str:
        """Update the MCP server configuration"""
        try:
            # Validate timeout range
            if timeout is not None and (timeout < 1000 or timeout > 30000):
                return "Error: Timeout must be between 1000 and 30000 milliseconds"
            
            # Validate retries range
            if retries is not None and (retries < 0 or retries > 5):
                return "Error: Retries must be between 0 and 5"
            
            # Read current config
            env_vars = read_env_file()
            
            # Update with new values
            if api_key is not None:
                env_vars['API_KEY'] = api_key
            if timeout is not None:
                env_vars['TIMEOUT'] = str(timeout)
            if retries is not None:
                env_vars['RETRIES'] = str(retries)
            if organization_id is not None:
                env_vars['ORGANIZATION_ID'] = organization_id
            if user_id is not None:
                env_vars['USER_ID'] = user_id
            
            # Write back to file
            write_env_file(env_vars)
            
            # Reload environment variables
            load_dotenv('.env.local', override=True)
            
            updated_fields = []
            if api_key is not None:
                updated_fields.append("API Key")
            if timeout is not None:
                updated_fields.append("Timeout")
            if retries is not None:
                updated_fields.append("Retries")
            if organization_id is not None:
                updated_fields.append("Organization ID")
            if user_id is not None:
                updated_fields.append("User ID")
            
            return f"Configuration updated successfully. Updated fields: {', '.join(updated_fields)}"
            
        except Exception as e:
            return f"Error updating configuration: {str(e)}"

    @mcp.tool()
    def config_status() -> str:
        """Check if the configuration is complete and valid"""
        try:
            env_vars = read_env_file()
            
            # Check each required field
            has_api_key = bool(env_vars.get('API_KEY'))
            has_graphql_endpoint = bool(env_vars.get('GRAPHQL_ENDPOINT'))
            has_organization_id = bool(env_vars.get('ORGANIZATION_ID'))
            has_user_id = bool(env_vars.get('USER_ID'))
            
            # Check for placeholder values
            api_key_valid = has_api_key and not any(placeholder in env_vars.get('API_KEY', '') 
                                                  for placeholder in ['your_', 'placeholder', '_here'])
            org_id_valid = has_organization_id and not any(placeholder in env_vars.get('ORGANIZATION_ID', '') 
                                                         for placeholder in ['your_', 'placeholder', '_here'])
            user_id_valid = has_user_id and not any(placeholder in env_vars.get('USER_ID', '') 
                                                   for placeholder in ['your_', 'placeholder', '_here'])
            
            is_configured = has_api_key and has_graphql_endpoint and has_organization_id and has_user_id
            is_fully_configured = is_configured and api_key_valid and org_id_valid and user_id_valid
            
            status = {
                'isConfigured': is_configured,
                'isFullyConfigured': is_fully_configured,
                'hasGraphQLEndpoint': has_graphql_endpoint,
                'hasApiKey': has_api_key,
                'hasOrganizationId': has_organization_id,
                'hasUserId': has_user_id,
                'apiKeyValid': api_key_valid,
                'organizationIdValid': org_id_valid,
                'userIdValid': user_id_valid,
                'timeout': env_vars.get('TIMEOUT', '30000'),
                'retries': env_vars.get('RETRIES', '3')
            }
            
            return f"""Configuration Status:

Overall Status: {'✅ Fully Configured' if is_fully_configured else '⚠️ Incomplete' if is_configured else '❌ Not Configured'}

Field Status:
- API Key: {'✅ Present & Valid' if api_key_valid else '⚠️ Present but Invalid' if has_api_key else '❌ Missing'}
- GraphQL Endpoint: {'✅ Present' if has_graphql_endpoint else '❌ Missing'}
- Organization ID: {'✅ Present & Valid' if org_id_valid else '⚠️ Present but Invalid' if has_organization_id else '❌ Missing'}
- User ID: {'✅ Present & Valid' if user_id_valid else '⚠️ Present but Invalid' if has_user_id else '❌ Missing'}

Settings:
- Timeout: {status['timeout']}ms
- Retries: {status['retries']}

{'Ready to use!' if is_fully_configured else 'Please complete configuration using config_set tool.'}"""
            
        except Exception as e:
            return f"Error checking configuration status: {str(e)}"

    @mcp.tool()
    def config_reset() -> str:
        """Reset the configuration to defaults"""
        try:
            # Create default configuration
            default_config = {
                'API_KEY': '',
                'GRAPHQL_ENDPOINT': '',
                'ORGANIZATION_ID': '',
                'USER_ID': '',
                'TIMEOUT': '30000',
                'RETRIES': '3'
            }
            
            # Write default config to file
            write_env_file(default_config)
            
            # Reload environment variables
            load_dotenv('.env.local', override=True)
            
            return """Configuration reset to defaults successfully.

Default values:
- API Key: (empty)
- GraphQL Endpoint: (empty)
- Organization ID: (empty)
- User ID: (empty)
- Timeout: 30000ms
- Retries: 3

Please use config_set to configure your API key and other required settings."""
            
        except Exception as e:
            return f"Error resetting configuration: {str(e)}"

# Export individual functions for testing
def config_get() -> str:
    """Get the current MCP server configuration"""
    try:
        env_vars = read_env_file()
        
        # Create safe config for display
        safe_config = {
            'apiKey': mask_api_key(env_vars.get('API_KEY', '')),
            'graphqlEndpoint': env_vars.get('GRAPHQL_ENDPOINT', ''),
            'organizationId': env_vars.get('ORGANIZATION_ID', ''),
            'userId': env_vars.get('USER_ID', ''),
            'timeout': env_vars.get('TIMEOUT', '30000'),
            'retries': env_vars.get('RETRIES', '3')
        }
        
        return f"""Current MCP Server Configuration:

API Key: {safe_config['apiKey']}
GraphQL Endpoint: {safe_config['graphqlEndpoint']}
Organization ID: {safe_config['organizationId']}
User ID: {safe_config['userId']}
Timeout: {safe_config['timeout']}ms
Retries: {safe_config['retries']}

Configuration Status: {'Complete' if is_configured() else 'Incomplete'}"""
        
    except Exception as e:
        return f"Error reading configuration: {str(e)}"

def config_set(
    api_key: Optional[str] = None,
    timeout: Optional[int] = None,
    retries: Optional[int] = None,
    organization_id: Optional[str] = None,
    user_id: Optional[str] = None
) -> str:
    """Update the MCP server configuration"""
    try:
        # Validate timeout range
        if timeout is not None and (timeout < 1000 or timeout > 30000):
            return "Error: Timeout must be between 1000 and 30000 milliseconds"
        
        # Validate retries range
        if retries is not None and (retries < 0 or retries > 5):
            return "Error: Retries must be between 0 and 5"
        
        # Read current config
        env_vars = read_env_file()
        
        # Update with new values
        if api_key is not None:
            env_vars['API_KEY'] = api_key
        if timeout is not None:
            env_vars['TIMEOUT'] = str(timeout)
        if retries is not None:
            env_vars['RETRIES'] = str(retries)
        if organization_id is not None:
            env_vars['ORGANIZATION_ID'] = organization_id
        if user_id is not None:
            env_vars['USER_ID'] = user_id
        
        # Write back to file
        write_env_file(env_vars)
        
        # Reload environment variables
        load_dotenv('.env.local', override=True)
        
        updated_fields = []
        if api_key is not None:
            updated_fields.append("API Key")
        if timeout is not None:
            updated_fields.append("Timeout")
        if retries is not None:
            updated_fields.append("Retries")
        if organization_id is not None:
            updated_fields.append("Organization ID")
        if user_id is not None:
            updated_fields.append("User ID")
        
        return f"Configuration updated successfully. Updated fields: {', '.join(updated_fields)}"
        
    except Exception as e:
        return f"Error updating configuration: {str(e)}"

def config_status() -> str:
    """Check if the configuration is complete and valid"""
    try:
        env_vars = read_env_file()
        
        # Check each required field
        has_api_key = bool(env_vars.get('API_KEY'))
        has_graphql_endpoint = bool(env_vars.get('GRAPHQL_ENDPOINT'))
        has_organization_id = bool(env_vars.get('ORGANIZATION_ID'))
        has_user_id = bool(env_vars.get('USER_ID'))
        
        # Check for placeholder values
        api_key_valid = has_api_key and not any(placeholder in env_vars.get('API_KEY', '') 
                                              for placeholder in ['your_', 'placeholder', '_here'])
        org_id_valid = has_organization_id and not any(placeholder in env_vars.get('ORGANIZATION_ID', '') 
                                                     for placeholder in ['your_', 'placeholder', '_here'])
        user_id_valid = has_user_id and not any(placeholder in env_vars.get('USER_ID', '') 
                                               for placeholder in ['your_', 'placeholder', '_here'])
        
        is_configured = has_api_key and has_graphql_endpoint and has_organization_id and has_user_id
        is_fully_configured = is_configured and api_key_valid and org_id_valid and user_id_valid
        
        status = {
            'isConfigured': is_configured,
            'isFullyConfigured': is_fully_configured,
            'hasGraphQLEndpoint': has_graphql_endpoint,
            'hasApiKey': has_api_key,
            'hasOrganizationId': has_organization_id,
            'hasUserId': has_user_id,
            'apiKeyValid': api_key_valid,
            'organizationIdValid': org_id_valid,
            'userIdValid': user_id_valid,
            'timeout': env_vars.get('TIMEOUT', '30000'),
            'retries': env_vars.get('RETRIES', '3')
        }
        
        return f"""Configuration Status:

Overall Status: {'✅ Fully Configured' if is_fully_configured else '⚠️ Incomplete' if is_configured else '❌ Not Configured'}

Field Status:
- API Key: {'✅ Present & Valid' if api_key_valid else '⚠️ Present but Invalid' if has_api_key else '❌ Missing'}
- GraphQL Endpoint: {'✅ Present' if has_graphql_endpoint else '❌ Missing'}
- Organization ID: {'✅ Present & Valid' if org_id_valid else '⚠️ Present but Invalid' if has_organization_id else '❌ Missing'}
- User ID: {'✅ Present & Valid' if user_id_valid else '⚠️ Present but Invalid' if has_user_id else '❌ Missing'}

Settings:
- Timeout: {status['timeout']}ms
- Retries: {status['retries']}

{'Ready to use!' if is_fully_configured else 'Please complete configuration using config_set tool.'}"""
        
    except Exception as e:
        return f"Error checking configuration status: {str(e)}"

def config_reset() -> str:
    """Reset the configuration to defaults"""
    try:
        # Create default configuration
        default_config = {
            'API_KEY': '',
            'GRAPHQL_ENDPOINT': '',
            'ORGANIZATION_ID': '',
            'USER_ID': '',
            'TIMEOUT': '30000',
            'RETRIES': '3'
        }
        
        # Write default config to file
        write_env_file(default_config)
        
        # Reload environment variables
        load_dotenv('.env.local', override=True)
        
        return """Configuration reset to defaults successfully.

Default values:
- API Key: (empty)
- GraphQL Endpoint: (empty)
- Organization ID: (empty)
- User ID: (empty)
- Timeout: 30000ms
- Retries: 3

Please use config_set to configure your API key and other required settings."""
        
    except Exception as e:
        return f"Error resetting configuration: {str(e)}"
