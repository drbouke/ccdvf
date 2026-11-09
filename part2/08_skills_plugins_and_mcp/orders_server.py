"""Acme orders as a Model Context Protocol (MCP) server over stdio."""
import logging

from mcp.server import MCPServer
from store_tools import POLICY, get_order

logging.basicConfig(level=logging.INFO)  # logging writes to stderr
log = logging.getLogger("acme-orders")
server = MCPServer("acme-orders")


@server.tool()
def order_record(order_id: str) -> str:
    """Full record of one Acme order: items, payments, shipment, tracking.

    Args:
        order_id: Order number in the form ord_21044
    """
    log.info("order_record %s", order_id)  # stdout carries the protocol
    return get_order(order_id)


@server.resource("acme://refund-policy", mime_type="text/markdown")
def refund_policy() -> str:
    """The Acme returns, refunds and delivery policy."""
    return POLICY


if __name__ == "__main__":
    server.run()  # stdio, the default transport
