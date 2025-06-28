#!/usr/bin/env python3
"""
SQL MCP Client
Connects to the SQL Server MCP server via stdio
"""

import asyncio
import json
import logging
import subprocess
import sys
from typing import Any, Dict, List, Optional
from mcp.client.stdio import stdio_client, StdioServerParameters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SQLMCPClient:
    def __init__(self, server_script_path: str = "servers/sql_server_mcp.py"):
        self.server_script_path = server_script_path
        self.session = None
        self.process = None
        self.stdio_context = None
        
    async def connect(self) -> bool:
        """Connect to SQL MCP server via stdio"""
        try:
            logger.info("Starting SQL MCP server process...")
            
            self.process = await asyncio.create_subprocess_exec(
                sys.executable, self.server_script_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            server_params = StdioServerParameters(
                command=sys.executable,
                args=[self.server_script_path]
            )
            
            self.stdio_context = stdio_client(server_params)
            read_stream, write_stream = await self.stdio_context.__aenter__()
            
            from mcp import ClientSession
            self.session = ClientSession(read_stream, write_stream)
            
            logger.info("Successfully connected to SQL MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to SQL MCP server: {e}")
            if self.process:
                self.process.terminate()
                await self.process.wait()
            return False
    
    async def connect_to_database(self, server: str, database: str, username: str = None, password: str = None) -> Dict[str, Any]:
        """Connect to SQL Server database"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            args = {
                "server": server,
                "database": database
            }
            
            if username and password:
                args["username"] = username
                args["password"] = password
            
            result = await self.session.call_tool("connect_database", args)
            logger.info(f"Database connection result: {result}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return {"error": str(e)}
    
    async def execute_query(self, query: str, parameters: List[str] = None) -> Dict[str, Any]:
        """Execute SQL query"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            args = {"query": query}
            if parameters:
                args["parameters"] = parameters
            
            result = await self.session.call_tool("execute_query", args)
            logger.info(f"Query executed successfully")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            return {"error": str(e)}
    
    async def list_tables(self) -> Dict[str, Any]:
        """List database tables"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            result = await self.session.read_resource("sql://tables")
            logger.info("Retrieved table list")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Failed to list tables: {e}")
            return {"error": str(e)}
    
    async def list_schemas(self) -> Dict[str, Any]:
        """List database schemas"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            result = await self.session.read_resource("sql://schemas")
            logger.info("Retrieved schema list")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Failed to list schemas: {e}")
            return {"error": str(e)}
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from SQL MCP server"""
        if not self.session:
            return []
        
        try:
            tools = await self.session.list_tools()
            logger.info(f"Found {len(tools)} tools")
            return [{"name": tool.name, "description": tool.description} for tool in tools]
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of available resources from SQL MCP server"""
        if not self.session:
            return []
        
        try:
            resources = await self.session.list_resources()
            logger.info(f"Found {len(resources)} resources")
            return [{"uri": resource.uri, "name": resource.name, "description": resource.description} for resource in resources]
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def disconnect(self):
        """Disconnect from SQL MCP server"""
        try:
            if self.session:
                await self.session.close()
            
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
            
            if self.process:
                self.process.terminate()
                await self.process.wait()
            
            logger.info("Disconnected from SQL MCP server")
            
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")

async def main():
    """Demo usage of SQL MCP Client"""
    client = SQLMCPClient()
    
    try:
        if await client.connect():
            print("✓ Connected to SQL MCP server")
            
            tools = await client.get_available_tools()
            print(f"✓ Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            resources = await client.get_available_resources()
            print(f"✓ Available resources ({len(resources)}):")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['description']}")
            
            print("\n--- Database Connection Demo ---")
            db_result = await client.connect_to_database(
                server="localhost",
                database="test_db"
            )
            
            if db_result.get("success"):
                print("✓ Connected to database")
                
                query_result = await client.execute_query("SELECT 1 as test_column")
                if query_result.get("success"):
                    print("✓ Query executed successfully")
                    print(f"Result: {query_result['result']}")
                else:
                    print(f"✗ Query failed: {query_result.get('error')}")
                
                tables_result = await client.list_tables()
                if tables_result.get("success"):
                    print("✓ Retrieved table list")
                    print(f"Tables: {tables_result['result']}")
                
            else:
                print(f"✗ Database connection failed: {db_result.get('error')}")
            
        else:
            print("✗ Failed to connect to SQL MCP server")
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
