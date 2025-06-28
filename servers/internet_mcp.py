#!/usr/bin/env python3
"""
Internet Search MCP Server
Provides MCP server functionality for internet search capabilities
"""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional
import aiohttp
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, Tool, TextContent, ImageContent, EmbeddedResource

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InternetSearchMCPServer:
    def __init__(self):
        self.server = Server("internet-search-mcp")
        self.session = None
        
    async def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_resources()
        async def list_resources() -> List[Resource]:
            """List available internet search resources"""
            return [
                Resource(
                    uri="search://web",
                    name="Web Search",
                    description="Search the web for information",
                    mimeType="application/json"
                ),
                Resource(
                    uri="search://news",
                    name="News Search",
                    description="Search for recent news articles",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def read_resource(uri: str) -> str:
            """Read internet search resource"""
            return json.dumps({
                "message": f"Use the search tools to query {uri}",
                "available_tools": ["web_search", "fetch_url", "get_page_content"]
            })
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """List available internet search tools"""
            return [
                Tool(
                    name="web_search",
                    description="Search the web using a search engine",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "num_results": {
                                "type": "integer",
                                "description": "Number of results to return",
                                "default": 10
                            }
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="fetch_url",
                    description="Fetch content from a specific URL",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to fetch"
                            },
                            "timeout": {
                                "type": "integer", 
                                "description": "Request timeout in seconds",
                                "default": 30
                            }
                        },
                        "required": ["url"]
                    }
                ),
                Tool(
                    name="get_page_content",
                    description="Extract text content from a webpage",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "url": {
                                "type": "string",
                                "description": "URL to extract content from"
                            },
                            "extract_links": {
                                "type": "boolean",
                                "description": "Whether to extract links from the page",
                                "default": False
                            }
                        },
                        "required": ["url"]
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "web_search":
                    return await self._web_search(arguments)
                elif name == "fetch_url":
                    return await self._fetch_url(arguments)
                elif name == "get_page_content":
                    return await self._get_page_content(arguments)
                else:
                    return [TextContent(type="text", text=f"Unknown tool: {name}")]
            except Exception as e:
                logger.error(f"Error calling tool {name}: {e}")
                return [TextContent(type="text", text=f"Error: {str(e)}")]
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def _web_search(self, args: Dict[str, Any]) -> List[TextContent]:
        """Perform web search using DuckDuckGo API"""
        try:
            query = args.get("query")
            num_results = args.get("num_results", 10)
            
            session = await self._get_session()
            
            search_url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with session.get(search_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    results = {
                        "query": query,
                        "abstract": data.get("Abstract", ""),
                        "abstract_source": data.get("AbstractSource", ""),
                        "abstract_url": data.get("AbstractURL", ""),
                        "answer": data.get("Answer", ""),
                        "definition": data.get("Definition", ""),
                        "related_topics": []
                    }
                    
                    for topic in data.get("RelatedTopics", [])[:num_results]:
                        if isinstance(topic, dict) and "Text" in topic:
                            results["related_topics"].append({
                                "text": topic.get("Text", ""),
                                "url": topic.get("FirstURL", "")
                            })
                    
                    return [TextContent(type="text", text=json.dumps(results, indent=2))]
                else:
                    return [TextContent(type="text", text=f"Search failed with status: {response.status}")]
                    
        except Exception as e:
            return [TextContent(type="text", text=f"Search failed: {str(e)}")]
    
    async def _fetch_url(self, args: Dict[str, Any]) -> List[TextContent]:
        """Fetch content from URL"""
        try:
            url = args.get("url")
            timeout = args.get("timeout", 30)
            
            session = await self._get_session()
            
            async with session.get(url, timeout=timeout) as response:
                content = await response.text()
                
                result = {
                    "url": url,
                    "status": response.status,
                    "headers": dict(response.headers),
                    "content": content[:5000],  # Limit content size
                    "content_length": len(content)
                }
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
        except Exception as e:
            return [TextContent(type="text", text=f"URL fetch failed: {str(e)}")]
    
    async def _get_page_content(self, args: Dict[str, Any]) -> List[TextContent]:
        """Extract text content from webpage"""
        try:
            url = args.get("url")
            extract_links = args.get("extract_links", False)
            
            session = await self._get_session()
            
            async with session.get(url) as response:
                html_content = await response.text()
                
                import re
                
                html_content = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
                html_content = re.sub(r'<style.*?</style>', '', html_content, flags=re.DOTALL)
                
                text_content = re.sub(r'<[^>]+>', '', html_content)
                text_content = re.sub(r'\s+', ' ', text_content).strip()
                
                result = {
                    "url": url,
                    "title": self._extract_title(html_content),
                    "text_content": text_content[:3000],  # Limit content
                    "content_length": len(text_content)
                }
                
                if extract_links:
                    links = re.findall(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>([^<]*)</a>', html_content)
                    result["links"] = [{"url": link[0], "text": link[1]} for link in links[:20]]
                
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
                
        except Exception as e:
            return [TextContent(type="text", text=f"Content extraction failed: {str(e)}")]
    
    def _extract_title(self, html_content: str) -> str:
        """Extract title from HTML"""
        import re
        title_match = re.search(r'<title[^>]*>([^<]+)</title>', html_content, re.IGNORECASE)
        return title_match.group(1).strip() if title_match else "No title found"
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()

async def main():
    """Main entry point for Internet Search MCP Server"""
    server_instance = InternetSearchMCPServer()
    await server_instance.setup_handlers()
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server_instance.server.run(
                read_stream,
                write_stream,
                server_instance.server.create_initialization_options()
            )
    finally:
        await server_instance.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
