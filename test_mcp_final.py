import asyncio
import aiohttp
import json
from mcp.types import ClientCapabilities, ClientInfo

async def test_server():
    print("Testing MCP HTTP server...")
    
    # Create proper MCP messages
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "0.1.0",
            "clientInfo": {
                "name": "test-client",
                "version": "0.1.0"
            },
            "capabilities": {}
        }
    }
    
    resources_msg = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "listResources",
        "params": {}
    }
    
    tools_msg = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "listTools",
        "params": {}
    }
    
    async with aiohttp.ClientSession() as session:
        print("\nTesting Initialize...")
        try:
            async with session.post("http://localhost:8000/mcp", json=init_msg) as response:
                text = await response.text()
                print(f"Status: {response.status}")
                print(f"Headers: {response.headers}")
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")
            
        print("\nTesting List Resources...")
        try:
            async with session.post("http://localhost:8000/mcp", json=resources_msg) as response:
                text = await response.text()
                print(f"Status: {response.status}")
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")
            
        print("\nTesting List Tools...")
        try:
            async with session.post("http://localhost:8000/mcp", json=tools_msg) as response:
                text = await response.text()
                print(f"Status: {response.status}")
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
