"""Acme reply review: a judge model scores a draft reply and says why."""
import json

import anthropic
from store_tools import DATA, POLICY

POINTS = {"type": "array", "items": {"type": "string"}}  # 1 to 3 points
VERDICT = {"format": {"type": "json_schema", "schema": {
    "type": "object", "additionalProperties": False,
    "required": ["strengths", "weaknesses", "reasoning", "score"],
    "properties": {"strengths": POINTS, "weaknesses": POINTS, "score": {
        "type": "integer"}, "reasoning": {"type": "string"}}}}}
JUDGE = ("Review the Acme support reply against this policy: 1 to 3 "
         "strengths and weaknesses, reasoning in 50 words, a score from 1 "
         "to 10.\n" + POLICY)
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
client = anthropic.Anthropic()

def chat(system, content, **extra):
    msg = client.messages.create(
        model="claude-haiku-5-5", max_tokens=1500, system=system, **extra,
        messages=[{"role": "user", "content": content}])
    return next(b.text for b in msg.content if b.type == "text")

for line in lines[:2]:  # T-1001 and T-1002
    ticket = json.loads(line)
    reply = chat("You are an Acme support agent. Reply in 60 words or fewer.",
                 ticket["text"])  # the draft, written without the policy
    verdict = json.loads(chat(JUDGE, f"<ticket>{ticket['text']}</ticket>\n"
                              f"<reply>{reply}</reply>", output_config=VERDICT))
    print(f"{ticket['ticket_id']}: score {verdict['score']}")
    print(f"  {verdict['reasoning']}")
