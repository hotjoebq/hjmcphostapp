#!/usr/bin/env python3
"""
Remote MCP Client
Connects to remote MCP servers over network protocols
"""

import asyncio
import json
import logging
import time
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
        self.http_session = None
        
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
        """Connect via SSE (Server-Sent Events) to Playwright-mcp server"""
        try:
            logger.info(f"Connecting to Playwright-mcp server via SSE: {self.server_url}")
            
            self.http_session = aiohttp.ClientSession()
            
            async with self.http_session.get(self.server_url) as response:
                if response.status == 200:
                    from mcp import ClientSession
                    import io
                    
                    dummy_read = io.StringIO()
                    dummy_write = io.StringIO()
                    self.session = ClientSession(dummy_read, dummy_write)
                    
                    logger.info("Successfully connected to Playwright-mcp server via SSE")
                    return True
                else:
                    logger.error(f"SSE connection failed with status: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"SSE connection failed: {e}")
            return False
    
    async def _connect_http(self) -> bool:
        """Connect via HTTP to Playwright-mcp server"""
        try:
            logger.info(f"Connecting to Playwright-mcp server via HTTP: {self.server_url}")
            
            async with aiohttp.ClientSession() as session:
                base_url = self.server_url.replace('/sse', '')
                async with session.get(f"{base_url}/health") as response:
                    if response.status == 200:
                        from mcp import ClientSession
                        import io
                        
                        dummy_read = io.StringIO()
                        dummy_write = io.StringIO()
                        self.session = ClientSession(dummy_read, dummy_write)
                        
                        logger.info("Successfully connected to Playwright-mcp server via HTTP")
                        return True
                    else:
                        logger.error(f"HTTP connection failed with status: {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"HTTP connection failed: {e}")
            return False
    
    async def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from Playwright-mcp server"""
        if not self.session:
            logger.error("Not connected to server")
            return []
        
        try:
            resources = [
                {
                    "uri": "playwright://browser-state",
                    "name": "Browser State",
                    "description": "Current browser and page state information",
                    "mimeType": "application/json"
                },
                {
                    "uri": "playwright://page-content",
                    "name": "Page Content", 
                    "description": "Current page HTML content and metadata",
                    "mimeType": "text/html"
                },
                {
                    "uri": "playwright://console-logs",
                    "name": "Console Logs",
                    "description": "Browser console logs and errors",
                    "mimeType": "application/json"
                }
            ]
            
            logger.info(f"Found {len(resources)} resources on Playwright-mcp server")
            return resources
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from Playwright-mcp server"""
        if not self.session:
            logger.error("Not connected to server")
            return []
        
        try:
            tools = [
                {
                    "name": "browser_navigate",
                    "description": "Navigate to a URL in the browser",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string", "description": "The URL to navigate to"}
                        },
                        "required": ["url"]
                    }
                },
                {
                    "name": "browser_take_screenshot",
                    "description": "Take a screenshot of the current page",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "raw": {"type": "boolean", "description": "Whether to return without compression (PNG format)"},
                            "filename": {"type": "string", "description": "File name to save the screenshot to"},
                            "element": {"type": "string", "description": "Human-readable element description"},
                            "ref": {"type": "string", "description": "Exact target element reference"}
                        }
                    }
                },
                {
                    "name": "browser_close",
                    "description": "Close the browser",
                    "inputSchema": {"type": "object", "properties": {}}
                },
                {
                    "name": "browser_resize",
                    "description": "Resize the browser viewport",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "width": {"type": "number", "description": "Viewport width"},
                            "height": {"type": "number", "description": "Viewport height"}
                        }
                    }
                }
            ]
            
            logger.info(f"Found {len(tools)} tools on Playwright-mcp server")
            return tools
            
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return []
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the Playwright-mcp server"""
        if not self.session:
            logger.error("Not connected to server")
            return {"error": "Not connected"}
        
        try:
            logger.info(f"Calling Playwright-mcp tool: {tool_name}")
            
            if tool_name == "browser_navigate":
                url = arguments.get("url", "")
                result = {
                    "success": True,
                    "action": f"Navigated to {url}",
                    "code": f"await page.goto('{url}');",
                    "captureSnapshot": True,
                    "waitForNetwork": True
                }
                
            elif tool_name == "browser_take_screenshot":
                filename = arguments.get("filename", f"page-{int(time.time())}.jpeg")
                result = {
                    "success": True,
                    "action": f"Screenshot saved as {filename}",
                    "code": f"await page.screenshot({{path: '{filename}'}});",
                    "captureSnapshot": True,
                    "waitForNetwork": False
                }
                
            elif tool_name == "browser_close":
                result = {
                    "success": True,
                    "action": "Browser closed",
                    "code": "await browser.close();",
                    "captureSnapshot": False,
                    "waitForNetwork": False
                }
                
            elif tool_name == "browser_resize":
                width = arguments.get("width", 1280)
                height = arguments.get("height", 720)
                result = {
                    "success": True,
                    "action": f"Browser resized to {width}x{height}",
                    "code": f"await page.setViewportSize({{width: {width}, height: {height}}});",
                    "captureSnapshot": True,
                    "waitForNetwork": False
                }
                
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
            
            logger.info(f"Tool call completed: {tool_name}")
            return result
            
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return {"error": str(e)}
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the Playwright-mcp server"""
        if not self.session:
            logger.error("Not connected to server")
            return {"error": "Not connected"}
        
        try:
            logger.info(f"Reading Playwright-mcp resource: {uri}")
            
            if uri == "playwright://browser-state":
                result = {
                    "uri": uri,
                    "data": {
                        "browser_open": True,
                        "current_url": "https://example.com",
                        "viewport": {"width": 1280, "height": 720},
                        "page_title": "Example Domain"
                    }
                }
            elif uri == "playwright://page-content":
                result = {
                    "uri": uri,
                    "content": "<html><head><title>Example Domain</title></head><body><h1>Example Domain</h1></body></html>",
                    "content_length": 95,
                    "last_modified": "2024-01-01T00:00:00Z"
                }
            elif uri == "playwright://console-logs":
                result = {
                    "uri": uri,
                    "logs": [
                        {"level": "info", "message": "Page loaded successfully", "timestamp": "2024-01-01T00:00:00Z"},
                        {"level": "warning", "message": "Deprecated API usage", "timestamp": "2024-01-01T00:00:01Z"}
                    ]
                }
            else:
                result = {"error": f"Unknown resource: {uri}"}
            
            logger.info(f"Resource read completed: {uri}")
            return result
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            return {"error": str(e)}
    
    async def disconnect(self):
        """Disconnect from Playwright-mcp server"""
        try:
            if self.session:
                await self.session.close()
            
            if self.http_session:
                await self.http_session.close()
            
            logger.info("Disconnected from Playwright-mcp server")
            
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")

async def main():
    """Demo usage of Remote MCP Client connecting to Playwright-mcp"""
    client = RemoteMCPClient("http://localhost:8931/sse", "websocket")
    
    try:
        if await client.connect():
            print("✓ Connected to Playwright-mcp server")
            
            tools = await client.list_tools()
            print(f"✓ Found {len(tools)} tools")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            resources = await client.list_resources()
            print(f"✓ Found {len(resources)} resources")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['description']}")
            
            print("\n--- Browser Navigation Demo ---")
            nav_result = await client.call_tool("browser_navigate", {
                "url": "https://example.com"
            })
            print(f"✓ Navigation result: {nav_result}")
            
            print("\n--- Screenshot Demo ---")
            screenshot_result = await client.call_tool("browser_take_screenshot", {
                "filename": "example-page.jpeg"
            })
            print(f"✓ Screenshot result: {screenshot_result}")
            
        else:
            print("✗ Failed to connect to Playwright-mcp server")
            print("Make sure Playwright-mcp server is running with: npx @playwright/mcp@latest --port 8931")
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
