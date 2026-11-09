"""Lab 6. A lead agent hands each course run to an auditor subagent, which finds duplicate and overlapping claims.

Complete the four TODO steps, then run from the ccdvf folder:
    python run.py labs/lab06_duplicate_auditor/auditor.py 2026-11-06
"""
import json
import sys
from pathlib import Path

import anthropic
from grants import query
from meter import Meter, text

MODEL = "claude-haiku-5-5"
OUT = Path(__file__).resolve().parent / "out" / "audit.json"

LEAD = ("You are the lead auditor of the Acme Skills Fund. List the claims submitted on the day the officer names, "
        "then call audit_course_run once for every distinct class id among them. When every run is audited, report "
        "in three sentences which claims are duplicates (D1), which overlap with another employer's claim (O1), and "
        "which are clear.")
AUDITOR = ("You audit the claims of one course run for the Acme Skills Fund. Section 8 of the grant guide: a claim "
           "whose trainees were all claimed before for the same run, under another claim number, is a duplicate "
           "(D1). Claims from different employers for the same run that share trainee ids overlap, and both are "
           "referred (O1). Compare trainee ids, not names. Return one finding for every claim you are given.")
FINDINGS = {
    "type": "object",
    "properties": {"findings": {"type": "array", "items": {
        "type": "object",
        "properties": {
            "claim_id": {"type": "string"},
            "finding": {"type": "string", "enum": ["duplicate", "overlap", "clear"]},
            "code": {"type": "string", "enum": ["D1", "O1", "none"]},
            "with_claim": {"type": "string", "description": "The other claim, or an empty string"},
            "evidence": {"type": "string"}},
        "required": ["claim_id", "finding", "code", "with_claim", "evidence"],
        "additionalProperties": False}}},
    "required": ["findings"],
    "additionalProperties": False,
}
TOOLS = [
    {"name": "list_claims", "description": "Claims submitted on one day: claim id, employer, course code, and class id.",
     "input_schema": {"type": "object", "properties": {"day": {"type": "string", "description": "YYYY-MM-DD"}},
                      "required": ["day"]}},
    {"name": "audit_course_run",
     "description": ("Hands one course run to an auditor, who reads every claim ever made for it and returns a finding "
                     "for each claim: duplicate (D1), overlap (O1), or clear."),
     "input_schema": {"type": "object", "properties": {"class_id": {"type": "string"}}, "required": ["class_id"]}},
]


def run_claims(class_id: str) -> list:
    """Every claim for one course run, oldest first, with its trainees."""
    rows = query("SELECT claim_id, submitted_on, employer, course_code, start_date, end_date, trainees "
                 "FROM claims WHERE class_id = ? ORDER BY submitted_on, claim_id", class_id)
    for r in rows:
        r["trainees"] = [{"trainee_id": t["trainee_id"], "name": t["name"]} for t in json.loads(r["trainees"])]
    return rows


def audit_course_run(client, sub_meter, class_id: str) -> list:
    """The subagent: a fresh conversation that sees only this run's claims and returns findings."""
    claims = run_claims(class_id)
    # TODO 1: send one request in a new conversation: the AUDITOR system prompt, one user message
    # holding "Course run <class_id>:" and the claims as JSON, and output_config that makes the reply
    # follow FINDINGS. Count it with sub_meter.add(), parse the reply, and return its "findings" list.
    return []


def main():
    day = sys.argv[1] if len(sys.argv) > 1 else "2026-11-06"
    client = anthropic.Anthropic()
    lead_meter, sub_meter = Meter(MODEL), Meter(MODEL)
    findings = {}
    messages = [{"role": "user", "content": f"Audit the claims submitted on {day}."}]
    for _ in range(25):
        response = lead_meter.add(client.messages.create(
            model=MODEL, max_tokens=2000, system=LEAD, tools=TOOLS, messages=messages))
        if response.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": response.content})
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            if block.name == "list_claims":
                rows = query("SELECT claim_id, employer, course_code, class_id FROM claims WHERE submitted_on = ?",
                             block.input["day"])
                result = json.dumps(rows)
            else:
                # TODO 2: run the subagent for block.input["class_id"], print a line
                # "  audit <class_id>: <n> finding(s)", keep each finding in the findings dictionary under
                # its claim_id, and give the lead the findings as JSON for its tool result.
                result = "[]"
            results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
        messages.append({"role": "user", "content": results})
    print("\n" + text(response) + "\n")
    # TODO 3: write the findings of the claims submitted that day to OUT as indented JSON (create
    # the out folder first). Findings about older claims, such as the original of a duplicate, stay out.
    # TODO 4: print the lead's usage and the subagents' usage on two lines that start with
    # "Lead: " and "Auditors: ", so you can see where the tokens went.


if __name__ == "__main__":
    main()
