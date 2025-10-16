import os
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
