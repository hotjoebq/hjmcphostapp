# MCP Host Application

This application demonstrates Model Context Protocol (MCP) architecture with:

## Architecture

### MCP Servers
1. **SQL Server MCP Server** - Connects to SQL Server via stdio
2. **Internet Search MCP Server** - Provides internet search capabilities

### MCP Clients
1. **Remote MCP Client** - Connects to remote MCP servers
2. **SQL MCP Client** - Connects to the SQL Server MCP server
3. **Internet MCP Client** - Connects to the Internet Search MCP server

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Usage

### Running the Main Application
```bash
python3 main.py
```

### Running Individual Clients

#### Remote MCP Client (Playwright-mcp)
The Remote MCP Client connects to a Playwright-mcp server for browser automation.

**Prerequisites:**
1. Install Playwright-mcp server:
   ```bash
   npm install -g @playwright/mcp@latest
   ```

2. Start Playwright-mcp server:
   ```bash
   npx @playwright/mcp@latest --port 8931
   ```

3. Run the Remote MCP Client:
   ```bash
   python3 clients/remote_client.py
   ```

**Available Tools:**
- `browser_navigate` - Navigate to URLs
- `browser_take_screenshot` - Take page screenshots
- `browser_close` - Close browser instance
- `browser_resize` - Resize browser viewport

**Available Resources:**
- `playwright://browser-state` - Browser state and viewport information
- `playwright://page-content` - Current page HTML content
- `playwright://console-logs` - Browser console logs and errors

#### SQL Server MCP Client
```bash
python3 clients/sql_client.py
```

#### Internet Search MCP Client
```bash
python3 clients/internet_client.py
```

## Configuration

### SQL Server Connection
Update the connection string in `servers/sql_server_mcp.py`:
```python
connection_string = "Driver={ODBC Driver 17 for SQL Server};Server=your_server;Database=your_db;UID=your_user;PWD=your_password"
```

### Playwright-mcp Server
The Remote MCP Client is configured to connect to Playwright-mcp server by default:
```python
client = RemoteMCPClient("http://localhost:8931/sse", "websocket")
```

**Server Configuration Options:**
- **SSE Transport**: `http://localhost:8931/sse` (default)
- **Streamable HTTP**: `http://localhost:8931/mcp`
- **Stdio Transport**: Use command-line configuration

**Starting Playwright-mcp Server:**
```bash
# Default stdio mode
npx @playwright/mcp@latest

# SSE mode (recommended for Remote MCP Client)
npx @playwright/mcp@latest --port 8931

# Custom port
npx @playwright/mcp@latest --port 9000
```

## Structure

```
├── servers/
│   ├── sql_server_mcp.py      # SQL Server MCP Server
│   └── internet_mcp.py        # Internet Search MCP Server
├── clients/
│   ├── remote_client.py       # Remote MCP Client
│   ├── sql_client.py          # SQL MCP Client
│   └── internet_client.py     # Internet MCP Client
├── main.py                    # Main application entry point
└── requirements.txt           # Python dependencies
```
