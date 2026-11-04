"""Typed output with Pydantic AI: an agent decides return requests against the order records and the policy.
Every answer must fit ReturnDecision; Pydantic validates it before your code uses it, so the table below can be
filled without parsing text."""
import json
import sqlite3
from typing import Literal
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from store_tools import DB, POLICY, get_order


class ReturnDecision(BaseModel):
    order_id: str
    decision: Literal["refund", "replace_or_refund", "refuse",
                      "needs_team_lead"]
    refund: float = Field(
        ge=0, description="Amount the policy allows, 0 if refused")
    policy_sections: list[str] = Field(
        description="For example ['2.1', '2.2']")
    reason: str = Field(
        description="One sentence for the customer service log")


agent = Agent("anthropic:claude-haiku-5-5", output_type=ReturnDecision,
              instructions="Decide Acme return requests strictly by this "
                           "policy. Today is 1 November 2026.\n\n" + POLICY)


@agent.tool_plain
def lookup_order(order_id: str) -> str:
    """Full record of one order: items, payments, delivery date, refunds."""
    return get_order(order_id)


def first(sql):
    with sqlite3.connect(DB) as con:
        return con.execute(sql).fetchone()[0]


earbuds = first("SELECT o.order_id FROM orders o JOIN order_items i USING (order_id) WHERE i.product_id = 'P-201' "
                "AND o.status = 'delivered' AND o.delivered_at >= '2026-10-15' LIMIT 1")
fryer = first("SELECT o.order_id FROM orders o JOIN order_items i USING (order_id) WHERE i.product_id = 'P-104' "
              "AND o.status = 'delivered' AND o.delivered_at >= '2026-10-10' LIMIT 1")
old = first("SELECT order_id FROM orders WHERE status = 'delivered' AND delivered_at < '2026-09-15' LIMIT 1")
REQUESTS = [
    ("ord_20931", "The blender jug arrived cracked; photos of the jug and the box attached. I want my money back."),
    ("ord_21500", "Air purifier housing cracked on arrival, photos attached. Full refund please."),
    (earbuds, "Opened the earbuds, I just do not like the sound. Please take them back."),
    (fryer, "Changed my mind about the air fryer. Box never opened."),
    (old, "I would like to return this order, I no longer need it. Everything is unused."),
]

print(f"{'order':10} {'decision':18} {'Amount':>8}  {'policy':10} reason")
for order_id, message in REQUESTS:
    d = agent.run_sync(f"Order {order_id}. Customer message: {message}").output
    print(f"{d.order_id:10} {d.decision:18} {d.refund:>8.2f}  {','.join(d.policy_sections):10} {d.reason}")
