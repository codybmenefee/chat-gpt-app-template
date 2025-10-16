"""
PDF text extraction tools for OneAgent MCP server.
Migrated from TypeScript pdf-tools.ts with simplified functionality.
"""

import os
import json
from typing import Optional
from datetime import datetime
import pypdf

def validate_file_path(path: str) -> bool:
    """Check if file exists and is readable."""
    return os.path.exists(path) and os.path.isfile(path)

def format_file_size(bytes: int) -> str:
    """Format file size in human readable format."""
    sizes = ['Bytes', 'KB', 'MB', 'GB']
    if bytes == 0:
        return '0 Bytes'
    i = 0
    while bytes >= 1024 and i < len(sizes) - 1:
        bytes /= 1024.0
        i += 1
    return f"{bytes:.2f} {sizes[i]}"

def extract_pdf_text(file_path: str, max_pages: int = 10) -> dict:
    """Extract text from PDF file using pypdf."""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            # Get page count
            page_count = len(pdf_reader.pages)
            
            # Extract text from pages (limited by max_pages)
            text_content = ""
            pages_to_extract = min(page_count, max_pages)
            
            for page_num in range(pages_to_extract):
                page = pdf_reader.pages[page_num]
                text_content += page.extract_text() + "\n"
            
            # Get metadata if available
            metadata = {}
            if pdf_reader.metadata:
                metadata = {
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': str(pdf_reader.metadata.get('/CreationDate', '')),
                    'modification_date': str(pdf_reader.metadata.get('/ModDate', ''))
                }
            
            return {
                'success': True,
                'text_content': text_content,
                'page_count': page_count,
                'extracted_pages': pages_to_extract,
                'metadata': metadata,
                'method': 'pypdf'
            }
            
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'method': 'pypdf'
        }

