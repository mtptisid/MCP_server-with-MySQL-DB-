import asyncio
import json
from mcp.client.http import http_client

async def test_server():
    print("Testing MCP HTTP server...")
    
    async with http_client("http://localhost:8000/mcp") as client:
        print("\n=== Listing Resources ===")
        resources = await client.list_resources()
        print("Resources:", json.dumps(resources, indent=2))
        
        print("\n=== Listing Tools ===")
        tools = await client.list_tools()
        print("Available Tools:", json.dumps(tools, indent=2))
        
        print("\n=== Listing Prompts ===")
        prompts = await client.list_prompts()
        print("Available Prompts:", json.dumps(prompts, indent=2))
        
        print("\n=== Testing add-note Tool ===")
        result = await client.call_tool("add-note", {
            "name": "test-note",
            "content": "This is a test note created by the test script"
        })
        print("Add Note Result:", json.dumps(result, indent=2))
        
        print("\n=== Verifying Added Note ===")
        updated_resources = await client.list_resources()
        print("Updated Resources:", json.dumps(updated_resources, indent=2))

if __name__ == "__main__":
    asyncio.run(test_server())
