# 1.2 Agent Construction with Claude

This lesson builds an agent from one request to a complete loop, then adds tools and hooks. Run each program from the `ccdvf` folder, for example `python run.py domain1/1.2_agent_construction/first_call.py`.

| Program | Concept | Output |
|---|---|---|
| `first_call.py` | One request | A ticket triaged against the full policy, with stop reason and cost |
| `inspect_response.py` | Response object | Every field of one response as JSON |
| `round_trip.py` | Tool-use round trip | Each request and response in the loop, linked by tool use ID |
| `agent.py` | Tool-use loop | A two-issue complaint answered after customer, order, and policy lookups |
| `fix_tests.py` | Agent SDK on a code base | The agent finds and fixes the bug that the tests in `tests` catch |
| `refund_agent.py` | Agent SDK, custom tools, hooks | Refund cases decided by an agent, with a PreToolUse hook enforcing approval limits |
| `hook_check.py` | Deterministic hooks | The same hook applied to store orders without a model |

`fix_tests.py` edits `refunds.py`. Run `python -m pytest domain1/1.2_agent_construction/tests` before and after the agent to see the test change from failing to passing. To restore the file in a codespace, run `git checkout domain1/1.2_agent_construction/refunds.py`. On a laptop, copy the file again from the downloaded archive.
