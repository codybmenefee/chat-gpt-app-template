import requests
import json
from typing import Dict, Any
from config import get_api_key, get_graphql_endpoint

def execute_graphql_mutation(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a GraphQL mutation.
    
    Args:
        query: GraphQL mutation string
        variables: Variables for the mutation
        
    Returns:
        Response JSON data
        
    Raises:
        Exception: If the request fails or returns errors
    """
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
