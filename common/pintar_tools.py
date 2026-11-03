"""Pintar support tools over data/pintar.db and data/refund_policy.md.

TOOLS holds the definitions Claude sees (name, description, input schema); run_tool() runs the one Claude asks for and
returns text. Claude never touches the database: it can only ask, and this code decides what to return.
"""
import json
import re
import sqlite3
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
DB = DATA / 'pintar.db'
POLICY = (DATA / 'refund_policy.md').read_text(encoding='utf-8')

TOOLS = [
    {"name": "find_customer",
     "description": "Find a customer by email address or customer id "
                    "(C-1234). Returns the profile and their recent orders.",
     "input_schema": {"type": "object", "required": ["query"], "properties": {
         "query": {"type": "string",
                   "description": "Email or customer id"}}}},
    {"name": "get_order",
     "description": "Full record of one order: items, payments (every "
                    "capture), shipment, courier tracking events and refunds.",
     "input_schema": {"type": "object", "required": ["order_id"],
                      "properties": {"order_id": {"type": "string",
                                     "description": "For example ord_20931"}}}},
    {"name": "search_policy",
     "description": "Search the Pintar returns, refunds and delivery "
                    "policy. Returns the matching sections with their numbers.",
     "input_schema": {"type": "object", "required": ["query"], "properties": {
         "query": {"type": "string",
                   "description": "Keywords, e.g. duplicate charge"}}}},
]


def _rows(sql, args=()):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in con.execute(sql, args)]
    finally:
        con.close()


def find_customer(query):
    q = query.strip()
    found = _rows('SELECT * FROM customers WHERE customer_id = ? OR lower(email) = lower(?)', (q, q))
    if not found:
        return 'No customer matches %r.' % q
    c = found[0]
    c['recent_orders'] = _rows('SELECT order_id, placed_at, status, total_myr FROM orders WHERE customer_id = ? '
                               'ORDER BY placed_at DESC LIMIT 5', (c['customer_id'],))
    return json.dumps(c)


def get_order(order_id):
    order = _rows('SELECT * FROM orders WHERE order_id = ?', (order_id.strip(),))
    if not order:
        return 'Order %s not found.' % order_id
    o = order[0]
    o['items'] = _rows('SELECT i.product_id, p.name, i.qty, i.unit_price_myr FROM order_items i JOIN products p USING (product_id) '
                       'WHERE i.order_id = ?', (o['order_id'],))
    o['payments'] = _rows('SELECT payment_id, method, amount_myr, status, paid_at FROM payments WHERE order_id = ? ORDER BY paid_at', (o['order_id'],))
    o['shipment'] = (_rows('SELECT courier, tracking_no, shipped_at, promised_by FROM shipments WHERE order_id = ?', (o['order_id'],)) or [None])[0]
    o['tracking'] = _rows('SELECT at, location, event FROM tracking_events WHERE order_id = ? ORDER BY at', (o['order_id'],))
    o['refunds'] = _rows('SELECT refund_id, amount_myr, reason, status, created_at FROM refunds WHERE order_id = ?', (o['order_id'],))
    return json.dumps(o)


def search_policy(query):
    words = [w for w in re.findall(r'[a-z0-9]+', query.lower()) if len(w) > 2]
    sections = re.split(r'\n(?=## )', POLICY)
    scored = sorted(((sum(s.lower().count(w) for w in words), s) for s in sections[1:]), reverse=True)
    hits = [s.strip() for score, s in scored[:2] if score > 0]
    return '\n\n'.join(hits) if hits else 'No policy section matches %r.' % query


def run_tool(name, tool_input):
    if name == "find_customer":
        return find_customer(**tool_input)
    if name == "get_order":
        return get_order(**tool_input)
    if name == "search_policy":
        return search_policy(**tool_input)
    return f"unknown tool: {name}"
