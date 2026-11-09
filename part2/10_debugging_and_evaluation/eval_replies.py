"""Acme reply eval: draft replies, grade each in code, report the average."""
import json
import re

import anthropic
from store_tools import DATA, POLICY

SYSTEM = ("You are an Acme support agent. Reply in at most 80 words and "
          "cite the policy section you apply, such as 2.1.\n" + POLICY)
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
dataset = [json.loads(line) for line in lines[:6]]  # six test cases
client = anthropic.Anthropic()


def run_prompt(case):
    msg = client.messages.create(
        model="claude-haiku-5-5", max_tokens=1000, system=SYSTEM,
        messages=[{"role": "user", "content": case["text"]}])
    return next(b.text for b in msg.content if b.type == "text")


def grade(case, output):
    """A code grader: half a point for the length, half for a section."""
    short = len(output.split()) <= 80
    cited = re.search(r"\b[1-5]\.[1-9]\b", output) is not None
    return (short + cited) / 2


results = [(c["ticket_id"], grade(c, run_prompt(c))) for c in dataset]
print("  ".join(f"{tid} {score}" for tid, score in results))
average = sum(score for _, score in results) / len(results)
print(f"Average score: {average:.2f}")
