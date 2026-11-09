"""Lab 2. Grant Desk reads a claim's scanned attendance list and PDF invoice.

Complete the five TODO steps in order, then run from the ccdvf folder:
    python run.py labs/lab02_read_documents/read_claim.py CLM-24001
"""
import base64
import sys
from pathlib import Path

import anthropic
from meter import Meter

MODEL = "claude-haiku-5-5"
CLAIMS = Path(__file__).resolve().parent.parent / "data" / "claims"
SYSTEM = ("You are Grant Desk, the claims assistant of the Acme Skills Fund. "
          "You check training grant claims against the Fund's grant guide.")
QUESTION = (
    "Compare the attendance list with the invoice. First list each trainee "
    "with the days attended out of the training days, for example 3/5. "
    "A day counts as attended only when the trainee's initials are in its "
    "cell. Then give the invoice total, and name every trainee the invoice "
    "bills who attended fewer than 80 percent of the training days.")


def image_block(path: Path) -> dict:
    """The attendance scan as an image content block."""
    # TODO 1: return an image block whose source is the file's bytes,
    # base64 encoded, with the media type "image/jpeg".
    return {}


def pdf_block(path: Path) -> dict:
    """The invoice as a document content block."""
    # TODO 2: return a document block whose source is the PDF's bytes,
    # base64 encoded, with the media type "application/pdf".
    return {}


def main():
    claim = sys.argv[1] if len(sys.argv) > 1 else "CLM-24001"
    folder = CLAIMS / claim
    client = anthropic.Anthropic()
    meter = Meter(MODEL)

    # TODO 3: build the content of the user message: the attendance image,
    # then the invoice document, then QUESTION as a text block. Documents go
    # before the question.
    content = []

    print(f"Claim {claim}\n")
    # TODO 4: stream the reply with client.messages.stream (MODEL,
    # max_tokens of 1500, SYSTEM, one user message with the content), and
    # print each piece of text as it arrives, on the same line.

    # TODO 5: after the stream ends, pass its final message to meter.add(),
    # then print a blank line and meter.report().


if __name__ == "__main__":
    main()
