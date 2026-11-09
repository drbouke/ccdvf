"""Acme support assistant: start the orders server and use what it offers."""
import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

SERVER = StdioServerParameters(command=sys.executable,
                               args=["orders_server.py"])


async def main():
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            info = await session.initialize()
            print(f"connected to {info.server_info.name}")
            for tool in (await session.list_tools()).tools:
                print(f"tool {tool.name}: {tool.input_schema['required']}")
            for res in (await session.list_resources()).resources:
                print(f"resource {res.uri} ({res.mime_type})")

            result = await session.call_tool(
                "order_record", {"order_id": "ord_21044"})
            order = json.loads(result.content[0].text)
            print(f"ord_21044: {order['status']}, "
                  f"{order['tracking'][-1]['event']}")
            policy = await session.read_resource("acme://refund-policy")
            print(f"policy: {len(policy.contents[0].text):,} characters")


asyncio.run(main())
