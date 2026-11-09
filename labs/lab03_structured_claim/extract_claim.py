"""Lab 3. Grant Desk turns every claim into JSON that follows one schema.

Complete the five TODO steps in order, then run from the ccdvf folder:
    python run.py labs/lab03_structured_claim/extract_claim.py
"""
import json
from pathlib import Path

import anthropic
from documents import all_claims, claim_blocks
from meter import Meter, text

MODEL = "claude-haiku-5-5"
OUT = Path(__file__).resolve().parent / "out" / "claims.json"
SYSTEM = ("You are Grant Desk, the claims assistant of the Acme Skills Fund. "
          "You read claim documents exactly as written and never guess.")
QUESTION = (
    "Extract this claim from the attendance list and the invoice. Dates are "
    "YYYY-MM-DD. A day counts as attended only when the trainee's initials "
    "are in its cell. Amounts are numbers in US dollars, without symbols.")

SCHEMA = {
    "type": "object",
    "properties": {
        "class_id": {"type": "string"},
        "course_title": {"type": "string"},
        "employer": {"type": "string"},
        "provider": {"type": "string"},
        "trainer": {"type": "string"},
        "start_date": {"type": "string"},
        "end_date": {"type": "string"},
        "training_days": {"type": "integer"},
        "invoice_number": {"type": "string"},
        "invoice_total": {"type": "number"},
        "fee_per_trainee_day": {"type": "number"},
        # TODO 1: describe one trainee: trainee_id (string), name (string),
        # and days_present (integer), all required, no other properties.
        "trainees": {"type": "array", "items": {}},
    },
    "required": ["class_id", "course_title", "employer", "provider", "trainer",
                 "start_date", "end_date", "training_days", "invoice_number",
                 "invoice_total", "fee_per_trainee_day", "trainees"],
    "additionalProperties": False,
}


def extract(client, meter, claim: str) -> dict:
    """One claim as a dictionary that follows SCHEMA."""
    content = claim_blocks(claim) + [{"type": "text", "text": QUESTION}]
    # TODO 2: send the request (MODEL, max_tokens of 2000, SYSTEM, one user
    # message with the content) with output_config set so that the reply
    # follows SCHEMA. Pass the response through meter.add().
    response = None
    # TODO 3: parse the reply text as JSON and return it.
    return {}


def claimable(data: dict) -> list:
    """The trainees who attended at least 80 percent of the training days."""
    # TODO 4: decide in code, not with Claude: a trainee is claimable when
    # days_present / training_days is at least 0.8, without rounding.
    return []


def main():
    client = anthropic.Anthropic()
    meter = Meter(MODEL)
    results = {}
    for claim in all_claims():
        data = extract(client, meter, claim)
        results[claim] = data
        ok = claimable(data)
        print(f"{claim}: {len(data['trainees'])} trainees, {len(ok)} claimable, "
              f"invoice USD {data['invoice_total']:,.2f}")
    # TODO 5: write results to OUT as indented JSON, creating its folder
    # first, then print where it was saved.
    print(meter.report())


if __name__ == "__main__":
    main()
