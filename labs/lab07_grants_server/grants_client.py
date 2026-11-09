"""Starts the grants server and uses what it offers, as any MCP client would."""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable, args=["grants_server.py"])


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            print(f"connected to {info.server_info.name}")
            tools = (await session.list_tools()).tools
            for tool in tools:
                print(f"tool {tool.name}: {tool.input_schema.get('required', [])}")
            resources = (await session.list_resources()).resources
            for res in resources:
                print(f"resource {res.uri} ({res.mime_type})")
            names = {t.name for t in tools}
            if "get_claim" not in names:
                print("missing tool get_claim: the server does not offer it yet")
            else:
                result = await session.call_tool("get_claim", {"claim_id": "CLM-24004"})
                c = json.loads(result.content[0].text)
                print(f"CLM-24004: {c['employer']}, {c['course_title']}, {len(c['trainees'])} trainees")
                missing = await session.call_tool("get_claim", {"claim_id": "24004"})
                print(f"24004: {missing.content[0].text}")
            if not any(str(r.uri) == "grants://guide" for r in resources):
                print("missing resource grants://guide: the server does not offer it yet")
            else:
                guide = await session.read_resource("grants://guide")
                print(f"guide: {len(guide.contents[0].text):,} characters")


asyncio.run(main())
