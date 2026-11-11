# 2. Claude API

Part 1. Building with Claude. The lesson covers 2.1 Responses and Streams.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `stream_events.py` | Streaming events | Each server-sent event of one reply, in arrival order |
| 2 | `stream_tool.py` | A streamed tool call | The tool input as it arrives, and when it becomes valid JSON |

Run every program from the `ccdvf` folder, for example:

```
python run.py part1/02_claude_api/stream_tool.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
