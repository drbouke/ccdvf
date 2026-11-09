"""Lab 1. Grant Desk's first request to Claude.

Complete the four TODO steps in order, then run from the ccdvf folder:
    python run.py labs/lab01_first_request/desk.py
"""
import anthropic
from meter import Meter, text

MODEL = "claude-haiku-5-5"
SYSTEM = ("You are Grant Desk, the claims assistant of the Acme Skills Fund. "
          "You check training grant claims against the Fund's grant guide.")
QUESTION = "Introduce yourself to a claims officer in one sentence."

meter = Meter(MODEL)

# TODO 1: create the client. It reads ANTHROPIC_API_KEY from the environment,
# which run.py loads from the .env file.
client = None

# TODO 2: send one request: the MODEL, max_tokens of 200, the SYSTEM prompt,
# and one user message holding QUESTION. Pass the response through
# meter.add(), which counts its tokens and returns it unchanged.
response = None

# TODO 3: print the reply, on a line that starts with "Reply: ".
# The text() helper joins the text blocks of a response.

# TODO 4: print the stop reason on a line that starts with "Stop reason: ",
# then print meter.report().
