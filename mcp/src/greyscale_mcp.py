from fastmcp import FastMCP
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

def get_api_key():
    """Get API key from environment variables."""
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in .env.local file")
    return api_key

def get_graphql_endpoint():
    """Get GraphQL endpoint from environment variables."""
    endpoint = os.getenv('GRAPHQL_ENDPOINT')
    if not endpoint:
        raise ValueError("GRAPHQL_ENDPOINT not found in .env.local file")
    return endpoint

def get_organization_id():
    """Get organization ID from environment variables."""
    org_id = os.getenv('ORGANIZATION_ID')
    if not org_id:
        raise ValueError("ORGANIZATION_ID not found in .env.local file")
    return org_id

def is_configured():
    """Check if all required configuration is present."""
    try:
        get_api_key()
        get_graphql_endpoint()
        get_organization_id()
        return True
    except ValueError:
        return False

def execute_graphql_mutation(query, variables=None):
    """Execute a GraphQL mutation."""
    endpoint = get_graphql_endpoint()
    api_key = get_api_key()
    
    headers = {
        'Authorization-API': api_key,
        'Content-Type': 'application/json'
    }
    
    payload = {
        'query': query,
        'variables': variables or {}
    }
    
    try:
        response = requests.post(endpoint, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Check for GraphQL errors
        if 'errors' in data:
            error_messages = [error.get('message', 'Unknown error') for error in data['errors']]
            raise Exception(f"GraphQL errors: {'; '.join(error_messages)}")
        
        return data.get('data', {})
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"GraphQL mutation failed: {str(e)}")

mcp = FastMCP()

@mcp.tool()
def update_organization_theme_greyscale(
    organization_id: str = None,
    primary_color: str = "#808080",
    background_color: str = "#f5f5f5",
    text_color: str = "#333333"
) -> str:
    """
    Update organization theme to greyscale colors.
    
    Args:
        organization_id: Organization ID (uses .env.local if not provided)
        primary_color: Primary brand color (default: medium grey)
        background_color: Background color (default: light grey)
        text_color: Text color (default: dark grey)
    """
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Please set API_KEY, GRAPHQL_ENDPOINT, and ORGANIZATION_ID in .env.local file."
        
        # Use provided org ID or get from config
        org_id = organization_id or get_organization_id()
        
        # Validate org ID
        if not org_id or org_id in ['your_org_id_here', 'placeholder', 'your_organization_id']:
            return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
        
        # Construct theme tokens for greyscale theme
        theme_tokens = {
            "ref": {
                "palette": {
                    "primary50": primary_color
                }
            },
            "comp": {
                "layout": {
                    "backgroundColor": background_color,
                    "textColor": text_color
                },
                "button": {
                    "filled": {
                        "primary": {
                            "enabled": {
                                "container": {"color": primary_color},
                                "text": {"color": "#ffffff"}
                            }
                        }
                    }
                }
            }
        }
        
        # GraphQL mutation
        mutation = """
        mutation updateOrganization($input: UpdateOrganizationInput!) {
          updateOrganization(input: $input) {
            organization {
              id
              name
              __typename
            }
            __typename
          }
        }
        """
        
        # Mutation variables
        mutation_input = {
            "organizationId": org_id,
            "themeTokens": theme_tokens,
            "theme": {}
        }
        
        # Execute GraphQL mutation
        result = execute_graphql_mutation(mutation, {"input": mutation_input})
        
        # Extract organization info from result
        organization = result.get("updateOrganization", {}).get("organization", {})
        
        return f"""Success! Organization theme updated to greyscale.

Organization ID: {organization.get('id', org_id)}
Organization Name: {organization.get('name', 'Unknown')}

Theme Colors Applied:
- Primary Color: {primary_color}
- Background Color: {background_color}  
- Text Color: {text_color}

The organization's theme has been successfully updated with greyscale colors."""
        
    except Exception as e:
        return f"Error updating organization theme: {str(e)}"

if __name__ == "__main__":
    mcp.run(
        transport="http",
        port=8123
    )
