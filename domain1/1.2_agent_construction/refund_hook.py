import sqlite3
from pintar_tools import DB

LIMIT_MYR = 500  # policy 6.1 to 6.3, enforced in code

async def cap_refunds(input_data, tool_use_id, context):
    args = input_data["tool_input"]
    with sqlite3.connect(DB) as con:
        earlier = con.execute(
            "SELECT COUNT(*) FROM refunds WHERE order_id = ?",
            (args["order_id"],)).fetchone()[0]
    if args["amount_myr"] <= LIMIT_MYR and earlier == 0:
        return {}  # allow
    why = "a second refund" if earlier else f"above MYR {LIMIT_MYR}"
    return {"hookSpecificOutput": {
        "hookEventName": input_data["hook_event_name"],
        "permissionDecision": "deny",
        "permissionDecisionReason": f"Team lead approval needed: {why}",
    }}
