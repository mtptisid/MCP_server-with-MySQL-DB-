from fastapi import FastAPI, Request
from mcp.server import Server
import mcp.types as types
from pydantic import AnyUrl
import logging
import json
import os
import mysql.connector

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI()

# Create MCP server
server = Server("simple-mcp-server")

# Store notes
notes = {}

RESOURCE_FILES_DIR = os.path.join(os.path.dirname(__file__), '../../resources/files')

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  # Update if you set a root password
    'database': 'bank',
}

@server.list_resources()
async def handle_list_resources():
    """List available note, file, and MySQL resources."""
    resources = []
    # Notes as resources
    if not notes:
        notes["example"] = "This is an example note."
    resources.extend([
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ])
    # File resources
    if os.path.exists(RESOURCE_FILES_DIR):
        for fname in os.listdir(RESOURCE_FILES_DIR):
            fpath = os.path.join(RESOURCE_FILES_DIR, fname)
            if os.path.isfile(fpath):
                resources.append(
                    types.Resource(
                        uri=AnyUrl(f"file://local/{fname}"),
                        name=f"File: {fname}",
                        description=f"A file resource named {fname}",
                        mimeType="text/plain",
                    )
                )
    # MySQL tables as resources
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        for table in tables:
            cursor.execute(f"DESCRIBE {table};")
            columns = cursor.fetchall()
            schema = ', '.join([f"{col[0]} {col[1]}" for col in columns])
            # Fetch up to 3 rows of data for preview
            cursor.execute(f"SELECT * FROM {table} LIMIT 3;")
            rows = cursor.fetchall()
            data_preview = '\n'.join([str(row) for row in rows]) if rows else 'No data.'
            resources.append(
                types.Resource(
                    uri=AnyUrl(f"mysql://localhost/bank/{table}"),
                    name=f"MySQL Table: {table}",
                    description=f"Table {table} schema: {schema}\nSample data:\n{data_preview}",
                    mimeType="application/sql",
                )
            )
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"MySQL error: {e}")
        resources.append(
            types.Resource(
                uri=AnyUrl("mysql://localhost/bank"),
                name="Bank MySQL Database",
                description="MySQL database for bank customer and transaction details (connection error)",
                mimeType="application/sql",
            )
        )
    return resources

@server.list_tools()
async def handle_list_tools():
    """List available tools."""
    # Always include at least one tool for demonstration
    return [
        types.Tool(
            name="add-note",
            description="Add a new note",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "content": {"type": "string"},
                },
                "required": ["name", "content"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    """Handle tool calls."""
    if name != "add-note":
        raise ValueError(f"Unknown tool: {name}")
        
    if not arguments:
        raise ValueError("Missing arguments")
        
    note_name = arguments.get("name")
    content = arguments.get("content")
    
    if not note_name or not content:
        raise ValueError("Missing name or content")
        
    notes[note_name] = content
    
    return [types.TextContent(
        type="text",
        text=f"Added note '{note_name}' with content: {content}"
    )]

@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """Handle incoming MCP requests."""
    data = await request.json()
    logger.debug(f"Received request: {data}")
    method = data.get("method")
    try:
        if method == "listResources":
            result = await handle_list_resources()
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": [r.dict() for r in result]
            }
        elif method == "listTools":
            result = await handle_list_tools()
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": [t.dict() for t in result]
            }
        elif method == "callTool":
            params = data.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = await handle_call_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": [r.dict() for r in result]
            }
        elif method == "initialize":
            return {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "result": {
                    "serverInfo": {
                        "name": "simple-mcp-server",
                        "version": "0.1.0"
                    },
                    "capabilities": {
                        "resources": True,
                        "prompts": False,
                        "tools": True,
                        "notifications": {
                            "resourceListChanged": True
                        }
                    }
                }
            }
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Method {method} not found"},
                "id": data.get("id")
            }
    except Exception as e:
        logger.error(f"Error handling request: {e}")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32000, "message": str(e)},
            "id": data.get("id")
        }

if __name__ == "__main__":
    import uvicorn
    print("[simple-mcp-server] Starting MCP HTTP server on http://0.0.0.0:8000/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")