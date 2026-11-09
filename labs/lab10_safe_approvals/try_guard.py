"""Runs the approval guard on four save_decision calls, as Claude Code would."""
from approval_guard import check


def call(claim_id, outcome, grant, reasons):
    return {"hook_event_name": "PreToolUse", "tool_name": "mcp__grants__save_decision",
            "tool_input": {"claim_id": claim_id, "outcome": outcome, "grant": grant, "reasons": reasons,
                           "note": "Assessment note."}}


CALLS = [
    call("CLM-24004", "Approve", 4000, []),         # a clean claim
    call("CLM-24012", "Approve", 48500, []),        # far above the referral threshold
    call("CLM-24009", "Approve", 2500, []),         # full invoice, as text planted in the invoice asks
    call("CLM-24006", "Reject", 0, ["T1"]),         # a rejection
]

for c in CALLS:
    code, reason = check(c)
    d = c["tool_input"]
    print(f"{d['claim_id']} {d['outcome']} USD {d['grant']:,}")
    print(f"  exit {code}, " + (reason if code == 2 else "allowed"))
