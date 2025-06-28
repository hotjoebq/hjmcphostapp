#!/usr/bin/env python3
"""
SQL Server MCP Server
Provides MCP server functionality for SQL Server connections via stdio
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional
import pyodbc
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLServerMCPServer:
    def __init__(self):
        self.server = Server("sql-server-mcp")
        self.connection_string = None
        self.connection = None
        
    async def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available SQL Server resources"""
            return [
                Resource(
                    uri="sql://tables",
                    name="Database Tables",
                    description="List all tables in the database",
                    mimeType="application/json"
                ),
                Resource(
                    uri="sql://schemas",
                    name="Database Schemas", 
                    description="List all schemas in the database",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read SQL Server resource"""
            if not self.connection:
                return json.dumps({"error": "No database connection"})
                
            try:
                cursor = self.connection.cursor()
                
                if uri == "sql://tables":
                    cursor.execute("""
                        SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE 
                        FROM INFORMATION_SCHEMA.TABLES
                        ORDER BY TABLE_SCHEMA, TABLE_NAME
                    """)
                    tables = []
                    for row in cursor.fetchall():
                        tables.append({
                            "schema": row[0],
                            "name": row[1], 
                            "type": row[2]
                        })
                    return json.dumps({"tables": tables})
                    
                elif uri == "sql://schemas":
                    cursor.execute("""
                        SELECT SCHEMA_NAME 
                        FROM INFORMATION_SCHEMA.SCHEMATA
                        ORDER BY SCHEMA_NAME
                    """)
                    schemas = [row[0] for row in cursor.fetchall()]
                    return json.dumps({"schemas": schemas})
                    
                else:
                    return json.dumps({"error": f"Unknown resource: {uri}"})
                    
            except Exception as e:
                logger.error(f"Error reading resource {uri}: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available SQL Server tools"""
            return [
                Tool(
                    name="execute_query",
                    description="Execute a SQL query on the connected database",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "SQL query to execute"
                            },
                            "parameters": {
                                "type": "array",
                                "description": "Query parameters",
                                "items": {"type": "string"}
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="connect_database",
                    description="Connect to SQL Server database",
                    inputSchema={
                        "type": "object", 
                        "properties": {
                            "server": {"type": "string", "description": "SQL Server instance"},
                            "database": {"type": "string", "description": "Database name"},
                            "username": {"type": "string", "description": "Username"},
                            "password": {"type": "string", "description": "Password"}
                        },
                        "required": ["server", "database"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "connect_database":
                    return await self._connect_database(arguments)
                elif name == "execute_query":
                    return await self._execute_query(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _connect_database(self, args: Dict[str, Any]) -> List[TextContent]:
        """Connect to SQL Server database"""
        try:
            server = args.get("server")
            database = args.get("database") 
            username = args.get("username")
            password = args.get("password")
            
            if username and password:
                self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}"
            else:
                self.connection_string = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes"
            
            self.connection = pyodbc.connect(self.connection_string)
            return [TextContent(type="text", text=f"Successfully connected to {server}/{database}")]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Connection failed: {str(e)}")]
    
    async def _execute_query(self, args: Dict[str, Any]) -> List[TextContent]:
        """Execute SQL query"""
        if not self.connection:
            return [TextContent(type="text", text="No database connection. Please connect first.")]
        
        try:
            query = args.get("query")
            parameters = args.get("parameters", [])
            
            cursor = self.connection.cursor()
            
            if parameters:
                cursor.execute(query, parameters)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                result = {
                    "columns": columns,
                    "rows": [list(row) for row in rows],
                    "row_count": len(rows)
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            else:
                self.connection.commit()
                return [TextContent(type="text", text=f"Query executed successfully. Rows affected: {cursor.rowcount}")]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Query execution failed: {str(e)}")]

async def main():
    """Main entry point for SQL Server MCP Server"""
    server_instance = SQLServerMCPServer()
    await server_instance.setup_handlers()
    
    async with stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            server_instance.server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
