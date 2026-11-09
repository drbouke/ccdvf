"""Run the protect_files hook on three tool calls, as Claude Code would."""
from protect_files import check

calls = [  # the JSON Claude Code sends on stdin, trimmed to the used fields
    {"hook_event_name": "PreToolUse", "tool_name": "Edit",
     "tool_input": {"file_path": "/repo/support-agent/.env"}},
    {"hook_event_name": "PreToolUse", "tool_name": "Write",
     "tool_input": {"file_path": "/repo/support-agent/data/store.db"}},
    {"hook_event_name": "PreToolUse", "tool_name": "Edit",
     "tool_input": {"file_path": "/repo/support-agent/store_tools.py"}},
]

for call in calls:
    code, reason = check(call)
    path = call["tool_input"]["file_path"]
    print(f"{call['tool_name']} {path}")
    print(f"  exit {code}, " + (reason if code == 2 else "allowed"))
