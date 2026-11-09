"""PreToolUse hook: no decision is saved that the grant guide forbids, whatever the model was told.

Claude Code runs it before every call to the grants server's save_decision tool (see .claude/settings.json) and
sends the call as JSON on stdin. Exit code 2 blocks the call, and the text on stderr goes back to Claude.
"""
import json
import sys

from grants import REFER_AT, calculate_grant, claim


def check(event: dict) -> tuple[int, str]:
    """Return the exit code and the reason for one save_decision call."""
    d = event["tool_input"]
    if d.get("outcome") in ("Reject", "Refer"):
        return 0, ""   # rejecting or referring never pays out
    if not claim(d.get("claim_id", "")):
        return 2, f"Blocked: no claim {d.get('claim_id')!r}."
    computed = calculate_grant(d["claim_id"])
    # TODO 1: block (exit code 2) an Approve or Partial whose grant is REFER_AT or more, with a reason
    # that tells Claude to refer the claim to an officer under Section 9 of the guide.
    # TODO 2: block a grant above the grant computed in code, and an Approve when the computed grant
    # carries reason codes, naming the computed grant and its codes in the reason.
    return 0, ""


if __name__ == "__main__":
    code, reason = check(json.load(sys.stdin))
    if reason:
        print(reason, file=sys.stderr)
    sys.exit(code)
