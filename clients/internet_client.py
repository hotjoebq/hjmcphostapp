#!/usr/bin/env python3
"""
Internet MCP Client
Connects to the Internet Search MCP server
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

class InternetMCPClient:
    def __init__(self, server_script_path: str = "servers/internet_mcp.py"):
        self.server_script_path = server_script_path
        self.session = None
        self.process = None
        self.stdio_context = None
        
    async def connect(self) -> bool:
        """Connect to Internet MCP server via stdio"""
        try:
            logger.info("Starting Internet MCP server process...")
            
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
            
            logger.info("Successfully connected to Internet MCP server")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Internet MCP server: {e}")
            if self.process:
                self.process.terminate()
                await self.process.wait()
            return False
    
    async def web_search(self, query: str, num_results: int = 10) -> Dict[str, Any]:
        """Perform web search"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            args = {
                "query": query,
                "num_results": num_results
            }
            
            result = await self.session.call_tool("web_search", args)
            logger.info(f"Web search completed for query: {query}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Web search failed: {e}")
            return {"error": str(e)}
    
    async def fetch_url(self, url: str, timeout: int = 30) -> Dict[str, Any]:
        """Fetch content from URL"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            args = {
                "url": url,
                "timeout": timeout
            }
            
            result = await self.session.call_tool("fetch_url", args)
            logger.info(f"URL fetched successfully: {url}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"URL fetch failed: {e}")
            return {"error": str(e)}
    
    async def get_page_content(self, url: str, extract_links: bool = False) -> Dict[str, Any]:
        """Extract text content from webpage"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            args = {
                "url": url,
                "extract_links": extract_links
            }
            
            result = await self.session.call_tool("get_page_content", args)
            logger.info(f"Page content extracted from: {url}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Page content extraction failed: {e}")
            return {"error": str(e)}
    
    async def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools from Internet MCP server"""
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
        """Get list of available resources from Internet MCP server"""
        if not self.session:
            return []
        
        try:
            resources = await self.session.list_resources()
            logger.info(f"Found {len(resources)} resources")
            return [{"uri": resource.uri, "name": resource.name, "description": resource.description} for resource in resources]
            
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
            return []
    
    async def read_resource(self, uri: str) -> Dict[str, Any]:
        """Read a resource from the Internet MCP server"""
        if not self.session:
            return {"error": "Not connected to MCP server"}
        
        try:
            result = await self.session.read_resource(uri)
            logger.info(f"Resource read: {uri}")
            return {"success": True, "result": result}
            
        except Exception as e:
            logger.error(f"Resource read failed: {e}")
            return {"error": str(e)}
    
    async def disconnect(self):
        """Disconnect from Internet MCP server"""
        try:
            if self.session:
                await self.session.close()
            
            if self.stdio_context:
                await self.stdio_context.__aexit__(None, None, None)
            
            if self.process:
                self.process.terminate()
                await self.process.wait()
            
            logger.info("Disconnected from Internet MCP server")
            
        except Exception as e:
            logger.error(f"Disconnect failed: {e}")

async def main():
    """Demo usage of Internet MCP Client"""
    client = InternetMCPClient()
    
    try:
        if await client.connect():
            print("✓ Connected to Internet MCP server")
            
            tools = await client.get_available_tools()
            print(f"✓ Available tools ({len(tools)}):")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
            
            resources = await client.get_available_resources()
            print(f"✓ Available resources ({len(resources)}):")
            for resource in resources:
                print(f"  - {resource['name']}: {resource['description']}")
            
            print("\n--- Web Search Demo ---")
            search_result = await client.web_search("Python MCP protocol", 5)
            if search_result.get("success"):
                print("✓ Web search completed")
                result_data = json.loads(search_result['result'][0].text) if search_result['result'] else {}
                print(f"Query: {result_data.get('query', 'N/A')}")
                print(f"Abstract: {result_data.get('abstract', 'N/A')[:200]}...")
            else:
                print(f"✗ Web search failed: {search_result.get('error')}")
            
            print("\n--- URL Fetch Demo ---")
            url_result = await client.fetch_url("https://httpbin.org/json")
            if url_result.get("success"):
                print("✓ URL fetch completed")
                result_data = json.loads(url_result['result'][0].text) if url_result['result'] else {}
                print(f"Status: {result_data.get('status', 'N/A')}")
                print(f"Content length: {result_data.get('content_length', 'N/A')}")
            else:
                print(f"✗ URL fetch failed: {url_result.get('error')}")
            
            print("\n--- Page Content Demo ---")
            content_result = await client.get_page_content("https://httpbin.org/html", True)
            if content_result.get("success"):
                print("✓ Page content extraction completed")
                result_data = json.loads(content_result['result'][0].text) if content_result['result'] else {}
                print(f"Title: {result_data.get('title', 'N/A')}")
                print(f"Content length: {result_data.get('content_length', 'N/A')}")
                links = result_data.get('links', [])
                print(f"Links found: {len(links)}")
            else:
                print(f"✗ Page content extraction failed: {content_result.get('error')}")
            
        else:
            print("✗ Failed to connect to Internet MCP server")
            
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
