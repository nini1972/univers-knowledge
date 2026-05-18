import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Load config to get project id if needed
    with open("mcp-config.json") as f:
        config = json.load(f)
    print(config)

    server_params = StdioServerParameters(
        command=".\\.mcp-servers\\mcp-nanobanana-go.exe",
        args=[],
        env={**os.environ.copy(), **config['mcpServers']['genmedia-nanobanana']['env']}
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # List tools
            tools = await session.list_tools()
            print("Available tools:", tools)
            
            # Call tool
            result = await session.call_tool(
                "nanobanana_image_generation",
                arguments={
                    "prompt": "A beautiful galaxy filled with colorful stars", 
                    "aspect_ratio": "16:9",
                    "model": "gemini-2.5-flash-image",
                    "output_directory": "./output_images"
                }
            )
            print("Tool result:", result)

if __name__ == "__main__":
    asyncio.run(run())
