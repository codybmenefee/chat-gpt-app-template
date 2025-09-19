# OneAgent MCP Server

An MCP (Model Context Protocol) server for wealth management portal operations via GraphQL. This server provides specific, purpose-built tools for portal operations rather than generic GraphQL tools.

## Prerequisites

- **Node.js**: Version 18.0.0 or higher
- **npm**: Latest version
- **Cursor IDE**: With MCP support enabled
- **OneVest API Access**: Valid API key and organization credentials

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone <repository-url>
cd one-agent

# Install dependencies
npm install
```

### 2. Configure Environment

```bash
# Copy the template environment file
cp .env.local.template .env.local

# Edit .env.local with your credentials
nano .env.local  # or use your preferred editor
```

### 3. Build the Project

```bash
# Build the TypeScript project
npm run build
```

### 4. Configure Cursor MCP

Add the OneAgent MCP server to your Cursor MCP configuration:

**File**: `~/.cursor/mcp.json`

```json
{
  "mcpServers": {
    "oneAgent": {
      "command": "/path/to/your/node",
      "args": [
        "/path/to/your/one-agent/dist/index.js"
      ],
      "cwd": "/path/to/your/one-agent",
      "env": {
        "NODE_ENV": "production"
      }
    }
  }
}
```

**Important**:

- Replace `/path/to/your/node` with your Node.js path (run `which node` to find it)
- Replace `/path/to/your/one-agent` with the actual path to your cloned repository
- The server runs from the built `dist/index.js` file, not the source files

### 5. Restart Cursor

After updating the MCP configuration, restart Cursor IDE to load the new MCP server.

## Development Setup

### For Development Mode

If you want to run in development mode with hot reload:

```json
{
  "mcpServers": {
    "oneAgent": {
      "command": "npx",
      "args": [
        "-y",
        "tsx",
        "src/index.ts"
      ],
      "cwd": "/path/to/your/one-agent",
      "env": {
        "NODE_ENV": "development"
      }
    }
  }
}
```

**Note**: Use development mode only for testing. Production should use the built `dist/index.js` file.

## Configuration

### Environment Variables

Create a `.env.local` file with your API credentials:

```env
# GraphQL API Configuration (endpoint is hardcoded in the application)
API_KEY=your-bearer-token-here

# Optional Configuration
TIMEOUT=10000
RETRIES=3

# Organization and User IDs (for theme and file operations)
ORGANIZATION_ID=your-org-id
USER_ID=your-user-id
```

### Getting Your Credentials

1. **API_KEY**: Get your Bearer token from the OneVest dashboard
2. **ORGANIZATION_ID**: Found in your organization settings
3. **USER_ID**: Your user ID from the system

## Available Tools

### Organization Management
- **`update_organization_theme`**: Update organization branding, logos, and visual settings
- **`upload_file`**: Upload files (documents, user avatars, general images)

### PDF Processing
- **`view_pdf`**: Extract and view text content from PDF files
- **`extract_pdf_text`**: Extract plain text from PDF files
- **`get_pdf_info`**: Get metadata and basic information about PDF files

### Configuration Management
- **`config_get`**: Get current server configuration (API key masked)
- **`config_set`**: Update server configuration settings
- **`config_reset`**: Reset configuration to defaults
- **`config_status`**: Check server configuration status

## Tool Usage Guidelines

### For Organization Logos

✅ **Use**: `update_organization_theme` - handles logo upload + organization update
❌ **Don't use**: `upload_file` for org logos - only creates file record

### For General Files

✅ **Use**: `upload_file` for documents, user avatars, general images
❌ **Don't use**: `update_organization_theme` for non-branding files

## Configuration Management via Tools

You can manage your configuration directly through Cursor using the config tools:

### Check Configuration Status

```text
Use the config_status tool to check if your configuration is complete
```

### Update Configuration

```text
Use the config_set tool to update your API key, organization ID, or user ID
```

### Get Current Configuration

```text
Use the config_get tool to view your current configuration (API key will be masked)
```

## Development

### Scripts

- `npm run dev` - Start development server with hot reload (for testing)
- `npm run build` - Build for production
- `npm start` - Run production build
- `npm run lint` - Run linting
- `npm run type-check` - Run TypeScript type checking

### Testing the MCP Server

```bash
# Build the project first
npm run build

