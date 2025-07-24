if __name__ == "__main__":
    print("[simple-mcp-server] MCP server is starting...")
    import asyncio
    from .server import main
    asyncio.run(main())
