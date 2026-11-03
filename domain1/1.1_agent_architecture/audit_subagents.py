"""Supervisor and subagents: a lead agent audits every duplicate charge in the store. It finds the orders, hands each
one to an order-auditor subagent (its own context window, only the order tool), and writes the report from their
short findings. The lead never reads the raw order records."""
import asyncio
import json
import sqlite3
from claude_agent_sdk import (AgentDefinition, AssistantMessage, ClaudeAgentOptions, ResultMessage,
                              ToolUseBlock, create_sdk_mcp_server, query, tool)
from pintar_tools import DB, get_order


@tool("find_duplicate_charges", "List the orders whose payment was captured more than once.", {})
async def duplicates_tool(args):
    with sqlite3.connect(DB) as con:
        rows = con.execute("SELECT order_id, COUNT(*), SUM(amount_myr) FROM payments WHERE status = 'captured' "
                           "GROUP BY order_id HAVING COUNT(*) > 1 ORDER BY order_id").fetchall()
    return {"content": [{"type": "text", "text": json.dumps(
        [{"order_id": o, "captures": n, "captured_myr": round(t, 2)} for o, n, t in rows])}]}


@tool("get_order", "Full record of one order: items, payments, shipment, tracking and refunds.", {"order_id": str})
async def order_tool(args):
    return {"content": [{"type": "text", "text": get_order(args["order_id"])}]}


store = create_sdk_mcp_server(name="store",
                              tools=[duplicates_tool, order_tool])
auditor = AgentDefinition(
    description="Checks one order for a duplicate charge and returns "
                "a one-line finding.",
    prompt=("Look up the order you are given. Report in one line: extra "
            "amount charged, whether a refund already covers it, the "
            "delivery status, and the action needed."),
    tools=["mcp__store__get_order"],
    model="claude-haiku-5-5")
options = ClaudeAgentOptions(
    model="claude-haiku-5-5",
    system_prompt=("You lead a payments audit at Pintar. Find the orders "
                   "charged more than once, give each order to the "
                   "order-auditor subagent, then write one table: order, "
                   "extra amount, refunded or not, delivery status, action "
                   "needed. End with the total extra amount still owed to "
                   "customers."),
    mcp_servers={"store": store},
    allowed_tools=["mcp__store__find_duplicate_charges",
                   "mcp__store__get_order", "Agent", "Task"],
    agents={"order-auditor": auditor},
    max_turns=40,
)


async def main():
    delegated = 0
    async for message in query(prompt="Audit all duplicate charges in the store.", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock) and block.name in ("Agent", "Task"):
                    delegated += 1
        elif isinstance(message, ResultMessage):
            print(message.result or message.subtype)
            print(f"\n[{delegated} subagent tasks, {message.num_turns} lead turns, USD {message.total_cost_usd:.4f}]")

asyncio.run(main())