# Test the server with a simple JSON-RPC request
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node dist/index.js

# Or run in development mode (for testing only)
npm run dev
```

**Note**: The MCP server should be run from the built `dist/index.js` file in production. The `npm run dev` command is only for development testing.

## Troubleshooting

### MCP Tools Not Appearing in Cursor

If the MCP tools don't appear in Cursor UI:

1. **Restart Cursor Completely**
   - Quit Cursor completely (Cmd+Q on Mac)
   - Reopen Cursor
   - Check if tools appear in the MCP tools panel

2. **Check Cursor Developer Tools**
   - Press Cmd+Shift+I (Mac) or Ctrl+Shift+I (Windows/Linux)
   - Go to Console tab
   - Look for any MCP-related errors
   - Check Network tab for failed MCP connections

3. **Verify MCP Configuration**
   - Check that `~/.cursor/mcp.json` contains the correct configuration
   - Ensure the `cwd` path points to your project directory
   - Verify the `args` points to `dist/index.js`

4. **Test MCP Server Manually**

   ```bash
   # Test the server responds correctly
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}' | node dist/index.js
   ```

5. **Check File Permissions**

   ```bash
   # Ensure the server file is executable
   chmod +x dist/index.js
   ```

### Common Issues

1. **"Command not found: node"**
   - Ensure Node.js is installed and in your PATH
   - Try using the full path to node in your MCP config
   - Run `which node` to find your Node.js path

2. **"Cannot find module"**
   - Run `npm install` to install dependencies
   - Run `npm run build` to build the project
   - Check that `dist/index.js` exists

3. **"Authentication failed"**
   - Check your `.env.local` file has correct credentials
   - Verify your API key is valid and has proper permissions
   - Use the `config_status` tool to check configuration

4. **"Organization not found"**
   - Verify your `ORGANIZATION_ID` is correct
   - Check that your API key has access to the organization
   - Use the `config_set` tool to update your organization ID

5. **"MCP server not responding"**
   - Check that the server path in mcp.json is correct
   - Ensure the server is running without errors
   - Check Cursor's developer console for connection errors

### Debug Mode

To enable debug logging, set the environment variable:

```bash
DEBUG=oneagent:* npm run dev
```

### Configuration Issues

1. **Missing API Key**: Use `config_set` to set your API key
2. **Invalid Endpoint**: Ensure the GraphQL endpoint URL is correct
3. **Missing IDs**: Set your organization ID and user ID using `config_set`
4. **Check Configuration**: Use `config_status` to verify all required fields are set

## Internal Employee Setup

### For New Team Members

1. **Request Access**: Get OneVest API credentials from your team lead
2. **Clone Repository**: Follow the Quick Start guide above
3. **Configure Environment**: Set up your `.env.local` file
4. **Update Cursor**: Add the MCP server to your Cursor configuration
5. **Test**: Verify the server is working with a simple operation

### Team Lead Checklist

- [ ] Verify team member has OneVest API access
- [ ] Provide correct `ORGANIZATION_ID` and staging endpoint
- [ ] Ensure team member has Node.js 18+ installed
- [ ] Test MCP server functionality after setup

## Deployment

### For Cursor Integration

1. **Build the project**:

   ```bash
   npm run build
   ```

2. **Add to Cursor MCP settings**:

   ```json
   {
     "mcpServers": {
       "oneAgent": {
         "command": "node",
         "args": ["/absolute/path/to/this/repo/dist/index.js"],
         "env": {
           "NODE_ENV": "production"
         }
       }
     }
   }
   ```

3. **Configure environment**:

   - Copy `.env.local.template` to `.env.local`
   - Add your API credentials
   - Restart Cursor

### For Enterprise Deployment

1. **Install dependencies**:

   ```bash
   npm install --production
   ```

2. **Configure**:

   - Set environment variables in `.env.local`
   - Ensure all required credentials are available

3. **Run**:

   ```bash
   npm start
   ```

## Security Notes

- **Never commit `.env.local`** - This file contains sensitive credentials
- **Use staging environment** for development and testing
- **Rotate API keys** regularly for security
- **Limit API key permissions** to only what's needed
- **The `config_get` tool masks your API key** for security

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review the logs for error messages
3. Use the `config_status` tool to verify configuration
4. Contact the development team for assistance

## License

MIT
