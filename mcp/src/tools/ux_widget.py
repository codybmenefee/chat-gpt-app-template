"""
Hello World Widget for ChatGPT App Template.
Implements proper OpenAI Apps SDK widget pattern with resource registration.
"""

from fastmcp import FastMCP

def register_ux_widget_tools(mcp: FastMCP):
    """Register hello world widget tools with FastMCP."""
    
    # Register the widget resource
    @mcp.resource(
        uri="ui://widget/hello-world.html",
        name="hello-world-widget",
        title="Hello World Widget",
        description="A simple hello world widget demonstrating ChatGPT custom UI",
        mime_type="text/html+skybridge"
    )
    def hello_world_widget_resource():
        """Return the HTML content for the hello world widget."""
        return """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Hello World Widget</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: system-ui, -apple-system, sans-serif;
            background-color: var(--bg-color, #ffffff);
            color: var(--text-color, #000000);
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            background: white;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        .header {
            font-size: 24px;
            font-weight: 600;
            margin-bottom: 20px;
            color: #0066cc;
            text-align: center;
        }
        .content {
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        .info {
            background-color: #f5f5f5;
            padding: 12px;
            border-radius: 8px;
            font-size: 14px;
            color: #666;
        }
        .button {
            padding: 8px 16px;
            margin: 4px;
            border: none;
            border-radius: 6px;
            background-color: #0066cc;
            color: white;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        .button:hover {
            background-color: #0052a3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">🎉 Hello World Widget!</div>
        
        <div class="content">
            <p>This is a simple "Hello World" widget demonstrating ChatGPT's custom UI capabilities.</p>
            <p>The widget is rendered inline in the ChatGPT conversation using OpenAI's Apps SDK.</p>
        </div>

        <div class="info">
            <strong>Widget Features:</strong>
            <ul>
                <li>Renders inline in ChatGPT conversation</li>
                <li>Uses proper MCP resource registration</li>
                <li>Demonstrates window.openai API integration</li>
                <li>Simple HTML/CSS/JS implementation</li>
            </ul>
        </div>

        <div style="text-align: center; margin-top: 20px;">
            <button class="button" onclick="showMessage()">Click Me!</button>
            <button class="button" onclick="requestFullscreen()">Request Fullscreen</button>
        </div>
    </div>

    <script>
        // Simple window.openai integration demo
        function showMessage() {
            if (window.openai) {
                alert('Hello from the widget! window.openai is available.');
                console.log('window.openai:', window.openai);
            } else {
                alert('Hello from the widget! (window.openai not available in this context)');
            }
        }

        function requestFullscreen() {
            if (window.openai?.requestDisplayMode) {
                window.openai.requestDisplayMode({ mode: 'fullscreen' });
            } else {
                alert('Request Fullscreen clicked! (window.openai.requestDisplayMode not available)');
            }
        }

        // Listen for window.openai changes
        window.addEventListener('openai:set_globals', (event) => {
            console.log('OpenAI globals updated:', event.detail);
        });

        // Initialize
        console.log('Hello World Widget loaded!');
        if (window.openai) {
            console.log('window.openai available:', window.openai);
        }
    </script>
</body>
</html>
        """.strip()

    # Register the tool that uses the widget
    @mcp.tool(
        name="hello_world_widget",
        title="Hello World Widget",
        description="Display a simple hello world widget in ChatGPT",
        meta={
            "openai/outputTemplate": "ui://widget/hello-world.html",
            "openai/toolInvocation/invoking": "Loading Hello World widget...",
            "openai/toolInvocation/invoked": "Hello World widget displayed!"
        }
    )
    def hello_world_widget():
        """Display a hello world widget in ChatGPT."""
        return {
            "content": [
                {
                    "type": "text",
                    "text": "Hello World Widget Demo\n\nThis widget demonstrates ChatGPT's custom UI capabilities with a simple inline component."
                }
            ],
            "structuredContent": {}
        }
