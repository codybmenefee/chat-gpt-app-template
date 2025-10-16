# OneAgent MCP Implementation

The OneAgent MCP (Model Context Protocol) implementation provides AI-powered tools that integrate directly with GraphQL APIs through ChatGPT and other AI platforms.

## Quick Start

### Prerequisites
- Python 3.8 or higher
- OneVest API credentials
- ChatGPT or compatible MCP client

### Installation

1. **Clone and navigate to MCP directory:**
   ```bash
   git clone <repository-url>
   cd one-agent/mcp
   ```

2. **Set up Python environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.local.template .env.local
   # Edit .env.local with your credentials
   ```

4. **Start the MCP server:**
   ```bash
   python src/main.py
   ```

## Configuration

### Environment Variables

Create a `.env.local` file with your API credentials:

```env
# Required Configuration
API_KEY=your-bearer-token-here
GRAPHQL_ENDPOINT=https://your-graphql-endpoint.com/graphql
ORGANIZATION_ID=your-organization-id
USER_ID=your-user-id

# Optional Configuration
TIMEOUT=10000
RETRIES=3
```

### Getting Your Credentials

1. **API_KEY**: Get your Bearer token from the OneVest dashboard
2. **GRAPHQL_ENDPOINT**: Your GraphQL API endpoint URL
3. **ORGANIZATION_ID**: Found in your organization settings
4. **USER_ID**: Your user ID from the system

## Available Tools

### Configuration Management
- **`config_get`** - Get current server configuration (API key masked)
- **`config_set`** - Update server configuration settings
- **`config_status`** - Check if configuration is complete and valid
- **`config_reset`** - Reset configuration to defaults

### Organization Management
- **`update_organization_theme`** - Update organization branding, logos, and visual settings
- **`list_organization_logos`** - List all logo files for an organization
- **`get_logo_download_url`** - Get presigned download URL for a logo
- **`verify_organization_logo`** - Check if organization has valid logo

### File Operations
- **`upload_file`** - Upload files to cloud storage and create file records
- **`view_pdf`** - Extract and view text content from PDF files

## Usage Examples

### Update Organization Theme
```text
Use the update_organization_theme tool to change your organization's branding colors and logo
```

### Upload a Document
```text
Use the upload_file tool to upload documents, images, or other files to your organization
```

### Extract PDF Text
```text
Use the view_pdf tool to extract and read text content from PDF files
```

### Check Configuration
```text
Use the config_status tool to verify your server configuration is complete
```

## Development

### Running in Development Mode

```bash
# Using RAV (recommended)
rav dev

# Or directly with uvicorn
uvicorn src.main:app --reload --host 0.0.0.0 --port 8123
```

### Project Structure

```
mcp/
├── src/
│   ├── main.py              # Main MCP server entry point
│   ├── config.py            # Configuration management
│   ├── graphql_client.py    # GraphQL client utilities
│   ├── config_tools.py      # Configuration tools
│   ├── pdf_tools.py         # PDF processing tools
│   ├── upload_tools.py      # File upload tools
│   └── theme_tools.py       # Theme management tools
├── requirements.txt         # Python dependencies
├── rav.yaml                # RAV script configuration
└── .env.local              # Environment configuration
```

### Adding New Tools

1. **Create tool function** in appropriate module:
   ```python
   @mcp.tool()
   def your_new_tool(param1: str, param2: int = 10) -> str:
       """Description of what this tool does"""
       # Implementation here
   ```

2. **Import in main.py**:
   ```python
   from your_module import your_new_tool
   ```

3. **Test thoroughly** with ChatGPT integration

## Testing

### Individual Tool Testing
```bash
# Test configuration tools
python src/test_config.py

# Test PDF tools
python src/test_pdf.py

# Test upload tools
python src/test_upload.py

# Test theme tools
python src/test_theme.py
```

### Integration Testing
```bash
# Test complete MCP server
python src/test_main_simple.py
```

## ChatGPT Integration

### Setting up ChatGPT Apps

1. **Create ChatGPT App** in OpenAI platform
2. **Configure MCP server** with your endpoint
3. **Test tools** through ChatGPT interface
4. **Deploy** for production use

### ngrok Tunnel (for local development)

```bash
# Install ngrok
npm install -g ngrok

# Start MCP server
python src/main.py

# In another terminal, create tunnel
ngrok http 8123

# Use ngrok URL in ChatGPT App configuration
```

## Troubleshooting

### Common Issues

1. **"Configuration incomplete"**
   - Check `.env.local` has all required variables
   - Use `config_status` tool to verify configuration
   - Ensure API key is valid and has proper permissions

2. **"GraphQL endpoint not found"**
   - Verify `GRAPHQL_ENDPOINT` URL is correct
   - Check network connectivity
   - Ensure endpoint is accessible

3. **"Organization not found"**
   - Verify `ORGANIZATION_ID` is correct
   - Check API key has access to organization
   - Use `config_set` to update organization ID

4. **"MCP server not responding"**
   - Check server is running on correct port (8123)
   - Verify no firewall blocking
   - Check server logs for errors

### Debug Mode

Enable debug logging:
```bash
DEBUG=oneagent:* python src/main.py
```

### Configuration Issues

- **Missing API Key**: Use `config_set` tool to set your API key
- **Invalid Endpoint**: Ensure GraphQL endpoint URL is correct
- **Missing IDs**: Set organization ID and user ID using `config_set`
- **Check Configuration**: Use `config_status` to verify all required fields

## Security Notes

- **Never commit `.env.local`** - Contains sensitive credentials
- **Use staging environment** for development and testing
- **Rotate API keys** regularly for security
- **Limit API key permissions** to only what's needed
- **The `config_get` tool masks your API key** for security

## Loop Prevention

The MCP server includes built-in loop detection:

- **Tracks failed attempts** per tool
- **Detects repeated failures** with similar parameters
- **Provides "LOOP DETECTED"** messages with guidance
- **Prevents infinite retry loops** automatically

When you see "LOOP DETECTED" errors:
- **STOP** retrying immediately
- **Check** your parameters and configuration
- **Ask** for clarification if needed
- **Try** a different approach

## Support

For issues or questions:

1. Check this documentation first
2. Review error logs and troubleshooting section
3. Use the `config_status` tool to verify configuration
4. Contact the development team for assistance

## License

MIT License - see LICENSE file for details.

---

**OneAgent MCP** - Making AI agents that actually work with your GraphQL data.
