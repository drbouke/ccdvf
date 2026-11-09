"""PreToolUse hook: block edits to files the agent must never change."""
import json
import sys

PROTECTED = (".env", "store.db", ".git/")  # secrets, live data, history


def check(event: dict) -> tuple[int, str]:
    """Return the exit code and the reason for one tool call."""
    path = event["tool_input"].get("file_path", "")
    for pattern in PROTECTED:
        if pattern in path.replace("\\", "/"):
            return 2, f"Blocked: {path} matches {pattern!r}"
    return 0, ""


if __name__ == "__main__":
    code, reason = check(json.load(sys.stdin))  # Claude Code sends JSON
    if reason:
        print(reason, file=sys.stderr)  # exit 2 sends stderr to Claude
    sys.exit(code)
