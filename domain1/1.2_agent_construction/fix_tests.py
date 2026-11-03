import asyncio
from claude_agent_sdk import ClaudeAgentOptions, ResultMessage
from claude_agent_sdk import query

options = ClaudeAgentOptions(
    allowed_tools=["Read", "Grep", "Glob", "Edit"],
    permission_mode="acceptEdits",  # edits run without asking
    max_turns=30,
    max_budget_usd=2.0,
)
async def main():
    task = "Find why tests/test_refunds.py fails and fix it"
    async for message in query(prompt=task, options=options):
        if isinstance(message, ResultMessage):
            print(message.subtype, message.total_cost_usd)

asyncio.run(main())
