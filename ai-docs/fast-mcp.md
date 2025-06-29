# The FastMCP Server

> Learn about the core FastMCP server class and how to run it.

export const VersionBadge = ({version}) => {
  return <code className="version-badge-container">
            <p className="version-badge">
                <span className="version-badge-label">New in version:</span> 
                <code className="version-badge-version">{version}</code>
            </p>
        </code>;
};

The central piece of a FastMCP application is the `FastMCP` server class. This class acts as the main container for your application's tools, resources, and prompts, and manages communication with MCP clients.

## Creating a Server

Instantiating a server is straightforward. You typically provide a name for your server, which helps identify it in client applications or logs.

```python
from fastmcp import FastMCP

# Create a basic server instance
mcp = FastMCP(name="MyAssistantServer")

# You can also add instructions for how to interact with the server
mcp_with_instructions = FastMCP(
    name="HelpfulAssistant",
    instructions="""
        This server provides data analysis tools.
        Call get_average() to analyze numerical data.
    """,
)
```

The `FastMCP` constructor accepts several arguments:

* `name`: (Optional) A human-readable name for your server. Defaults to "FastMCP".
* `instructions`: (Optional) Description of how to interact with this server. These instructions help clients understand the server's purpose and available functionality.
* `lifespan`: (Optional) An async context manager function for server startup and shutdown logic.
* `tags`: (Optional) A set of strings to tag the server itself.
* `tools`: (Optional) A list of tools (or functions to convert to tools) to add to the server. In some cases, providing tools programmatically may be more convenient than using the `@mcp.tool` decorator.
* `**settings`: Keyword arguments corresponding to additional `ServerSettings` configuration

## Components

FastMCP servers expose several types of components to the client:

### Tools

Tools are functions that the client can call to perform actions or access external systems.

```python
@mcp.tool
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers together."""
    return a * b
```

See [Tools](/servers/tools) for detailed documentation.

### Resources

Resources expose data sources that the client can read.

```python
@mcp.resource("data://config")
def get_config() -> dict:
    """Provides the application configuration."""
    return {"theme": "dark", "version": "1.0"}
```

See [Resources & Templates](/servers/resources) for detailed documentation.

### Resource Templates

Resource templates are parameterized resources that allow the client to request specific data.

```python
@mcp.resource("users://{user_id}/profile")
def get_user_profile(user_id: int) -> dict:
    """Retrieves a user's profile by ID."""
    # The {user_id} in the URI is extracted and passed to this function
    return {"id": user_id, "name": f"User {user_id}", "status": "active"}
```

See [Resources & Templates](/servers/resources) for detailed documentation.

### Prompts

Prompts are reusable message templates for guiding the LLM.

```python
@mcp.prompt
def analyze_data(data_points: list[float]) -> str:
    """Creates a prompt asking for analysis of numerical data."""
    formatted_data = ", ".join(str(point) for point in data_points)
    return f"Please analyze these data points: {formatted_data}"
```

See [Prompts](/servers/prompts) for detailed documentation.

## Running the Server

FastMCP servers need a transport mechanism to communicate with clients. You typically start your server by calling the `mcp.run()` method on your `FastMCP` instance, often within an `if __name__ == "__main__":` block in your main server script. This pattern ensures compatibility with various MCP clients.

```python
# my_server.py
from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")

@mcp.tool
def greet(name: str) -> str:
    """Greet a user by name."""
    return f"Hello, {name}!"

if __name__ == "__main__":
    # This runs the server, defaulting to STDIO transport
    mcp.run()
    
    # To use a different transport, e.g., HTTP:
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=9000)
```

FastMCP supports several transport options:

* STDIO (default, for local tools)
* Streamable HTTP (recommended for web services)
* SSE (legacy web transport, deprecated)

The server can also be run using the FastMCP CLI.

For detailed information on each transport, how to configure them (host, port, paths), and when to use which, please refer to the [**Running Your FastMCP Server**](/deployment/running-server) guide.

## Composing Servers

<VersionBadge version="2.2.0" />

FastMCP supports composing multiple servers together using `import_server` (static copy) and `mount` (live link). This allows you to organize large applications into modular components or reuse existing servers.

See the [Server Composition](/servers/composition) guide for full details, best practices, and examples.

```python
# Example: Importing a subserver
from fastmcp import FastMCP
import asyncio

main = FastMCP(name="Main")
sub = FastMCP(name="Sub")

@sub.tool
def hello(): 
    return "hi"

# Mount directly
main.mount("sub", sub)
```

## Proxying Servers

<VersionBadge version="2.0.0" />

FastMCP can act as a proxy for any MCP server (local or remote) using `FastMCP.as_proxy`, letting you bridge transports or add a frontend to existing servers. For example, you can expose a remote SSE server locally via stdio, or vice versa.

See the [Proxying Servers](/servers/proxy) guide for details and advanced usage.

```python
from fastmcp import FastMCP, Client

backend = Client("http://example.com/mcp/sse")
proxy = FastMCP.as_proxy(backend, name="ProxyServer")
# Now use the proxy like any FastMCP server
```

## Server Configuration

Server behavior, like transport settings (host, port for SSE) and how duplicate components are handled, can be configured via `ServerSettings`. These settings can be passed during `FastMCP` initialization, set via environment variables (prefixed with `FASTMCP_SERVER_`), or loaded from a `.env` file.

```python
from fastmcp import FastMCP

# Configure during initialization
mcp = FastMCP(
    name="ConfiguredServer",
    port=8080, # Directly maps to ServerSettings
    on_duplicate_tools="error" # Set duplicate handling
)

# Settings are accessible via mcp.settings
print(mcp.settings.port) # Output: 8080
print(mcp.settings.on_duplicate_tools) # Output: "error"
```

### Key Configuration Options

* **`host`**: Host address for SSE transport (default: "127.0.0.1")
* **`port`**: Port number for SSE transport (default: 8000)
* **`log_level`**: Logging level (default: "INFO")
* **`on_duplicate_tools`**: How to handle duplicate tool registrations
* **`on_duplicate_resources`**: How to handle duplicate resource registrations
* **`on_duplicate_prompts`**: How to handle duplicate prompt registrations

All of these can be configured directly as parameters when creating the `FastMCP` instance.

### Custom Tool Serialization

<VersionBadge version="2.2.7" />

By default, FastMCP serializes tool return values to JSON when they need to be converted to text. You can customize this behavior by providing a `tool_serializer` function when creating your server:

```python
import yaml
from fastmcp import FastMCP

# Define a custom serializer that formats dictionaries as YAML
def yaml_serializer(data):
    return yaml.dump(data, sort_keys=False)

# Create a server with the custom serializer
mcp = FastMCP(name="MyServer", tool_serializer=yaml_serializer)

@mcp.tool
def get_config():
    """Returns configuration in YAML format."""
    return {"api_key": "abc123", "debug": True, "rate_limit": 100}
```

The serializer function takes any data object and returns a string representation. This is applied to **all non-string return values** from your tools. Tools that already return strings bypass the serializer.

This customization is useful when you want to:

* Format data in a specific way (like YAML or custom formats)
* Control specific serialization options (like indentation or sorting)
* Add metadata or transform data before sending it to clients

<Tip>
  If the serializer function raises an exception, the tool will fall back to the default JSON serialization to avoid breaking the server.
</Tip>
