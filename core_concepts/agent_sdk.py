"""Acme support assistant: an agent that researches a ticket on its own."""
import asyncio

from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions,
                              ResultMessage, ToolUseBlock, query)

OPTIONS = ClaudeAgentOptions(
    model="claude-haiku-5-5",
    tools=["Read", "Grep"],          # the only tools that exist
    allowed_tools=["Read", "Grep"],  # run without asking
    cwd="../data",                   # tickets, policy and store
    max_turns=8,  # the task needs about four; this stops a runaway loop
)
TASK = ("Ticket T-1003 in tickets.jsonl: what does the policy in this "
        "folder allow, and which sections apply? Reply in at most 60 "
        "words.")


async def main() -> None:
    async for message in query(prompt=TASK, options=OPTIONS):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print("tool:", block.name)
        elif isinstance(message, ResultMessage):
            print(message.result, f"\n{message.num_turns} turns")


asyncio.run(main())
