# Simple ChatGPT App Template

A minimal template for building ChatGPT apps using FastMCP. This template demonstrates both simple function tools and custom UI widgets.

## Features

- **Simple Math Tool**: Add two numbers together
- **Hello World Widget**: Custom UI component that renders inline in ChatGPT
- **Minimal Setup**: No API keys or complex configuration required
- **Easy to Extend**: Clean structure for adding more tools

## Quick Start

### Prerequisites

- Python 3.8 or higher

### Installation

1. **Clone this template:**

   ```bash
   git clone <your-repo-url>
   cd simple-chatgpt-template
   ```

2. **Set up Python environment:**

   ```bash
   cd mcp
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the MCP server:**

   ```bash
   python src/main.py
   ```

4. **Connect to ChatGPT:**
   - Open ChatGPT
   - Go to Settings → Apps → Add App
   - Enter your server URL: `https://your-ngrok-url.ngrok.io/mcp`
   - Test the tools!

## Local Development with ChatGPT

For local development, ChatGPT needs to access your MCP server over the internet. Use ngrok to create a secure tunnel to your local server.

## Available Tools

### `add_numbers`

Adds two numbers together and returns a formatted result.

**Example:**

```text
Use the add_numbers tool to calculate 5 + 3
```

### `hello_world_widget`

Displays a custom UI widget inline in ChatGPT conversation.

**Example:**

```text
Use the hello_world_widget tool to show the demo widget
```

## How to Extend

### Adding a New Tool

1. **Create a new tool file** in `mcp/src/tools/`:

   ```python
   # my_tools.py
   from fastmcp import FastMCP
   
   def register_my_tools(mcp: FastMCP):
       @mcp.tool(
           name="my_tool",
           title="My Tool",
           description="What my tool does"
       )
       def my_tool(param: str) -> str:
           return f"Result: {param}"
   ```

2. **Import and register** in `main.py`:

   ```python
   from tools.my_tools import register_my_tools
   
   # In main.py
   register_my_tools(mcp)
   ```

3. **Test your tool** in ChatGPT!

### Adding a Custom Widget

1. **Create widget HTML** in your tool file:

   ```python
   @mcp.resource(
       uri="ui://widget/my-widget.html",
       name="my-widget",
       title="My Widget",
       description="My custom widget",
       mime_type="text/html+skybridge"
   )
   def my_widget_resource():
       return """
       <!DOCTYPE html>
       <html>
       <head><title>My Widget</title></head>
       <body>
           <h1>Hello from my widget!</h1>
       </body>
       </html>
       """
   ```

2. **Create tool** that uses the widget:

   ```python
   @mcp.tool(
       name="my_widget",
       title="My Widget",
       description="Display my custom widget",
       meta={
           "openai/outputTemplate": "ui://widget/my-widget.html"
       }
   )
   def my_widget():
       return {"content": [{"type": "text", "text": "Widget loaded!"}]}
   ```

## Project Structure

```text
simple-chatgpt-template/
├── README.md                 # This file
└── mcp/                     # MCP server implementation
    ├── src/
    │   ├── main.py          # Main server entry point
    │   └── tools/
    │       ├── math_tools.py    # Math operations
    │       └── ux_widget.py     # Hello world widget
    ├── requirements.txt     # Python dependencies
    └── README.md           # MCP-specific documentation
```

## Development

### Testing with ChatGPT

1. Start your MCP server
2. Expose it with ngrok: `ngrok http 8123`
3. In ChatGPT, go to Settings → Apps
4. Add a new app with URL: `https://your-ngrok-url.ngrok.io/mcp`
5. Test your tools in conversation

## Troubleshooting

### Server Won't Start

- Check Python version (3.8+ required)
- Verify all dependencies installed: `pip install -r requirements.txt`

### ChatGPT Can't Connect

- Verify server is running: `curl http://localhost:8123/mcp`
- Verify ngrok tunnel is open
- Check firewall settings

### Tools Not Working

- Check server logs for errors
- Verify tool registration in `main.py`
- Test tools individually

## License

MIT License - feel free to use this template for your own projects!

---

**LFG!** 🚀
