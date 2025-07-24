import asyncio
import aiohttp
import json

async def test_server():
    print("Testing MCP HTTP server...")
    
    async with aiohttp.ClientSession() as session:
        # Initialize
        init_data = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "capabilities": {}
            }
        }
        
        try:
            async with session.post("http://localhost:8000/mcp", json=init_data) as response:
                text = await response.text()
                print(f"\nStatus: {response.status}")
                print(f"Headers: {response.headers}")
                print(f"Response: {text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_server())
