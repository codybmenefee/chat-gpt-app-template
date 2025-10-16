"""
File upload tools for OneAgent MCP server.
Migrated from TypeScript image-upload-tools.ts.full with simplified functionality.
"""

import os
import json
import mimetypes
from typing import Optional
from dotenv import load_dotenv
import requests

# Load environment variables from .env.local
load_dotenv('.env.local')

from core.config import (
    get_api_key,
    get_graphql_endpoint,
    get_organization_id,
    get_user_id,
    is_configured
)
from core.graphql_client import execute_graphql_mutation

def validate_file_path(path: str) -> bool:
    """Check if file exists and is readable."""
    return os.path.exists(path) and os.path.isfile(path)

def get_file_content_type(file_path: str) -> str:
    """Get MIME type for file."""
    content_type, _ = mimetypes.guess_type(file_path)
    return content_type or 'application/octet-stream'

def register_upload_tools(mcp):
    """Register file upload tools with FastMCP."""
    
    @mcp.tool()
    def upload_file(
        file_path: str,
        file_name: Optional[str] = None,
        object_type: str = "ORGANIZATION",
        object_id: Optional[str] = None,
        file_type: str = "DOCUMENT",
        user_id: Optional[str] = None,
        permission_type: str = "PUBLIC"
    ) -> str:
        """
        Upload general files to S3 and create file document records.
        Use for documents, user avatars, and general images.
        DO NOT use for organization logos - use update_organization_theme instead.
        If objectId/userId are not provided, uses configured values from .env.local.
        
        Args:
            file_path: Path to the file to upload
            file_name: Name for the file (defaults to filename from path)
            object_type: Type of object (ORGANIZATION, USER, CLIENT)
            object_id: ID of the object (uses ORGANIZATION_ID from config if not provided)
            file_type: Type of file (AVATAR, DOCUMENT, IMAGE)
            user_id: User ID (uses USER_ID from config if not provided)
            permission_type: Permission level (PUBLIC, PRIVATE, RESTRICTED)
        """
        try:
            # Validate configuration
            if not is_configured():
                return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
            
            # Validate file path
            if not validate_file_path(file_path):
                return f"Error: File not found: {file_path}"
            
            # Get configuration values
            org_id = object_id or get_organization_id()
            user_id_value = user_id or get_user_id()
            file_name_value = file_name or os.path.basename(file_path)
            
            # Validate object_type
            if object_type not in ['ORGANIZATION', 'USER', 'CLIENT']:
                return "Error: object_type must be ORGANIZATION, USER, or CLIENT"
            
            # Validate file_type
            if file_type not in ['AVATAR', 'DOCUMENT', 'IMAGE']:
                return "Error: file_type must be AVATAR, DOCUMENT, or IMAGE"
            
            # Validate permission_type
            if permission_type not in ['PUBLIC', 'PRIVATE', 'RESTRICTED']:
                return "Error: permission_type must be PUBLIC, PRIVATE, or RESTRICTED"
            
            # Check for placeholder values
            if org_id and any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
                return "Error: Invalid organization ID provided. Please omit the objectId parameter to use the configured value, or provide a valid organization ID."
            
            if user_id_value and any(placeholder in user_id_value for placeholder in ['your_', 'placeholder', '_here']):
                return "Error: Invalid user ID provided. Please omit the userId parameter to use the configured value, or provide a valid user ID."
            
            print(f"🚀 Starting file upload: {file_name_value}")
            
            # Step 1: Get upload URL
            print("📡 Getting upload URL...")
            upload_url_query = """
                query fetchFileUploadUrl($input: FetchFileUploadUrlInput!) {
                    fetchFileUploadUrl(input: $input) {
                        temporarySignedURL
                        timestamp
                        __typename
                    }
                }
            """
            
            upload_url_variables = {
                "input": {
                    "objectType": object_type,
                    "objectId": org_id,
                    "fileName": file_name_value,
                    "type": file_type,
                    "userId": user_id_value,
                    "generateUniqueFileName": True,
                },
            }
            
            upload_url_result = execute_graphql_mutation(upload_url_query, upload_url_variables)
            upload_data = upload_url_result.get("fetchFileUploadUrl", {})
            temporary_signed_url = upload_data.get("temporarySignedURL")
            timestamp = upload_data.get("timestamp")
            
            if not temporary_signed_url:
                return "Error: Failed to get upload URL from GraphQL"
            
            print("✅ Upload URL generated")
            
            # Step 2: Read file and upload to S3
            print("📤 Uploading file to S3...")
            with open(file_path, 'rb') as file:
                file_buffer = file.read()
            
            upload_response = requests.put(
                temporary_signed_url,
                data=file_buffer,
                headers={'Content-Type': 'application/octet-stream'},
                timeout=60
            )
            
            if not upload_response.ok:
                return f"Error: Failed to upload file to S3: {upload_response.status_code} {upload_response.reason}"
            
            print("✅ File uploaded to S3 successfully")
            
            # Step 3: Create file document
            print("📄 Creating file document...")
            create_document_mutation = """
                mutation createFileDocument($input: CreateFileDocumentInput!) {
                    createFileDocument(input: $input) {
                        fileDocument {
                            id
                            name
                            fileName
                            s3Key
                            type
                            __typename
                        }
                        __typename
                    }
                }
            """
            
            document_variables = {
                "input": {
                    "fileName": file_name_value,
                    "objectId": org_id,
                    "objectType": object_type,
                    "name": file_name_value,
                    "type": file_type,
                    "permissionType": permission_type,
                    "sourceType": file_type,
                    "timestamp": timestamp,
                },
            }
            
            document_result = execute_graphql_mutation(create_document_mutation, document_variables)
            file_document = document_result.get("createFileDocument", {}).get("fileDocument", {})
            
            if not file_document.get("id"):
                return "Error: Failed to create file document"
            
            print("✅ File document created:", file_document["id"])
            
            result = {
                "success": True,
                "fileDocument": file_document,
                "message": "File uploaded and processed successfully",
                "steps": [
                    "1. ✅ Generated upload URL",
                    "2. ✅ Uploaded file to S3", 
                    "3. ✅ Created file document",
                ],
                "fileInfo": {
                    "originalPath": file_path,
                    "fileName": file_name_value,
                    "fileSize": len(file_buffer),
                    "contentType": get_file_content_type(file_path)
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error uploading file: {str(e)}"

# Export individual function for testing
def upload_file(
    file_path: str,
    file_name: Optional[str] = None,
    object_type: str = "ORGANIZATION",
    object_id: Optional[str] = None,
    file_type: str = "DOCUMENT",
    user_id: Optional[str] = None,
    permission_type: str = "PUBLIC"
) -> str:
    """
    Upload general files to S3 and create file document records.
    Use for documents, user avatars, and general images.
    DO NOT use for organization logos - use update_organization_theme instead.
    If objectId/userId are not provided, uses configured values from .env.local.
    
    Args:
        file_path: Path to the file to upload
        file_name: Name for the file (defaults to filename from path)
        object_type: Type of object (ORGANIZATION, USER, CLIENT)
        object_id: ID of the object (uses ORGANIZATION_ID from config if not provided)
        file_type: Type of file (AVATAR, DOCUMENT, IMAGE)
        user_id: User ID (uses USER_ID from config if not provided)
        permission_type: Permission level (PUBLIC, PRIVATE, RESTRICTED)
    """
    try:
        # Validate configuration
        if not is_configured():
            return "Error: Server configuration is incomplete. Use config_set to configure API key and other required settings."
        
        # Validate file path
        if not validate_file_path(file_path):
            return f"Error: File not found: {file_path}"
        
        # Get configuration values
        org_id = object_id or get_organization_id()
        user_id_value = user_id or get_user_id()
        file_name_value = file_name or os.path.basename(file_path)
        
        # Validate object_type
        if object_type not in ['ORGANIZATION', 'USER', 'CLIENT']:
            return "Error: object_type must be ORGANIZATION, USER, or CLIENT"
        
        # Validate file_type
        if file_type not in ['AVATAR', 'DOCUMENT', 'IMAGE']:
            return "Error: file_type must be AVATAR, DOCUMENT, or IMAGE"
        
        # Validate permission_type
        if permission_type not in ['PUBLIC', 'PRIVATE', 'RESTRICTED']:
            return "Error: permission_type must be PUBLIC, PRIVATE, or RESTRICTED"
        
        # Check for placeholder values
        if org_id and any(placeholder in org_id for placeholder in ['your_', 'placeholder', '_here']):
            return "Error: Invalid organization ID provided. Please omit the objectId parameter to use the configured value, or provide a valid organization ID."
        
        if user_id_value and any(placeholder in user_id_value for placeholder in ['your_', 'placeholder', '_here']):
            return "Error: Invalid user ID provided. Please omit the userId parameter to use the configured value, or provide a valid user ID."
        
        print(f"🚀 Starting file upload: {file_name_value}")
        
        # Step 1: Get upload URL
        print("📡 Getting upload URL...")
        upload_url_query = """
            query fetchFileUploadUrl($input: FetchFileUploadUrlInput!) {
                fetchFileUploadUrl(input: $input) {
                    temporarySignedURL
                    timestamp
                    __typename
                }
            }
        """
        
        upload_url_variables = {
            "input": {
                "objectType": object_type,
                "objectId": org_id,
                "fileName": file_name_value,
                "type": file_type,
                "userId": user_id_value,
                "generateUniqueFileName": True,
            },
        }
        
        upload_url_result = execute_graphql_mutation(upload_url_query, upload_url_variables)
        upload_data = upload_url_result.get("fetchFileUploadUrl", {})
        temporary_signed_url = upload_data.get("temporarySignedURL")
        timestamp = upload_data.get("timestamp")
        
        if not temporary_signed_url:
            return "Error: Failed to get upload URL from GraphQL"
        
        print("✅ Upload URL generated")
        
        # Step 2: Read file and upload to S3
        print("📤 Uploading file to S3...")
        with open(file_path, 'rb') as file:
            file_buffer = file.read()
        
        upload_response = requests.put(
            temporary_signed_url,
            data=file_buffer,
            headers={'Content-Type': 'application/octet-stream'},
            timeout=60
        )
        
        if not upload_response.ok:
            return f"Error: Failed to upload file to S3: {upload_response.status_code} {upload_response.reason}"
        
        print("✅ File uploaded to S3 successfully")
        
        # Step 3: Create file document
        print("📄 Creating file document...")
        create_document_mutation = """
            mutation createFileDocument($input: CreateFileDocumentInput!) {
                createFileDocument(input: $input) {
                    fileDocument {
                        id
                        name
                        fileName
                        s3Key
                        type
                        __typename
                    }
                    __typename
                }
            }
        """
        
        document_variables = {
            "input": {
                "fileName": file_name_value,
                "objectId": org_id,
                "objectType": object_type,
                "name": file_name_value,
                "type": file_type,
                "permissionType": permission_type,
                "sourceType": file_type,
                "timestamp": timestamp,
            },
        }
        
        document_result = execute_graphql_mutation(create_document_mutation, document_variables)
        file_document = document_result.get("createFileDocument", {}).get("fileDocument", {})
        
        if not file_document.get("id"):
            return "Error: Failed to create file document"
        
        print("✅ File document created:", file_document["id"])
        
        result = {
            "success": True,
            "fileDocument": file_document,
            "message": "File uploaded and processed successfully",
            "steps": [
                "1. ✅ Generated upload URL",
                "2. ✅ Uploaded file to S3", 
                "3. ✅ Created file document",
            ],
            "fileInfo": {
                "originalPath": file_path,
                "fileName": file_name_value,
                "fileSize": len(file_buffer),
                "contentType": get_file_content_type(file_path)
            }
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error uploading file: {str(e)}"

