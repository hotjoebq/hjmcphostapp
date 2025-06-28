#!/usr/bin/env python3
"""
MCP Host Application - Main Entry Point
Demonstrates the three MCP clients connecting to their respective servers
"""

import asyncio
import json
import logging
import sys
import os
from typing import Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from clients.remote_client import RemoteMCPClient
from clients.sql_client import SQLMCPClient
from clients.internet_client import InternetMCPClient

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPHostApplication:
    def __init__(self):
        self.remote_client = None
        self.sql_client = None
        self.internet_client = None
        
    async def initialize_clients(self):
        """Initialize all MCP clients"""
        logger.info("Initializing MCP clients...")
        
        self.remote_client = RemoteMCPClient("ws://localhost:8080/mcp", "websocket")
        
        self.sql_client = SQLMCPClient("servers/sql_server_mcp.py")
        
        self.internet_client = InternetMCPClient("servers/internet_mcp.py")
        
        logger.info("All MCP clients initialized")
    
    async def test_remote_client(self) -> Dict[str, Any]:
        """Test Remote MCP Client functionality"""
        logger.info("=== Testing Remote MCP Client ===")
        results = {"client": "remote", "tests": []}
        
        try:
            if await self.remote_client.connect():
                results["tests"].append({"test": "connection", "status": "success"})
                logger.info("✓ Remote client connected successfully")
                
                resources = await self.remote_client.list_resources()
                results["tests"].append({
                    "test": "list_resources", 
                    "status": "success", 
                    "count": len(resources)
                })
                logger.info(f"✓ Found {len(resources)} resources")
                
                tools = await self.remote_client.list_tools()
                results["tests"].append({
                    "test": "list_tools", 
                    "status": "success", 
                    "count": len(tools)
                })
                logger.info(f"✓ Found {len(tools)} tools")
                
                tool_result = await self.remote_client.call_tool("remote_compute", {
                    "operation": "test",
                    "data": {"message": "Hello from MCP Host App"}
                })
                results["tests"].append({
                    "test": "call_tool", 
                    "status": "success" if "error" not in tool_result else "error",
                    "result": tool_result
                })
                logger.info("✓ Tool call completed")
                
                resource_data = await self.remote_client.read_resource("remote://data")
                results["tests"].append({
                    "test": "read_resource", 
                    "status": "success" if "error" not in resource_data else "error",
                    "result": resource_data
                })
                logger.info("✓ Resource read completed")
                
            else:
                results["tests"].append({"test": "connection", "status": "failed"})
                logger.error("✗ Remote client connection failed")
                
        except Exception as e:
            logger.error(f"Remote client test failed: {e}")
            results["tests"].append({"test": "exception", "status": "error", "error": str(e)})
        
        return results
    
    async def test_sql_client(self) -> Dict[str, Any]:
        """Test SQL MCP Client functionality"""
        logger.info("=== Testing SQL MCP Client ===")
        results = {"client": "sql", "tests": []}
        
        try:
            if await self.sql_client.connect():
                results["tests"].append({"test": "connection", "status": "success"})
                logger.info("✓ SQL client connected successfully")
                
                tools = await self.sql_client.get_available_tools()
                results["tests"].append({
                    "test": "list_tools", 
                    "status": "success", 
                    "count": len(tools)
                })
                logger.info(f"✓ Found {len(tools)} tools")
                
                resources = await self.sql_client.get_available_resources()
                results["tests"].append({
                    "test": "list_resources", 
                    "status": "success", 
                    "count": len(resources)
                })
                logger.info(f"✓ Found {len(resources)} resources")
                
                db_result = await self.sql_client.connect_to_database(
                    server="localhost",
                    database="test_db"
                )
                results["tests"].append({
                    "test": "connect_database", 
                    "status": "success" if db_result.get("success") else "error",
                    "result": db_result
                })
                
                if db_result.get("success"):
                    logger.info("✓ Database connection test completed")
                    
                    query_result = await self.sql_client.execute_query("SELECT 1 as test_column")
                    results["tests"].append({
                        "test": "execute_query", 
                        "status": "success" if query_result.get("success") else "error",
                        "result": query_result
                    })
                    logger.info("✓ Query execution test completed")
                
            else:
                results["tests"].append({"test": "connection", "status": "failed"})
                logger.error("✗ SQL client connection failed")
                
        except Exception as e:
            logger.error(f"SQL client test failed: {e}")
            results["tests"].append({"test": "exception", "status": "error", "error": str(e)})
        
        return results
    
    async def test_internet_client(self) -> Dict[str, Any]:
        """Test Internet MCP Client functionality"""
        logger.info("=== Testing Internet MCP Client ===")
        results = {"client": "internet", "tests": []}
        
        try:
            if await self.internet_client.connect():
                results["tests"].append({"test": "connection", "status": "success"})
                logger.info("✓ Internet client connected successfully")
                
                tools = await self.internet_client.get_available_tools()
                results["tests"].append({
                    "test": "list_tools", 
                    "status": "success", 
                    "count": len(tools)
                })
                logger.info(f"✓ Found {len(tools)} tools")
                
                resources = await self.internet_client.get_available_resources()
                results["tests"].append({
                    "test": "list_resources", 
                    "status": "success", 
                    "count": len(resources)
                })
                logger.info(f"✓ Found {len(resources)} resources")
                
                search_result = await self.internet_client.web_search("Python MCP protocol", 3)
                results["tests"].append({
                    "test": "web_search", 
                    "status": "success" if search_result.get("success") else "error",
                    "result": search_result
                })
                logger.info("✓ Web search test completed")
                
                url_result = await self.internet_client.fetch_url("https://httpbin.org/json")
                results["tests"].append({
                    "test": "fetch_url", 
                    "status": "success" if url_result.get("success") else "error",
                    "result": url_result
                })
                logger.info("✓ URL fetch test completed")
                
            else:
                results["tests"].append({"test": "connection", "status": "failed"})
                logger.error("✗ Internet client connection failed")
                
        except Exception as e:
            logger.error(f"Internet client test failed: {e}")
            results["tests"].append({"test": "exception", "status": "error", "error": str(e)})
        
        return results
    
    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive test of all MCP clients"""
        logger.info("Starting comprehensive MCP application test...")
        
        await self.initialize_clients()
        
        test_results = {
            "application": "MCP Host Application",
            "timestamp": "2024-01-01T00:00:00Z",
            "clients": []
        }
        
        remote_results = await self.test_remote_client()
        test_results["clients"].append(remote_results)
        
        sql_results = await self.test_sql_client()
        test_results["clients"].append(sql_results)
        
        internet_results = await self.test_internet_client()
        test_results["clients"].append(internet_results)
        
        await self.cleanup()
        
        return test_results
    
    async def cleanup(self):
        """Cleanup all client connections"""
        logger.info("Cleaning up client connections...")
        
        try:
            if self.remote_client:
                await self.remote_client.disconnect()
            
            if self.sql_client:
                await self.sql_client.disconnect()
            
            if self.internet_client:
                await self.internet_client.disconnect()
                
            logger.info("✓ All clients disconnected successfully")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

async def main():
    """Main entry point"""
    print("=" * 60)
    print("MCP Host Application - Comprehensive Test")
    print("=" * 60)
    
    app = MCPHostApplication()
    
    try:
        results = await app.run_comprehensive_test()
        
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        
        for client_result in results["clients"]:
            client_name = client_result["client"].upper()
            print(f"\n{client_name} MCP CLIENT:")
            
            for test in client_result["tests"]:
                status_symbol = "✓" if test["status"] == "success" else "✗"
                test_name = test["test"].replace("_", " ").title()
                print(f"  {status_symbol} {test_name}")
                
                if "count" in test:
                    print(f"    Count: {test['count']}")
                
                if test["status"] == "error" and "error" in test:
                    print(f"    Error: {test['error']}")
        
        all_connections_successful = all(
            any(test["test"] == "connection" and test["status"] == "success" 
                for test in client["tests"])
            for client in results["clients"]
        )
        
        print(f"\n{'=' * 60}")
        if all_connections_successful:
            print("🎉 ALL MCP CLIENTS CONNECTED SUCCESSFULLY!")
            print("✓ Remote MCP Client - Connected to simulated remote server")
            print("✓ SQL MCP Client - Connected to SQL Server MCP via stdio")
            print("✓ Internet MCP Client - Connected to Internet Search MCP via stdio")
        else:
            print("⚠️  SOME MCP CLIENT CONNECTIONS FAILED")
            print("Check the detailed results above for more information")
        
        print("=" * 60)
        
        with open("test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("📄 Detailed results saved to test_results.json")
        
    except Exception as e:
        logger.error(f"Application test failed: {e}")
        print(f"\n❌ Application test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
