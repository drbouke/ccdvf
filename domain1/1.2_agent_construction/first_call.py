"""One request: Claude triages a customer email against the full Pintar policy."""
import json
import anthropic
from meter import Meter, text
from pintar_tools import DATA, POLICY

MODEL = "claude-haiku-5-5"
lines = (DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()
ticket = json.loads(lines[0])

client = anthropic.Anthropic()
meter = Meter(MODEL)
resp = meter.add(client.messages.create(
    model=MODEL,
    max_tokens=1200,
    system=("You are a Pintar customer service team lead. "
            "Apply only this policy:\n\n" + POLICY),
    messages=[{"role": "user", "content":
               "Triage this ticket concisely: category, urgency, the policy "
               "sections that apply, and the next step.\n\n" + ticket["text"]}],
))
print(ticket["ticket_id"], ticket["text"], "\n")
print(text(resp))
print("\nstop_reason:", resp.stop_reason, "|", meter.report())
