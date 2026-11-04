"""Evaluator-optimizer: one call translates a listing into French, a second call reviews it against the Acme
glossary and the facts, and the loop repeats with the feedback until the reviewer accepts (at most 3 rounds)."""
import json
import anthropic
from meter import Meter, text
from store_tools import DATA

MODEL = "claude-haiku-5-5"
GLOSSARY = json.loads((DATA / "glossary.json").read_text(encoding="utf-8"))
VERDICT = {"name": "verdict", "description": "Review result.",
           "input_schema": {"type": "object", "properties": {
               "accept": {"type": "boolean"},
               "issues": {"type": "array", "items": {"type": "string"},
                          "description": "Each problem to fix: wrong glossary term, changed fact, unnatural French"}},
               "required": ["accept", "issues"]}}
client = anthropic.Anthropic()
meter = Meter(MODEL)
product = json.loads((DATA / "product_specs.json").read_text(encoding="utf-8"))[1]   # the headphones
source = f"{product['name']}. {product['notes']} Specs: " + "; ".join(f"{k}: {v}" for k, v in product["specs"].items())

feedback, draft = "", ""
for round_no in range(1, 4):
    terms = json.dumps(GLOSSARY, ensure_ascii=False)
    ask = ("Translate this product text into natural French for "
           f"an online store. Required terms: {terms}\n\nText: {source}")
    if feedback:
        ask += (f"\n\nYour previous draft:\n{draft}\n\n"
                f"Fix these issues:\n{feedback}")
    draft = text(meter.add(client.messages.create(
        model=MODEL, max_tokens=2500,
        messages=[{"role": "user", "content": ask}])))
    review = meter.add(client.messages.create(
        model=MODEL, max_tokens=2500, tools=[VERDICT],
        tool_choice={"type": "tool", "name": "verdict"},
        messages=[{"role": "user", "content":
                   "Review this French translation strictly. It must use "
                   "the glossary terms where the concept appears, keep every "
                   "number and fact, and read naturally.\n"
                   f"Glossary: {terms}\n"
                   f"Source: {source}\nTranslation: {draft}"}]))
    verdict = next(b.input for b in review.content if b.type == "tool_use")
    status = "accepted" if verdict["accept"] else "revise"
    print(f"Round {round_no}: {status}"
          + "".join(f"\n  - {issue}" for issue in verdict["issues"]))
    if verdict["accept"]:
        break
    feedback = "\n".join(verdict["issues"])
print("\nFinal translation:\n" + draft)
print("\n" + meter.report())
