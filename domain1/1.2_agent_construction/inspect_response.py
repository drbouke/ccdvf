"""The whole response object of one request, as JSON, so every field can be read: the id, the role, the content blocks
(a thinking block can come before the text), stop_reason and the token usage."""
import json
import anthropic
from store_tools import DATA, POLICY

ticket = json.loads((DATA / "tickets.jsonl").read_text(encoding="utf-8").splitlines()[0])
client = anthropic.Anthropic()
resp = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=1200,
    system="You are an Acme customer service team lead. Apply only this policy:\n\n" + POLICY,
    messages=[{"role": "user", "content": "Triage this ticket in two sentences: category, urgency "
               "and the next step.\n\n" + ticket["text"]}],
)
print(json.dumps(resp.to_dict(), indent=2, ensure_ascii=False))
