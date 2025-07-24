import asyncio
import json
from mcp.server.stdio import stdio_client
from mcp import InitializeRequest, ClientCapabilities

async def test_server():
    print("Testing MCP server in stdio mode...")
    
    async with stdio_client() as (read_stream, write_stream):
        # Initialize
        await write_stream.send(InitializeRequest(
            capabilities=ClientCapabilities()
        ).dict())
        init_response = await read_stream.receive()
        print("\nInitialization Response:", json.dumps(init_response, indent=2))
        
        # List Resources
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "listResources",
            "params": {}
        })
        resources = await read_stream.receive()
        print("\nResources:", json.dumps(resources, indent=2))
        
        # List Tools
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "listTools",
            "params": {}
        })
        tools = await read_stream.receive()
        print("\nTools:", json.dumps(tools, indent=2))
        
        # List Prompts
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "listPrompts",
            "params": {}
        })
        prompts = await read_stream.receive()
        print("\nPrompts:", json.dumps(prompts, indent=2))
        
        # Add a note
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 4,
            "method": "callTool",
            "params": {
                "name": "add-note",
                "arguments": {
                    "name": "test-note",
                    "content": "This is a test note"
                }
            }
        })
        add_result = await read_stream.receive()
        print("\nAdd Note Result:", json.dumps(add_result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_server())
