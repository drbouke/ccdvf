"""Lab 9. Measure Grant Desk on twenty claims that officers have already decided.

assess.py is the finished assessor of Lab 8. Complete the five TODO steps, then run from the ccdvf folder:
    python run.py labs/lab09_desk_evaluation/evaluate.py
"""
import json
from pathlib import Path

import anthropic
from assess import MODEL, build_params, parse_decision
from meter import Meter, text

HERE = Path(__file__).resolve().parent
EVAL_SET = HERE.parent / "data" / "eval_set.jsonl"
OUT = HERE / "out" / "eval_report.json"
JUDGE = ("You review the note a claims assistant wrote for a claims officer. Score it from 1 to 5: 5 when it states "
         "the outcome, gives the reason behind every reason code, and cites the guide section of each rule it "
         "applies; 3 when one of these is missing; 1 when it is wrong or empty. Be strict.")
SCORE = {"type": "object",
         "properties": {"score": {"type": "integer", "enum": [1, 2, 3, 4, 5]}, "why": {"type": "string"}},
         "required": ["score", "why"], "additionalProperties": False}


def grade(decision: dict, expected: dict) -> dict:
    """Code-graded checks of one decision against the officers' decision."""
    # TODO 3: return three booleans: "outcome" (the outcomes are equal), "reasons" (the same set of
    # reason codes, in any order), and "grant" (within USD 1 of the expected grant).
    return {"outcome": False, "reasons": False, "grant": False}


def main():
    client = anthropic.Anthropic()
    meter = Meter(MODEL)
    # TODO 1: read the eval set: one JSON object per line, each with claim_id and the expected
    # outcome, grant, and reasons.
    cases = []
    results = []
    for case in cases:
        # TODO 2: assess the claim with one request built by build_params, counted by the meter, and
        # turn the reply into a decision with parse_decision, which marks a cut-off reply as an Error.
        decision = {"outcome": "", "grant": 0, "reasons": [], "note": ""}
        checks = grade(decision, case)
        results.append({"claim_id": case["claim_id"], "expected": case, "decision": decision, "checks": checks})
        marks = " ".join(f"{k} {'ok' if v else 'MISS'}" for k, v in checks.items())
        print(f"{case['claim_id']}: {decision['outcome']:<8} {marks}")
    # TODO 4: score the notes of the first five decisions with a judge model: one request each, with
    # the JUDGE system prompt, the claim's expected decision and the note in the user message, and output
    # that follows SCORE, and thinking disabled so the short verdict always fits. Store the score and the
    # reason in each result under "judge".
    # TODO 5: compute the share of results whose outcome, reasons, and grant checks passed, and the
    # mean judge score; print them, and save them with every result to OUT as indented JSON.
    print(meter.report())


if __name__ == "__main__":
    main()
