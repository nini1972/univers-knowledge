import asyncio
import os
import json
import re
from crewai.tools import BaseTool
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def _resolve_nanobanana_binary(root_dir: str) -> str:
    """Resolve MCP binary path for the current OS; return empty string when unavailable."""
    servers_dir = os.path.join(root_dir, ".mcp-servers")
    windows_bin = os.path.join(servers_dir, "mcp-nanobanana-go.exe")
    posix_bin = os.path.join(servers_dir, "mcp-nanobanana-go")

    if os.name == "nt" and os.path.exists(windows_bin):
        return windows_bin
    if os.path.exists(posix_bin):
        return posix_bin
    return ""

async def _generate_image_async(prompt: str) -> str:
    """Async core to call the nanobanana MCP server."""
    # Load config to get environment
    # Resolve project root relative to src/tools/
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Allow opt-out in CI or environments without Genmedia provisioning.
    if os.getenv("ENABLE_GENMEDIA", "true").lower() == "false":
        return "GENMEDIA_UNAVAILABLE: disabled by ENABLE_GENMEDIA=false"

    try:
        config_path = os.path.join(root_dir, "mcp-config.json")
        with open(config_path) as f:
            config = json.load(f)
        env_vars = config['mcpServers']['genmedia-nanobanana']['env']
    except Exception:
        env_vars = {}

    bin_path = _resolve_nanobanana_binary(root_dir)
    if not bin_path:
        return "GENMEDIA_UNAVAILABLE: nanobanana MCP binary not found for this OS"

    server_params = StdioServerParameters(
        command=bin_path,
        args=[],
        env={**os.environ.copy(), **env_vars}
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Make sure the output directory exists
                out_dir = os.path.join(root_dir, "knowledge_base", "images")
                os.makedirs(out_dir, exist_ok=True)

                # Need to use the fallback model gemini-2.5-flash-image if 3.x is unavailable
                result = await session.call_tool(
                    "nanobanana_image_generation",
                    arguments={
                        "prompt": prompt, 
                        "aspect_ratio": "16:9",
                        "model": "gemini-2.5-flash-image",
                        "output_directory": out_dir
                    }
                )
                
                # Return the text content and parse the generated image path
                text_output = "\\n".join([c.text for c in result.content if c.type == 'text'])
                
                # The tool output has format: "...Generated and saved 1 image(s): <path>"
                # Search for the path. We will try to isolate just the generated image path.
                match = re.search(r'saved \d+ image\(s\):\s*(.+)', text_output)
                if match:
                    # Return path relative to the workspace root if possible, or just the filename for markdown
                    filepath = match.group(1).strip()
                    # Convert to forward slashes for markdown
                    filepath = filepath.replace("\\\\", "/")
                    
                    # Ensure path works relative to the knowledge_base folder since the final markdown is inside knowledge_base
                    # E.g., if path is c:/.../knowledge_base/images/file.png, we just want 'images/file.png'
                    if "knowledge_base" in filepath:
                        filepath = filepath.split("knowledge_base/")[-1]
                        
                    return filepath
                return text_output
    except Exception as e:
        return f"GENMEDIA_UNAVAILABLE: {str(e)}"

class GenerateUniverseImageTool(BaseTool):
    name: str = "Generate Universe Image"
    description: str = (
        "Generate an image using the Google Genmedia (Nano Banana) MCP Server. "
        "Pass a highly detailed, 1-paragraph prompt that visualizes a physics or cosmology concept. "
        "Returns the generated local image path or a GENMEDIA_UNAVAILABLE message."
    )

    def _run(self, prompt: str) -> str:
        return asyncio.run(_generate_image_async(prompt))
