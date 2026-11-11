# 4. Tools

Part 1. Building with Claude. The lesson covers 4.1 Tools in Practice.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `agent.py` | Tool-use loop | A two-issue complaint answered after customer, order, and policy lookups |
| 2 | `tool_errors.py` | Tool errors | Each tool call and result as a trace, then the answer |
| 3 | `tool_errors.py --generic` | Uninstructive errors | The same task when every error says only "failed" |

Run every program from the `ccdvf` folder, for example:

```
python run.py part1/04_tools/agent.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
