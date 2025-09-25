# OneAgent MCP Server - Quick Installation

## For Team Members

### One-Command Installation

Copy and paste this command into your terminal:

```bash
curl -fsSL https://raw.githubusercontent.com/codybmenefee/one-agent/main/install.sh | bash
```

### Local Installation

If you have the repository cloned locally:

```bash
cd /path/to/one-agent && ./install.sh
```

## Prerequisites

- Node.js 22.0.0 or higher
- Cursor IDE installed
- Git (for cloning the repository)

## What the installer does

1. ✅ Checks Node.js version compatibility
2. ✅ Installs project dependencies (`npm install`)
3. ✅ Builds the MCP server (`npm run build`)
4. ✅ Creates MCP configuration for Cursor
5. ✅ Places the configuration in the correct Cursor directory

## After Installation

1. **Restart Cursor** - The MCP server will be loaded
2. **Set up configuration** - Create `.env.local` with your API credentials
3. **Test the connection** - Use the `config_status` tool to verify setup

## Configuration

Create a `.env.local` file in the project directory:

```env
# Required
API_KEY=your-bearer-token-here
ORGANIZATION_ID=your-org-id
USER_ID=your-user-id

# Optional
TIMEOUT=10000
RETRIES=3
```

## Troubleshooting

### MCP Tools Not Appearing
- Restart Cursor completely (Cmd+Q on Mac)
- Check Cursor's developer console for errors
- Verify the MCP configuration was created correctly

### Configuration Issues
- Use the `config_status` tool to check your setup
- Use the `config_set` tool to update your credentials
- Ensure your API key has proper permissions

## Support

For issues or questions:
1. Check the troubleshooting section in README.md
2. Use the `config_status` tool to verify configuration
3. Contact the development team for assistance
