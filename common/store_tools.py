"""Acme support tools backed by the store database and the refund policy.

TOOLS holds the tool definitions sent to Claude. run_tool() runs the tool
Claude asks for and returns the result as text, so Claude never reads the
database itself.
"""
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DB = DATA / "store.db"
POLICY = (DATA / "refund_policy.md").read_text(encoding="utf-8")

TOOLS = [
    {
        "name": "find_customer",
        "description": ("Find a customer by email address or customer id "
                        "(C-1234). Returns the profile and their recent "
                        "orders."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "Email or customer id"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_order",
        "description": ("Full record of one order: items, payments (every "
                        "capture), shipment, courier tracking events and "
                        "refunds."),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string",
                             "description": "For example ord_20931"},
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "search_policy",
        "description": ("Search the Acme returns, refunds and delivery "
                        "policy. Returns the matching sections with their "
                        "numbers."),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string",
                          "description": "Keywords, e.g. duplicate charge"},
            },
            "required": ["query"],
        },
    },
]


def _query(sql: str, params: tuple = ()) -> list[dict]:
    """Run a read-only query and return the rows as dictionaries."""
    with closing(sqlite3.connect(DB)) as con:
        con.row_factory = sqlite3.Row
        return [dict(row) for row in con.execute(sql, params)]


def find_customer(query: str) -> str:
    """The customer profile with their five most recent orders."""
    key = query.strip()
    found = _query("SELECT * FROM customers "
                   "WHERE customer_id = ? OR lower(email) = lower(?)",
                   (key, key))
    if not found:
        return f"No customer matches {key!r}."
    customer = found[0]
    # the five latest orders give context and keep the result short
    customer["recent_orders"] = _query(
        "SELECT order_id, placed_at, status, total FROM orders "
        "WHERE customer_id = ? ORDER BY placed_at DESC LIMIT 5",
        (customer["customer_id"],))
    return json.dumps(customer)


def get_order(order_id: str) -> str:
    """One order with its items, payments, shipment, tracking and refunds."""
    found = _query("SELECT * FROM orders WHERE order_id = ?",
                   (order_id.strip(),))
    if not found:
        return f"Order {order_id} not found."
    order = found[0]
    key = (order["order_id"],)
    order["items"] = _query(
        "SELECT i.product_id, p.name, i.qty, i.unit_price "
        "FROM order_items i JOIN products p USING (product_id) "
        "WHERE i.order_id = ?", key)
    order["payments"] = _query(
        "SELECT payment_id, method, amount, status, paid_at FROM payments "
        "WHERE order_id = ? ORDER BY paid_at", key)
    shipments = _query(
        "SELECT courier, tracking_no, shipped_at, promised_by "
        "FROM shipments WHERE order_id = ?", key)
    order["shipment"] = shipments[0] if shipments else None
    order["tracking"] = _query(
        "SELECT at, location, event FROM tracking_events "
        "WHERE order_id = ? ORDER BY at", key)
    order["refunds"] = _query(
        "SELECT refund_id, amount, reason, status, created_at FROM refunds "
        "WHERE order_id = ?", key)
    return json.dumps(order)


def search_policy(query: str) -> str:
    """The two policy sections that match the most query words."""
    # words of three letters or more: "is" and "of" match every section
    words = [w for w in re.findall(r"[a-z0-9]+", query.lower()) if len(w) > 2]
    sections = re.split(r"\n(?=## )", POLICY)[1:]
    scored = sorted(((sum(s.lower().count(w) for w in words), s)
                     for s in sections), reverse=True)
    hits = [s.strip() for score, s in scored[:2] if score > 0]  # best two
    if not hits:
        return f"No policy section matches {query!r}."
    return "\n\n".join(hits)


HANDLERS = {
    "find_customer": find_customer,
    "get_order": get_order,
    "search_policy": search_policy,
}


def run_tool(name: str, tool_input: dict) -> str:
    """Run the tool Claude asked for and return its result as text."""
    handler = HANDLERS.get(name)
    if handler is None:
        return f"unknown tool: {name}"
    return handler(**tool_input)
