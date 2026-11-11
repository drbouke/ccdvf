# 2. Claude API

Part 1. Building with Claude. The lesson covers 2.1 Requests with Files.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `read_slip.py` | An image in a request | The courier slip read from a picture and checked against the store record |
| 2 | `files_api.py` | The Files API | The invoice uploaded once, two questions by file id, then deleted |
| 3 | `stream_events.py` | Streaming events (extra practice) | Each server-sent event of one reply, in arrival order |
| 4 | `stream_tool.py` | A streamed tool call (extra practice) | The tool input as it arrives, and when it becomes valid JSON |

Run every program from the `ccdvf` folder, for example:

```
python run.py part1/02_claude_api/files_api.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
