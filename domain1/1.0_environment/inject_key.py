"""Follow the API key from the .env file to the request Claude receives.

Open this file in VS Code and run it from the terminal:

    python domain1/1.0_environment/inject_key.py
"""
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

print("1 before load_dotenv:", os.environ.get("ANTHROPIC_API_KEY"))
load_dotenv(ENV_FILE)
print("2 after load_dotenv: ", os.environ.get("ANTHROPIC_API_KEY"))


def show_header(response):
    headers = response.request.headers
    sent = headers.get("authorization") or headers["x-api-key"]
    print("4 request header:    ", sent[:25], "...")


hooks = {"response": [show_header]}
http = anthropic.DefaultHttpxClient(event_hooks=hooks)
client = anthropic.Anthropic(http_client=http)
print("3 client.api_key:    ", client.api_key[:18], "...")

resp = client.messages.create(
    model="claude-haiku-5-5",
    max_tokens=2500,
    messages=[{"role": "user", "content": "Reply with the word: Ready"}],
)
text = "".join(b.text for b in resp.content if b.type == "text")
print("5 Claude answered:   ", text.strip())
