"""Lab 7. The grants system as a Model Context Protocol (MCP) server over stdio.

Any MCP client can use it: grants_client.py in this folder, or Claude Code through .mcp.json. Complete the three
TODO steps, then run the client from the ccdvf folder:
    python run.py labs/lab07_grants_server/grants_client.py
"""
import json
import logging

from mcp.server import MCPServer
from grants import GUIDE, calculate_grant, claim, query, record_decision

logging.basicConfig(level=logging.INFO)   # logs go to stderr; stdout carries the protocol
log = logging.getLogger("grants")
server = MCPServer("grants")


# TODO 1: expose get_claim as a tool. Decorate the function with @server.tool(); its docstring becomes
# the description Claude reads, and its "Args:" section describes the parameter. Return the claim as JSON,
# or a message naming the expected form (CLM-24001) when there is no such claim.


@server.tool()
def check_eligibility(claim_id: str) -> str:
    """The facts behind the eligibility rules: employer status and contributions, provider registration, trainer
    accreditation, and earlier claims for the same course run.

    Args:
        claim_id: Claim number in the form CLM-24001
    """
    log.info("check_eligibility %s", claim_id)
    c = claim(claim_id)
    if not c:
        return f"No claim {claim_id}."
    return json.dumps({
        "employer": query("SELECT * FROM employers WHERE name = ?", c["employer"])[0],
        "provider": query("SELECT * FROM providers WHERE name = ?", c["provider"])[0],
        "trainer": query("SELECT * FROM trainers WHERE name = ?", c["trainer"])[0],
        "earlier_claims_same_run": query("SELECT claim_id, submitted_on, employer FROM claims WHERE class_id = ? "
                                         "AND submitted_on < ?", c["class_id"], c["submitted_on"]),
        "training": {"start_date": c["start_date"], "end_date": c["end_date"], "submitted_on": c["submitted_on"]}})


@server.tool()
def grant_amount(claim_id: str) -> str:
    """Applies the attendance rule, the caps, and the balance (guide Sections 4 to 6): the grant and its codes.

    Args:
        claim_id: Claim number in the form CLM-24001
    """
    log.info("grant_amount %s", claim_id)
    return json.dumps(calculate_grant(claim_id)) if claim(claim_id) else f"No claim {claim_id}."


# TODO 2: expose save_decision as a tool with the parameters claim_id (str), outcome (str: Approve,
# Partial, Reject, or Refer), grant (float), reasons (list[str]), and note (str). Refuse an outcome outside
# those four with a message, otherwise record it with grants.record_decision and return its confirmation.


# TODO 3: expose the grant guide as a resource at the URI grants://guide with the MIME type
# text/markdown, so a client can read the whole guide.


if __name__ == "__main__":
    server.run()   # stdio, the default transport
