import asyncio
import aiohttp
import json

async def test_server():
    print("Testing MCP HTTP server...")
    
    async with aiohttp.ClientSession() as session:
        # Test POST to /mcp endpoint
        data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "capabilities": {}
            }
        }
        async with session.post("http://localhost:8000/mcp", json=data) as response:
            print("\nInitialize Response:", await response.json())
        
        # Test list tools
        data = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "listTools",
            "params": {}
        }
        async with session.post("http://localhost:8000/mcp", json=data) as response:
            print("\nTools Response:", await response.json())
        
        # Test list resources
        data = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "listResources",
            "params": {}
        }
        async with session.post("http://localhost:8000/mcp", json=data) as response:
            print("\nResources Response:", await response.json())
        
        # Test list prompts
        data = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "listPrompts",
            "params": {}
        }
        async with session.post("http://localhost:8000/mcp", json=data) as response:
            print("\nPrompts Response:", await response.json())
        
        # Test add-note tool
        data = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "callTool",
            "params": {
                "name": "add-note",
                "arguments": {
                    "name": "test-note",
                    "content": "This is a test note"
                }
            }
        }
        async with session.post("http://localhost:8000/mcp", json=data) as response:
            print("\nAdd Note Response:", await response.json())

if __name__ == "__main__":
    asyncio.run(test_server())
