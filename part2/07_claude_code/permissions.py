"""Acme support assistant: Claude Code permission rules, deny over allow."""
import asyncio
import json

from claude_agent_sdk import ClaudeAgentOptions, ResultMessage, query

SETTINGS = {"permissions": {
    "allow": ["Read", "Grep"],               # reading is allowed in general
    "deny": ["Read(./tickets.jsonl)"],       # but not the customer messages
}}
OPTIONS = ClaudeAgentOptions(
    model="claude-haiku-5-5", cwd="../../data",  # policy, tickets, store
    settings=json.dumps(SETTINGS), setting_sources=[],  # only these rules
    permission_mode="dontAsk", max_turns=6,  # not allowed: refused, no prompt
)
TASKS = ["Which section of refund_policy.md covers a duplicate charge? "
         "Answer in at most 15 words.",
         "Read tickets.jsonl and count the tickets that mention a blender. "
         "Answer in one sentence."]


async def main() -> None:
    for task in TASKS:
        async for message in query(prompt=task, options=OPTIONS):
            if isinstance(message, ResultMessage):
                denied = [d.get("tool_name") for d in
                          (message.permission_denials or [])]
                print(f"- {task[:40]}...\n  denied: {denied or 'none'}\n"
                      f"  {message.result.split('. ')[0].rstrip('.')}.")


asyncio.run(main())
