# OneAgent

**OneAgent** is a comprehensive platform for building AI-powered tools that integrate directly with GraphQL APIs. Our mission is to simplify the creation of intelligent agents that can interact with complex data systems through natural language interfaces.

## What is OneAgent?

OneAgent provides a unified approach to building AI agents that can:
- Connect directly to GraphQL APIs
- Process documents and files intelligently
- Manage organizational settings and branding
- Provide natural language interfaces to complex systems

## Available Implementations

### MCP (Model Context Protocol) Implementation
The MCP implementation allows OneAgent to integrate with ChatGPT and other AI platforms through the Model Context Protocol.

**Quick Start:**
```bash
cd mcp
pip install -r requirements.txt
python src/main.py
```

**Features:**
- Organization theme and branding management
- PDF text extraction and processing
- File upload to cloud storage
- Configuration management
- Direct GraphQL API integration

[📖 **MCP Documentation**](./mcp/README.md)

## Architecture Philosophy

OneAgent follows a modular architecture where each implementation serves a specific use case:

- **`/mcp`** - Model Context Protocol implementation for AI platform integration
- **`/sdk`** - Software Development Kit (planned)
- **`/cli`** - Command Line Interface (planned)
- **`/api`** - REST API server (planned)

Each implementation shares core GraphQL integration patterns while providing platform-specific interfaces.

## Repository Structure

```
one-agent/                          # Brand/Product root
├── README.md                       # This file - product overview
├── .claude.md                      # Development guidelines
├── mcp/                           # MCP implementation
│   ├── README.md                  # MCP-specific documentation
│   ├── .claude.md                 # MCP development rules
│   └── src/                       # Python source code
└── _archive/                      # Archived implementations
    └── nodejs-mcp/                # Original TypeScript MCP
```

## Getting Started

1. **Choose your implementation** - Start with the MCP implementation for ChatGPT integration
2. **Follow implementation docs** - Each implementation has detailed setup instructions
3. **Configure your environment** - Set up API keys and GraphQL endpoints
4. **Start building** - Use OneAgent tools to create intelligent workflows

## Development

OneAgent is built with:
- **Python** for MCP implementation (FastMCP framework)
- **TypeScript** for archived Node.js implementation
- **GraphQL** for API integration
- **Modular architecture** for extensibility

## Contributing

We welcome contributions! Please see the implementation-specific documentation for development guidelines:
- [MCP Development Guide](./mcp/.claude.md)

## License

MIT License - see LICENSE file for details.

---

**OneAgent** - Making AI agents that actually work with your data.