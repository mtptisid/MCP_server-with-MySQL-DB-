import asyncio
import json
from mcp import ClientSession, stdio_client

async def test_server():
    print("Connecting to MCP server...")
    # Create a subprocess running the MCP server
    process = await asyncio.create_subprocess_exec(
        "python", "-m", "simple_mcp_server.server",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE
    )
    
    # Create stdio client connected to the server process
    async with stdio_client(process) as (read_stream, write_stream):
        client = ClientSession(read_stream, write_stream)
        await client.initialize()
        
        print("\n=== Testing Server Capabilities ===")
        print("Server Info:", client.server_info)
        print("Capabilities:", json.dumps(client.capabilities, indent=2))
        
        print("\n=== Listing Resources ===")
        resources = await client.list_resources()
        print("Resources:", json.dumps(resources, indent=2))
        
        print("\n=== Listing Tools ===")
        tools = await client.list_tools()
        print("Available Tools:", json.dumps(tools, indent=2))
        
        print("\n=== Listing Prompts ===")
        prompts = await client.list_prompts()
        print("Available Prompts:", json.dumps(prompts, indent=2))
        
        # Test adding a note using the add-note tool
        print("\n=== Testing add-note Tool ===")
        tool_result = await client.call_tool("add-note", {
            "name": "test-note",
            "content": "This is a test note created by the test script"
        })
        print("Tool Result:", json.dumps(tool_result, indent=2))
        
        # Verify the note was added by listing resources again
        print("\n=== Verifying Added Note ===")
        updated_resources = await client.list_resources()
        print("Updated Resources:", json.dumps(updated_resources, indent=2))

if __name__ == "__main__":
    asyncio.run(test_server())
