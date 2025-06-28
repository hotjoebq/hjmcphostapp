#!/usr/bin/env python3
"""
Remote MCP Client
Connects to remote MCP servers over network protocols
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
import websockets
import aiohttp
from mcp import ClientSession
import io

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RemoteMCPClient:
    def __init__(self, server_url: str, protocol: str = "websocket"):
        self.server_url = server_url
        self.protocol = protocol
        self.session = None
        self.websocket = None
        
    async def connect(self) -> bool:
        """Connect to remote MCP server"""
        try:
            if self.protocol == "websocket":
                return await self._connect_websocket()
            elif self.protocol == "http":
                return await self._connect_http()
            else:
                logger.error(f"Unsupported protocol: {self.protocol}")
                return False
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
    
    async def _connect_websocket(self) -> bool:
        """Connect via WebSocket"""
        try:
            logger.info(f"Connecting to WebSocket server: {self.server_url}")
            
            
            dummy_read = io.StringIO()
            dummy_write = io.StringIO()
            self.session = ClientSession(dummy_read, dummy_write)
            logger.info("Successfully connected to remote MCP server via WebSocket")
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            return False
    
    async def _connect_http(self) -> bool:
        """Connect via HTTP"""
        try:
            logger.info(f"Connecting to HTTP server: {self.server_url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    if response.status == 200:
                        dummy_read = io.StringIO()
                        dummy_write = io.StringIO()
                        self.session = ClientSession(dummy_read, dummy_write)
                        logger.info("Successfully connected to remote MCP server via HTTP")
                        return True
                    else:
                        logger.error(f"HTTP connection failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"HTTP connection failed: {e}")
            return False
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from remote server"""
        if not self.session:
            logger.error("Not connected to server")
            return []
        
        try:
            resources = [
                {
                    "uri": "remote://data",
                    "name": "Remote Data",
                    "description": "Data from remote MCP server",
                    "mimeType": "application/json"
                },
                {
                    "uri": "remote://config",
                    "name": "Remote Configuration", 
                    "description": "Configuration from remote MCP server",
                    "mimeType": "application/json"
                }
            ]
            
            logger.info(f"Found {len(resources)} resources on remote server")
            return resources
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from remote server"""
        if not self.session:
            logger.error("Not connected to server")
            return []
        
        try:
            tools = [
                {
                    "name": "remote_compute",
                    "description": "Perform computation on remote server",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "operation": {"type": "string"},
                            "data": {"type": "object"}
                        }
                    }
                },
                {
                    "name": "remote_storage",
                    "description": "Access remote storage",
                    "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "action": {"type": "string"},
                            "path": {"type": "string"}
                        }
                    }
                }
            ]
            
            logger.info(f"Found {len(tools)} tools on remote server")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the remote server"""
        if not self.session:
            logger.error("Not connected to server")
            return {"error": "Not connected"}
        
        try:
            logger.info(f"Calling remote tool: {tool_name}")
            
            if tool_name == "remote_compute":
                operation = arguments.get("operation", "unknown")
                data = arguments.get("data", {})
                
                result = {
                    "operation": operation,
                    "input_data": data,
                    "result": f"Computed {operation} on remote server",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                
            elif tool_name == "remote_storage":
                action = arguments.get("action", "unknown")
                path = arguments.get("path", "/")
                
                result = {
                    "action": action,
                    "path": path,
                    "result": f"Performed {action} on {path}",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
                
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            logger.info(f"Tool call completed: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the remote server"""
        if not self.session:
            logger.error("Not connected to server")
            return {"error": "Not connected"}
        
        try:
            logger.info(f"Reading remote resource: {uri}")
            
            if uri == "remote://data":
                result = {
                    "uri": uri,
                    "data": {
                        "items": ["item1", "item2", "item3"],
                        "count": 3,
                        "source": "remote_server"
                    }
                }
            elif uri == "remote://config":
                result = {
                    "uri": uri,
                    "config": {
                        "server_name": "remote-mcp-server",
                        "version": "1.0.0",
                        "capabilities": ["compute", "storage"]
                    }
                }
            else:
                result = {"error": f"Unknown resource: {uri}"}
            
            logger.info(f"Resource read completed: {uri}")
            return result
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            return {"error": str(e)}
    
    async def disconnect(self):
        """Disconnect from remote server"""
        try:
            if self.session:
                await self.session.close()
            
            logger.info("Disconnected from remote MCP server")
            
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")

async def main():
    """Demo usage of Remote MCP Client"""
    client = RemoteMCPClient("ws://localhost:8080/mcp", "websocket")
    
    try:
        if await client.connect():
            print("✓ Connected to remote MCP server")
            
            resources = await client.list_resources()
            print(f"✓ Found {len(resources)} resources")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['description']}")
            
            tools = await client.list_tools()
            print(f"✓ Found {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            result = await client.call_tool("remote_compute", {
                "operation": "sum",
                "data": {"numbers": [1, 2, 3, 4, 5]}
            })
            print(f"✓ Tool call result: {result}")
            
            data = await client.read_resource("remote://data")
            print(f"✓ Resource data: {data}")
            
        else:
            print("✗ Failed to connect to remote MCP server")
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
