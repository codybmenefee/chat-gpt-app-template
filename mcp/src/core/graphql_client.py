import requests
import json
from typing import Dict, Any
from .config import get_api_key, get_graphql_endpoint

def _parse_graphql_errors(errors: list) -> str:
    """Parse GraphQL errors and format them for better user experience."""
    error_messages = []
    for error in errors:
        message = error.get('message', 'Unknown error')
        
        # Parse field validation errors for better user experience
        if 'Field "' in message and 'is not defined by type' in message:
            # Extract field name and type
            field_match = message.split('Field "')[1].split('"')[0] if 'Field "' in message else None
            type_match = message.split('type "')[1].split('"')[0] if 'type "' in message else None
            
            # Check for suggestions
            suggestion = ""
            if 'Did you mean "' in message:
                suggestion = message.split('Did you mean "')[1].split('"?')[0]
            
            if field_match and type_match:
                formatted_error = f"Invalid field '{field_match}' in {type_match}"
                if suggestion:
                    formatted_error += f". Did you mean '{suggestion}'?"
                error_messages.append(formatted_error)
            else:
                error_messages.append(message)
        else:
            error_messages.append(message)
    
    return '; '.join(error_messages)

def execute_graphql_query(query: str, variables: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Execute a GraphQL query.
    
    Args:
        query: GraphQL query string
        variables: Variables for the query
        
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
            formatted_errors = _parse_graphql_errors(data['errors'])
            raise Exception(f"GraphQL errors: {formatted_errors}")
        
        return data.get('data', {})
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"GraphQL query failed: {str(e)}")

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
            formatted_errors = _parse_graphql_errors(data['errors'])
            raise Exception(f"GraphQL errors: {formatted_errors}")
        
        return data.get('data', {})
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"HTTP request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise Exception(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"GraphQL mutation failed: {str(e)}")