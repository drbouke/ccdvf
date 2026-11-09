"""Acme support assistant: keep a chat going across several turns."""
import anthropic
from store_tools import POLICY

client = anthropic.Anthropic()
# chat replies stay short: two sentences
SYSTEM = ("You are an Acme support agent. Answer in at most two "
          "sentences. Apply this policy:\n" + POLICY)


def ask(messages: list[dict]) -> str:
    """Send one request with the given conversation; return the reply."""
    response = client.messages.create(model="claude-haiku-5-5",
                                      max_tokens=800,  # thinking + reply
                                      system=SYSTEM, messages=messages)
    return "".join(b.text for b in response.content if b.type == "text")


complaint = {"role": "user", "content": ("My Air Fryer XL arrived with a "
                                         "cracked basket. I would like a "
                                         "replacement.")}
reply = {"role": "assistant", "content": ask([complaint])}
follow_up = {"role": "user",
             "content": "Refund it instead. Do I pay the return postage?"}

print("Without history:", ask([follow_up]))
print("With history:   ", ask([complaint, reply, follow_up]))