def register_pdf_tools(mcp):
    """Register PDF text extraction tools with FastMCP."""
    
    @mcp.tool()
    def view_pdf(
        file_path: str,
        max_pages: int = 10,
        include_metadata: bool = True,
        include_text_preview: bool = True
    ) -> str:
        """
        Extract and view text content from a PDF file with comprehensive information 
        including metadata, page count, and text preview.
        
        Args:
            file_path: Path to the PDF file
            max_pages: Maximum number of pages to extract (default: 10, max: 100)
            include_metadata: Whether to include PDF metadata (default: True)
            include_text_preview: Whether to include text preview (default: True)
        """
        try:
            # Validate file path
            if not validate_file_path(file_path):
                return f"Error: PDF file not found: {file_path}"
            
            # Check if file is a PDF
            if not file_path.lower().endswith('.pdf'):
                return f"Error: File is not a PDF: {file_path}"
            
            # Validate max_pages parameter
            if max_pages < 1 or max_pages > 100:
                return "Error: max_pages must be between 1 and 100"
            
            # Get file stats
            stats = os.stat(file_path)
            
            # Extract text from PDF
            extraction_result = extract_pdf_text(file_path, max_pages)
            
            if not extraction_result['success']:
                # Fallback: return basic file info if extraction fails
                result = {
                    'success': False,
                    'filePath': file_path,
                    'fileInfo': {
                        'size': stats.st_size,
                        'sizeFormatted': format_file_size(stats.st_size),
                        'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    },
                    'pdfInfo': {
                        'pageCount': 0,
                        'note': 'Text extraction failed - pypdf could not process the file'
                    },
                    'content': f"PDF file detected but text extraction failed. File size: {format_file_size(stats.st_size)}",
                    'textPreview': 'Text preview not available',
                    'extractedPages': 0,
                    'totalPages': 0,
                    'method': 'pypdf (failed)',
                    'error': extraction_result['error']
                }
            else:
                # Successful extraction
                text_content = extraction_result['text_content']
                page_count = extraction_result['page_count']
                extracted_pages = extraction_result['extracted_pages']
                
                # Create text preview if requested
                text_preview = ""
                if include_text_preview and text_content:
                    text_preview = text_content[:500] + ("..." if len(text_content) > 500 else "")
                
                result = {
                    'success': True,
                    'filePath': file_path,
                    'fileInfo': {
                        'size': stats.st_size,
                        'sizeFormatted': format_file_size(stats.st_size),
                        'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                    },
                    'pdfInfo': {
                        'pageCount': page_count,
                        'extractedPages': extracted_pages,
                        'totalPages': page_count
                    },
                    'content': text_content,
                    'method': extraction_result['method']
                }
                
                # Add metadata if requested and available
                if include_metadata and extraction_result.get('metadata'):
                    result['pdfInfo']['metadata'] = extraction_result['metadata']
                
                # Add text preview if requested
                if include_text_preview:
                    result['textPreview'] = text_preview
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Error viewing PDF: {str(e)}"

# Export individual function for testing
def view_pdf(
    file_path: str,
    max_pages: int = 10,
    include_metadata: bool = True,
    include_text_preview: bool = True
) -> str:
    """
    Extract and view text content from a PDF file with comprehensive information 
    including metadata, page count, and text preview.
    
    Args:
        file_path: Path to the PDF file
        max_pages: Maximum number of pages to extract (default: 10, max: 100)
        include_metadata: Whether to include PDF metadata (default: True)
        include_text_preview: Whether to include text preview (default: True)
    """
    try:
        # Validate file path
        if not validate_file_path(file_path):
            return f"Error: PDF file not found: {file_path}"
        
        # Check if file is a PDF
        if not file_path.lower().endswith('.pdf'):
            return f"Error: File is not a PDF: {file_path}"
        
        # Validate max_pages parameter
        if max_pages < 1 or max_pages > 100:
            return "Error: max_pages must be between 1 and 100"
        
        # Get file stats
        stats = os.stat(file_path)
        
        # Extract text from PDF
        extraction_result = extract_pdf_text(file_path, max_pages)
        
        if not extraction_result['success']:
            # Fallback: return basic file info if extraction fails
            result = {
                'success': False,
                'filePath': file_path,
                'fileInfo': {
                    'size': stats.st_size,
                    'sizeFormatted': format_file_size(stats.st_size),
                    'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                },
                'pdfInfo': {
                    'pageCount': 0,
                    'note': 'Text extraction failed - PyPDF2 could not process the file'
                },
                'content': f"PDF file detected but text extraction failed. File size: {format_file_size(stats.st_size)}",
                'textPreview': 'Text preview not available',
                'extractedPages': 0,
                'totalPages': 0,
                'method': 'PyPDF2 (failed)',
                'error': extraction_result['error']
            }
        else:
            # Successful extraction
            text_content = extraction_result['text_content']
            page_count = extraction_result['page_count']
            extracted_pages = extraction_result['extracted_pages']
            
            # Create text preview if requested
            text_preview = ""
            if include_text_preview and text_content:
                text_preview = text_content[:500] + ("..." if len(text_content) > 500 else "")
            
            result = {
                'success': True,
                'filePath': file_path,
                'fileInfo': {
                    'size': stats.st_size,
                    'sizeFormatted': format_file_size(stats.st_size),
                    'created': datetime.fromtimestamp(stats.st_ctime).isoformat(),
                    'modified': datetime.fromtimestamp(stats.st_mtime).isoformat(),
                },
                'pdfInfo': {
                    'pageCount': page_count,
                    'extractedPages': extracted_pages,
                    'totalPages': page_count
                },
                'content': text_content,
                'method': extraction_result['method']
            }
            
            # Add metadata if requested and available
            if include_metadata and extraction_result.get('metadata'):
                result['pdfInfo']['metadata'] = extraction_result['metadata']
            
            # Add text preview if requested
            if include_text_preview:
                result['textPreview'] = text_preview
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return f"Error viewing PDF: {str(e)}"
