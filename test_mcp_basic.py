import asyncio
import json
from mcp.server.stdio import stdio_server
from mcp.types import InitializeRequest, ClientCapabilities

async def test_server():
    print("Testing MCP server...")
    
    async with stdio_server() as (read_stream, write_stream):
        # Send initialize request
        await write_stream.send(
            InitializeRequest(
                capabilities=ClientCapabilities()
            ).dict()
        )
        init_response = await read_stream.receive()
        print("\nInitialization response:", json.dumps(init_response, indent=2))
        
        # List resources
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 1,
            "method": "listResources",
            "params": {}
        })
        resources_response = await read_stream.receive()
        print("\nResources:", json.dumps(resources_response, indent=2))
        
        # List tools
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 2,
            "method": "listTools",
            "params": {}
        })
        tools_response = await read_stream.receive()
        print("\nTools:", json.dumps(tools_response, indent=2))
        
        # Test add-note tool
        await write_stream.send({
            "jsonrpc": "2.0",
            "id": 3,
            "method": "callTool",
            "params": {
                "name": "add-note",
                "arguments": {
                    "name": "test-note",
                    "content": "This is a test note"
                }
            }
        })
        add_note_response = await read_stream.receive()
        print("\nAdd note response:", json.dumps(add_note_response, indent=2))

if __name__ == "__main__":
    asyncio.run(test_server())
