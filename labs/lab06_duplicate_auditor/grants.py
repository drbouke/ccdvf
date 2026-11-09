"""Grant Desk tools: the grants system as tools Claude can call.

TOOLS holds the definitions sent to Claude; run_tool() runs the tool Claude asks for and returns its result as text,
so Claude never reads the database itself. calculate_grant() applies Sections 4 to 6 of the grant guide in code.
"""
import json
import sqlite3
from contextlib import closing
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
DB = DATA / "grants.db"
GUIDE = (DATA / "grant_guide.md").read_text(encoding="utf-8")
CAP_FEE, CAP_MATERIALS, REFER_AT = 400, 50, 20000


def query(sql: str, *args) -> list:
    with closing(sqlite3.connect(DB)) as con:
        con.row_factory = sqlite3.Row
        return [dict(r) for r in con.execute(sql, args)]


def claim(claim_id: str) -> dict | None:
    rows = query("SELECT * FROM claims WHERE claim_id = ?", claim_id)
    if not rows:
        return None
    c = rows[0]
    c["trainees"] = json.loads(c["trainees"])
    return c


def calculate_grant(claim_id: str) -> dict:
    """Sections 4 to 6 of the guide in code: claimable trainees, caps, balance, and the grant."""
    c = claim(claim_id)
    employer = query("SELECT * FROM employers WHERE name = ?", c["employer"])[0]
    approval = query("SELECT * FROM approvals WHERE course_code = ?", c["course_code"])[0]
    days = min(c["training_days"], approval["training_days"])
    keep = [t for t in c["trainees"] if t["days_present"] / c["training_days"] >= 0.8]
    removed = [t["name"] for t in c["trainees"] if t not in keep]
    reasons = (["A1"] if removed else []) + (["C1"] if c["fee_per_trainee_day"] > CAP_FEE else []) \
        + (["C2"] if c["materials_per_trainee"] > CAP_MATERIALS else [])
    grant = len(keep) * (min(c["fee_per_trainee_day"], CAP_FEE) * days + min(c["materials_per_trainee"], CAP_MATERIALS))
    grant = min(grant, c["invoice_total"], approval["approved_amount"])
    if grant > employer["grant_balance"]:
        grant = employer["grant_balance"]
        reasons.append("B2")
    return {"claim_id": claim_id, "claimable_trainees": len(keep), "removed_trainees": removed,
            "grant": float(grant), "reasons": reasons, "refer_if_grant_at_least": REFER_AT}


TOOLS = [
    {"name": "get_claim",
     "description": ("The claim record: employer, provider, course code, class id, trainer, training dates and days, "
                     "submission date, invoice total, fees, and each trainee's days present."),
     "input_schema": {"type": "object", "properties": {
         "claim_id": {"type": "string", "description": "Claim number, for example CLM-24001"}},
         "required": ["claim_id"]}},
    {"name": "get_employer",
     "description": "An employer's registration status, the last month its contributions are paid for, and its grant balance.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string", "description": "Employer name exactly as on the claim"}},
         "required": ["name"]}},
    {"name": "get_provider",
     "description": "The dates between which a training provider is registered with the Fund.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string", "description": "Provider name exactly as on the claim"}},
         "required": ["name"]}},
    # Step 1: define the get_trainer tool: its name, a description that says what it returns (the
    # accreditation number and the last day the accreditation is valid), and an input_schema with one
    # required string property, name.
    {"name": "get_trainer",
     "description": "A trainer's accreditation number and the last day the accreditation is valid.",
     "input_schema": {"type": "object", "properties": {
         "name": {"type": "string", "description": "Trainer name exactly as on the claim"}},
         "required": ["name"]}},
    {"name": "find_claims",
     "description": "Every claim for one course run, found by class id, with its submission date and trainee ids.",
     "input_schema": {"type": "object", "properties": {
         "class_id": {"type": "string", "description": "Class id of the course run, for example 51207"}},
         "required": ["class_id"]}},
    {"name": "calculate_grant",
     "description": ("Applies the attendance rule, the fee and materials caps, and the employer balance (guide "
                     "Sections 4 to 6) and returns the grant with its reason codes A1, C1, C2, and B2. It does not "
                     "check eligibility: employer status, provider, trainer, deadline, or duplicates."),
     "input_schema": {"type": "object", "properties": {
         "claim_id": {"type": "string"}}, "required": ["claim_id"]}},
    {"name": "record_decision",
     "description": "Records the assessment of a claim. Call it once, as the last step.",
     "input_schema": {"type": "object", "properties": {
         "claim_id": {"type": "string"},
         "outcome": {"type": "string", "enum": ["Approve", "Partial", "Reject", "Refer"]},
         "grant": {"type": "number", "description": "USD; 0 for Reject"},
         "reasons": {"type": "array", "items": {"type": "string"}, "description": "Reason codes, for example [\"A1\"]"},
         "note": {"type": "string", "description": "One or two sentences for the officer, citing guide sections"}},
         "required": ["claim_id", "outcome", "grant", "reasons", "note"]}},
]


def record_decision(claim_id, outcome, grant, reasons, note) -> str:
    with closing(sqlite3.connect(DB)) as con:
        con.execute("INSERT OR REPLACE INTO decisions (claim_id, outcome, grant_amount, reasons, note) VALUES (?,?,?,?,?)",
                    (claim_id, outcome, float(grant), json.dumps(sorted(reasons)), note))
        con.commit()
    return f"Recorded {claim_id}: {outcome}, USD {float(grant):,.2f}, reasons {sorted(reasons)}"


def run_tool(name: str, args: dict) -> tuple[str, bool]:
    """Runs one tool; returns (result text, is_error)."""
    if name == "get_claim":
        c = claim(args["claim_id"])
        return (json.dumps(c), False) if c else (f"No claim {args['claim_id']}. Claim numbers look like CLM-24001.", True)
    if name == "get_employer":
        rows = query("SELECT * FROM employers WHERE name = ?", args["name"])
        return (json.dumps(rows[0]), False) if rows else (f"No employer named {args['name']!r}; use the name on the claim.", True)
    if name == "get_provider":
        rows = query("SELECT * FROM providers WHERE name = ?", args["name"])
        return (json.dumps(rows[0]), False) if rows else (f"No provider named {args['name']!r}; use the name on the claim.", True)
    # Step 2: run get_trainer: read the trainer's row from the trainers table and return it as JSON
    # with is_error False. For an unknown name, return a message that tells Claude what to try, with
    # is_error True.
    if name == "get_trainer":
        rows = query("SELECT * FROM trainers WHERE name = ?", args["name"])
        return (json.dumps(rows[0]), False) if rows else (f"No trainer named {args['name']!r}; use the name on the claim.", True)
    if name == "find_claims":
        rows = query("SELECT claim_id, submitted_on, employer, trainees FROM claims WHERE class_id = ? ORDER BY submitted_on",
                     args["class_id"])
        for r in rows:
            r["trainee_ids"] = [t["trainee_id"] for t in json.loads(r.pop("trainees"))]
        return json.dumps(rows), False
    if name == "calculate_grant":
        if not claim(args["claim_id"]):
            return f"No claim {args['claim_id']}.", True
        return json.dumps(calculate_grant(args["claim_id"])), False
    if name == "record_decision":
        return record_decision(**args), False
    return f"Unknown tool {name}", True
