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
