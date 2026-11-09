"""Lab 4. Grant Desk assesses a claim with tools, in an agent loop.

Complete TODO 1 and TODO 2 in grants.py, then TODO 3 to TODO 5 here, and run from the ccdvf folder:
    python run.py labs/lab04_grant_tools/assess_agent.py CLM-24001
"""
import json
import sys

import anthropic
from grants import TOOLS, run_tool
from meter import Meter, text

MODEL = "claude-haiku-5-5"
SYSTEM = (
    "You are Grant Desk, the claims assistant of the Acme Skills Fund. Assess the claim the officer names. "
    "Check every fact with the tools: the claim, the employer's status and contributions, the provider's "
    "registration and the trainer's accreditation on every training day, the 180-day deadline, and earlier "
    "claims for the same course run. Then call calculate_grant for the amount and its reason codes. "
    "Reject when any eligibility rule fails (codes E1, P1, T1, S1, D1). Otherwise record Partial when "
    "calculate_grant returns reason codes, Refer when the grant is USD 20,000 or more, and Approve "
    "otherwise. Finish by calling record_decision once, then summarize the decision in two sentences.")


def assess(client, meter, claim_id: str) -> str:
    messages = [{"role": "user", "content": f"Assess claim {claim_id}."}]
    for _ in range(20):  # a ceiling on turns, so a confused loop cannot run up costs
        response = meter.add(client.messages.create(
            model=MODEL, max_tokens=2000, system=SYSTEM, tools=TOOLS, messages=messages))
        # TODO 3: when the stop reason is not "tool_use", Claude has finished: return its text.
        # Otherwise append Claude's turn to messages as an assistant message with response.content.
        return text(response)  # replace this line
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            # TODO 4: run the tool with run_tool(block.name, block.input), print a trace line
            # "  -> name(arguments)" with the arguments as JSON, and add a tool_result block that
            # carries the block's id, the result text, and is_error.
        # TODO 5: send every result back in one user message.
    return "Stopped after 20 turns without a decision."


def main():
    claims = sys.argv[1:] or ["CLM-24001", "CLM-24004", "CLM-24006"]
    client = anthropic.Anthropic()
    meter = Meter(MODEL)
    for claim_id in claims:
        print(claim_id)
        print(assess(client, meter, claim_id), "\n")
    print(meter.report())


if __name__ == "__main__":
    main()
