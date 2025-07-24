import asyncio
import logging
import os
from typing import AsyncGenerator

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from anyio import create_memory_object_stream
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import uvicorn

from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio

class AsyncIterableStream:
    def __init__(self, stream: MemoryObjectReceiveStream):
        self._stream = stream

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return await self._stream.receive()
        except anyio.EndOfStream:
            raise StopAsyncIteration
        except Exception as e:
            logging.error(f"Error in stream: {e}")
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None

# Store notes as a simple key-value dict to demonstrate state management
notes: dict[str, str] = {}

server = Server("simple-mcp-server")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """
    List available note resources.
    Each note is exposed as a resource with a custom note:// URI scheme.
    """
    return [
        types.Resource(
            uri=AnyUrl(f"note://internal/{name}"),
            name=f"Note: {name}",
            description=f"A simple note named {name}",
            mimeType="text/plain",
        )
        for name in notes
    ]

@server.read_resource()
async def handle_read_resource(uri: AnyUrl) -> str:
    """
    Read a specific note's content by its URI.
    The note name is extracted from the URI host component.
    """
    if uri.scheme != "note":
        raise ValueError(f"Unsupported URI scheme: {uri.scheme}")

    name = uri.path
    if name is not None:
        name = name.lstrip("/")
        return notes[name]
    raise ValueError(f"Note not found: {name}")

@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """
    List available prompts.
    Each prompt can have optional arguments to customize its behavior.
    """
    return [
        types.Prompt(
            name="summarize-notes",
            description="Creates a summary of all notes",
            arguments=[
                types.PromptArgument(
                    name="style",
                    description="Style of the summary (brief/detailed)",
                    required=False,
                )
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """
    Generate a prompt by combining arguments with server state.
    The prompt includes all current notes and can be customized via arguments.
    """
    if name != "summarize-notes":
        raise ValueError(f"Unknown prompt: {name}")

    style = (arguments or {}).get("style", "brief")
    detail_prompt = " Give extensive details." if style == "detailed" else ""

    return types.GetPromptResult(
        description="Summarize the current notes",
        messages=[
            types.PromptMessage(
                role="user",
                content=types.TextContent(
                    type="text",
                    text=f"Here are the current notes to summarize:{detail_prompt}\n\n"
                    + "\n".join(
                        f"- {name}: {content}"
                        for name, content in notes.items()
                    ),
                ),
            )
        ],
    )

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """
    List available tools.
    Each tool specifies its arguments using JSON Schema validation.
    """
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
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """
    Handle tool execution requests.
    Tools can modify server state and notify clients of changes.
    """
    if name != "add-note":
        raise ValueError(f"Unknown tool: {name}")

    if not arguments:
        raise ValueError("Missing arguments")

    note_name = arguments.get("name")
    content = arguments.get("content")

    if not note_name or not content:
        raise ValueError("Missing name or content")

    # Update server state
    notes[note_name] = content

    # Notify clients that resources have changed
    await server.request_context.session.send_resource_list_changed()

    return [
        types.TextContent(
            type="text",
            text=f"Added note '{note_name}' with content: {content}",
        )
    ]

async def run_http_server():
    """Run the HTTP server with CORS support."""
    # Set up logging
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger("mcp-server")
    
    # Create FastAPI app and streams
    app = FastAPI(
        title="MCP Server",
        description="A simple MCP server implementation",
        version="0.1.0",
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    request_in, request_out = create_memory_object_stream()
    response_in, response_out = create_memory_object_stream()

    @app.post("/mcp")
    async def mcp_endpoint(request: Request):
        logger.debug("Received POST request to /mcp")
        data = await request.json()
        logger.debug(f"Request data: {data}")
        await request_out.send(data)
        logger.debug("Sent data to MCP server")
        return {"status": "ok"}

    @app.get("/mcp/stream")
    async def stream_endpoint():
        logger.debug("New SSE connection established")
        async def event_generator():
            try:
                while True:
                    logger.debug("Waiting for message from MCP server...")
                    message = await response_in.receive()
                    logger.debug(f"Received message from MCP server: {message}")
                    yield {"data": message}
            except asyncio.CancelledError:
                logger.debug("SSE connection cancelled")
                pass
            except Exception as e:
                logger.error(f"Error in event generator: {e}")
                raise
        return EventSourceResponse(event_generator())

    # Start and run both servers
    config = uvicorn.Config(app=app, host="0.0.0.0", port=8000, log_level="debug")
    server_instance = uvicorn.Server(config)
    logger.debug("Starting uvicorn server...")

    try:
        # Run both servers concurrently
        await asyncio.gather(
            server_instance.serve(),
            server.run(
                AsyncIterableStream(request_in),
                response_out,
                InitializationOptions(
                    server_name="simple-mcp-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
        )
    except Exception as e:
        logger.error(f"Error running servers: {e}")
        raise

async def main():
    mode = os.environ.get("MCP_SERVER_MODE", "stdio")
    if mode == "http":
        print("[simple-mcp-server] Starting MCP HTTP streaming server on http://0.0.0.0:8000/mcp")
        await run_http_server()
    else:
        print("[simple-mcp-server] Starting MCP server in stdio mode...")
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="simple-mcp-server",
                    server_version="0.1.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )

if __name__ == "__main__":
    asyncio.run(main())
