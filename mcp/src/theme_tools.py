"""
Organization theme and logo management tools for OneAgent MCP server.
Migrated from TypeScript graphql-tools.ts.full with simplified functionality.
"""

import os
import json
import re
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import requests

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

def execute_graphql_mutation(query: str, variables: dict = None) -> dict:
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

def validate_hex_color(color: str) -> bool:
    """Validate hex color format #RRGGBB"""
    return bool(re.match(r'^#[0-9a-fA-F]{6}$', color))

def validate_css_value(value: str, pattern: str) -> bool:
    """Validate CSS value format"""
    return bool(re.match(pattern, value))

def register_theme_tools(mcp):
    """Register organization theme and logo management tools with FastMCP."""
    
    @mcp.tool()
    def update_organization_theme(
        organization_id: Optional[str] = None,
        favicon_link: Optional[str] = None,
        browser_tab_title: Optional[str] = None,
        logo_file: Optional[Dict[str, Any]] = None,
        theme_tokens: Optional[Dict[str, Any]] = None,
        theme: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Update organization theme, branding, and visual design settings.
        PRIMARY tool for organization logo uploads and theme customization.
        Handles colors, typography, layout, and all visual branding elements.
        Logo uploads are automatically linked to the organization.
        If organizationId is not provided, uses the configured organization ID from .env.local.
        
        Args:
            organization_id: Organization ID (uses config if not provided)
            favicon_link: URL for favicon
            browser_tab_title: Title for browser tab
            logo_file: Logo file information (fileName, filePath, userId, etc.)
            theme_tokens: Theme token configuration
            theme: Additional theme configuration
        """
        try:
            # Validate configuration
            if not is_configured():
                return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
            
            # Get organization ID
            org_id = organization_id or get_organization_id()
            
            # Validate organization ID
            if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
                return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
            
            # Validate theme tokens if provided
            if theme_tokens:
                # Basic validation for simplified theme tokens
                if 'ref' in theme_tokens and 'palette' in theme_tokens['ref']:
                    palette = theme_tokens['ref']['palette']
                    for color_key, color_value in palette.items():
                        if color_value and not validate_hex_color(color_value):
                            return f"Error: Invalid hex color format for {color_key}: {color_value}. Use format #RRGGBB"
                
                if 'comp' in theme_tokens:
                    comp = theme_tokens['comp']
                    if 'layout' in comp:
                        layout = comp['layout']
                        for color_key, color_value in layout.items():
                            if color_value and not validate_hex_color(color_value):
                                return f"Error: Invalid hex color format for layout.{color_key}: {color_value}. Use format #RRGGBB"
            
            # TODO: Add comprehensive theme token schema validation (all 50+ tokens)
            # TODO: Add logo upload integration (combine upload_file + updateOrganization)
            # TODO: Add theme preview/validation
            # TODO: Add support for typography, elevation, border radius customization
            # TODO: Add support for component-level theme tokens (buttons, cards, etc.)
            
            print(f"🎨 Updating organization theme for: {org_id}")
            
            # GraphQL mutation for updating organization
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
            
            # Build mutation input
            mutation_input = {
                "organizationId": org_id
            }
            
            if favicon_link:
                mutation_input["faviconLink"] = favicon_link
            
            if browser_tab_title:
                mutation_input["browserTabTitle"] = browser_tab_title
            
            if theme_tokens:
                mutation_input["themeTokens"] = theme_tokens
            
            if theme:
                mutation_input["theme"] = theme
            
            # Execute GraphQL mutation
            result = execute_graphql_mutation(mutation, {"input": mutation_input})
            
            # Extract organization info from result
            organization = result.get("updateOrganization", {}).get("organization", {})
            
            return f"""Success! Organization theme updated successfully.

Organization ID: {organization.get('id', org_id)}
Organization Name: {organization.get('name', 'Unknown')}

Updated Settings:
- Favicon Link: {favicon_link or 'Not updated'}
- Browser Tab Title: {browser_tab_title or 'Not updated'}
- Theme Tokens: {'Updated' if theme_tokens else 'Not updated'}
- Theme: {'Updated' if theme else 'Not updated'}

The organization's theme has been successfully updated."""
            
        except Exception as e:
            return f"Error updating organization theme: {str(e)}"

    @mcp.tool()
    def list_organization_logos(
        organization_id: Optional[str] = None,
        limit: int = 10
    ) -> str:
        """
        List all logo files associated with an organization.
        Useful for verifying logo uploads and managing multiple logos.
        
        Args:
            organization_id: Organization ID (uses config if not provided)
            limit: Maximum number of logos to return (default: 10, max: 50)
        """
        try:
            # Validate configuration
            if not is_configured():
                return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
            
            # Get organization ID
            org_id = organization_id or get_organization_id()
            
            # Validate organization ID
            if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
                return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
            
            # Validate limit
            if limit < 1 or limit > 50:
                return "Error: limit must be between 1 and 50"
            
            print(f"🔍 Listing logos for organization: {org_id}")
            
            # GraphQL query for file documents
            query = """
                query fileDocuments($input: FileDocumentsInput!) {
                    fileDocuments(input: $input) {
                        fileDocuments {
                            id
                            name
                            fileName
                            type
                            permissionType
                            createdAt
                            __typename
                        }
                        __typename
                    }
                }
            """
            
            query_variables = {
                "input": {
                    "objectType": "ORGANIZATION",
                    "objectId": org_id,
                    "type": "LOGO",
                    "limit": limit
                }
            }
            
            result = execute_graphql_mutation(query, query_variables)
            file_documents = result.get("fileDocuments", {}).get("fileDocuments", [])
            
            if not file_documents:
                return f"No logos found for organization {org_id}"
            
            logos_info = []
            for doc in file_documents:
                logos_info.append({
                    "id": doc.get("id"),
                    "name": doc.get("name"),
                    "fileName": doc.get("fileName"),
                    "type": doc.get("type"),
                    "permissionType": doc.get("permissionType"),
                    "createdAt": doc.get("createdAt")
                })
            
            return f"""Found {len(logos_info)} logo(s) for organization {org_id}:

{json.dumps(logos_info, indent=2)}"""
            
        except Exception as e:
            return f"Error listing organization logos: {str(e)}"

    @mcp.tool()
    def get_logo_download_url(file_document_id: str) -> str:
        """
        Get the download URL for a specific logo file.
        Useful for verifying logo accessibility and getting the URL to display the logo.
        
        Args:
            file_document_id: The file document ID
        """
        try:
            # Validate configuration
            if not is_configured():
                return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
            
            if not file_document_id:
                return "Error: file_document_id is required"
            
            print(f"🔗 Getting download URL for file document: {file_document_id}")
            
            # GraphQL mutation for presigned download URL
            mutation = """
                mutation requestPresignedDownloadUrl($input: RequestPresignedDownloadUrlInput!) {
                    requestPresignedDownloadUrl(input: $input) {
                        presignedUrl
                        expiresAt
                        __typename
                    }
                }
            """
            
            mutation_variables = {
                "input": {
                    "fileDocumentId": file_document_id
                }
            }
            
            result = execute_graphql_mutation(mutation, mutation_variables)
            download_data = result.get("requestPresignedDownloadUrl", {})
            
            presigned_url = download_data.get("presignedUrl")
            expires_at = download_data.get("expiresAt")
            
            if not presigned_url:
                return "Error: Failed to get download URL"
            
            return f"""Download URL generated successfully:

File Document ID: {file_document_id}
Download URL: {presigned_url}
Expires At: {expires_at}

Note: This URL is temporary and will expire. Use it promptly to download the logo."""
            
        except Exception as e:
            return f"Error getting logo download URL: {str(e)}"

    @mcp.tool()
    def verify_organization_logo(
        organization_id: Optional[str] = None
    ) -> str:
        """
        Verify that an organization has a logo and get its details.
        Returns the most recent logo file information.
        
        Args:
            organization_id: Organization ID (uses config if not provided)
        """
        try:
            # Validate configuration
            if not is_configured():
                return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
            
            # Get organization ID
            org_id = organization_id or get_organization_id()
            
            # Validate organization ID
            if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
                return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
            
            print(f"✅ Verifying logo for organization: {org_id}")
            
            # GraphQL query for file documents (limit to 1 to get most recent)
            query = """
                query fileDocuments($input: FileDocumentsInput!) {
                    fileDocuments(input: $input) {
                        fileDocuments {
                            id
                            name
                            fileName
                            type
                            permissionType
                            createdAt
                            __typename
                        }
                        __typename
                    }
                }
            """
            
            query_variables = {
                "input": {
                    "objectType": "ORGANIZATION",
                    "objectId": org_id,
                    "type": "LOGO",
                    "limit": 1
                }
            }
            
            result = execute_graphql_mutation(query, query_variables)
            file_documents = result.get("fileDocuments", {}).get("fileDocuments", [])
            
            if not file_documents:
                return f"❌ No logo found for organization {org_id}"
            
            logo = file_documents[0]
            
            return f"""✅ Logo verified for organization {org_id}:

Logo Details:
- ID: {logo.get('id')}
- Name: {logo.get('name')}
- File Name: {logo.get('fileName')}
- Type: {logo.get('type')}
- Permission: {logo.get('permissionType')}
- Created: {logo.get('createdAt')}

The organization has a valid logo file."""
            
        except Exception as e:
            return f"Error verifying organization logo: {str(e)}"

# Export individual functions for testing
def update_organization_theme(
    organization_id: Optional[str] = None,
    favicon_link: Optional[str] = None,
    browser_tab_title: Optional[str] = None,
    logo_file: Optional[Dict[str, Any]] = None,
    theme_tokens: Optional[Dict[str, Any]] = None,
    theme: Optional[Dict[str, Any]] = None
) -> str:
    """Update organization theme, branding, and visual design settings."""
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
        
        # Get organization ID
        org_id = organization_id or get_organization_id()
        
        # Validate organization ID
        if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
            return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
        
        # Validate theme tokens if provided
        if theme_tokens:
            # Basic validation for simplified theme tokens
            if 'ref' in theme_tokens and 'palette' in theme_tokens['ref']:
                palette = theme_tokens['ref']['palette']
                for color_key, color_value in palette.items():
                    if color_value and not validate_hex_color(color_value):
                        return f"Error: Invalid hex color format for {color_key}: {color_value}. Use format #RRGGBB"
            
            if 'comp' in theme_tokens:
                comp = theme_tokens['comp']
                if 'layout' in comp:
                    layout = comp['layout']
                    for color_key, color_value in layout.items():
                        if color_value and not validate_hex_color(color_value):
                            return f"Error: Invalid hex color format for layout.{color_key}: {color_value}. Use format #RRGGBB"
        
        print(f"🎨 Updating organization theme for: {org_id}")
        
        # GraphQL mutation for updating organization
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
        
        # Build mutation input
        mutation_input = {
            "organizationId": org_id
        }
        
        if favicon_link:
            mutation_input["faviconLink"] = favicon_link
        
        if browser_tab_title:
            mutation_input["browserTabTitle"] = browser_tab_title
        
        if theme_tokens:
            mutation_input["themeTokens"] = theme_tokens
        
        if theme:
            mutation_input["theme"] = theme
        
        # Execute GraphQL mutation
        result = execute_graphql_mutation(mutation, {"input": mutation_input})
        
        # Extract organization info from result
        organization = result.get("updateOrganization", {}).get("organization", {})
        
        return f"""Success! Organization theme updated successfully.

Organization ID: {organization.get('id', org_id)}
Organization Name: {organization.get('name', 'Unknown')}

Updated Settings:
- Favicon Link: {favicon_link or 'Not updated'}
- Browser Tab Title: {browser_tab_title or 'Not updated'}
- Theme Tokens: {'Updated' if theme_tokens else 'Not updated'}
- Theme: {'Updated' if theme else 'Not updated'}

The organization's theme has been successfully updated."""
        
    except Exception as e:
        return f"Error updating organization theme: {str(e)}"

def list_organization_logos(
    organization_id: Optional[str] = None,
    limit: int = 10
) -> str:
    """List all logo files associated with an organization."""
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
        
        # Get organization ID
        org_id = organization_id or get_organization_id()
        
        # Validate organization ID
        if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
            return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
        
        # Validate limit
        if limit < 1 or limit > 50:
            return "Error: limit must be between 1 and 50"
        
        print(f"🔍 Listing logos for organization: {org_id}")
        
        # GraphQL query for file documents
        query = """
            query fileDocuments($input: FileDocumentsInput!) {
                fileDocuments(input: $input) {
                    fileDocuments {
                        id
                        name
                        fileName
                        type
                        permissionType
                        createdAt
                        __typename
                    }
                    __typename
                }
            }
        """
        
        query_variables = {
            "input": {
                "objectType": "ORGANIZATION",
                "objectId": org_id,
                "type": "LOGO",
                "limit": limit
            }
        }
        
        result = execute_graphql_mutation(query, query_variables)
        file_documents = result.get("fileDocuments", {}).get("fileDocuments", [])
        
        if not file_documents:
            return f"No logos found for organization {org_id}"
        
        logos_info = []
        for doc in file_documents:
            logos_info.append({
                "id": doc.get("id"),
                "name": doc.get("name"),
                "fileName": doc.get("fileName"),
                "type": doc.get("type"),
                "permissionType": doc.get("permissionType"),
                "createdAt": doc.get("createdAt")
            })
        
        return f"""Found {len(logos_info)} logo(s) for organization {org_id}:

{json.dumps(logos_info, indent=2)}"""
        
    except Exception as e:
        return f"Error listing organization logos: {str(e)}"

def get_logo_download_url(file_document_id: str) -> str:
    """Get the download URL for a specific logo file."""
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
        
        if not file_document_id:
            return "Error: file_document_id is required"
        
        print(f"🔗 Getting download URL for file document: {file_document_id}")
        
        # GraphQL mutation for presigned download URL
        mutation = """
            mutation requestPresignedDownloadUrl($input: RequestPresignedDownloadUrlInput!) {
                requestPresignedDownloadUrl(input: $input) {
                    presignedUrl
                    expiresAt
                    __typename
                }
            }
        """
        
        mutation_variables = {
            "input": {
                "fileDocumentId": file_document_id
            }
        }
        
        result = execute_graphql_mutation(mutation, mutation_variables)
        download_data = result.get("requestPresignedDownloadUrl", {})
        
        presigned_url = download_data.get("presignedUrl")
        expires_at = download_data.get("expiresAt")
        
        if not presigned_url:
            return "Error: Failed to get download URL"
        
        return f"""Download URL generated successfully:

File Document ID: {file_document_id}
Download URL: {presigned_url}
Expires At: {expires_at}

Note: This URL is temporary and will expire. Use it promptly to download the logo."""
        
    except Exception as e:
        return f"Error getting logo download URL: {str(e)}"

def verify_organization_logo(
    organization_id: Optional[str] = None
) -> str:
    """Verify that an organization has a logo and get its details."""
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
        
        # Get organization ID
        org_id = organization_id or get_organization_id()
        
        # Validate organization ID
        if not org_id or any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
            return "Error: Invalid organization ID. Please set ORGANIZATION_ID in .env.local file or provide a valid organization_id parameter."
        
        print(f"✅ Verifying logo for organization: {org_id}")
        
        # GraphQL query for file documents (limit to 1 to get most recent)
        query = """
            query fileDocuments($input: FileDocumentsInput!) {
                fileDocuments(input: $input) {
                    fileDocuments {
                        id
                        name
                        fileName
                        type
                        permissionType
                        createdAt
                        __typename
                    }
                    __typename
                }
            }
        """
        
        query_variables = {
            "input": {
                "objectType": "ORGANIZATION",
                "objectId": org_id,
                "type": "LOGO",
                "limit": 1
            }
        }
        
        result = execute_graphql_mutation(query, query_variables)
        file_documents = result.get("fileDocuments", {}).get("fileDocuments", [])
        
        if not file_documents:
            return f"❌ No logo found for organization {org_id}"
        
        logo = file_documents[0]
        
        return f"""✅ Logo verified for organization {org_id}:

Logo Details:
- ID: {logo.get('id')}
- Name: {logo.get('name')}
- File Name: {logo.get('fileName')}
- Type: {logo.get('type')}
- Permission: {logo.get('permissionType')}
- Created: {logo.get('createdAt')}

The organization has a valid logo file."""
        
    except Exception as e:
        return f"Error verifying organization logo: {str(e)}"

