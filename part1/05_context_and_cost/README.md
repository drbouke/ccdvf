# 5. Context and Cost

Part 1. Building with Claude. The lesson covers 5.1 Context and Cost.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `context_clearing.py` | Context editing | A 30-order review with old tool results cleared |
| 2 | `context_clearing.py --off` | Context editing off | The same review without clearing, for comparison |
| 3 | `cache_miss.py` | Cache invalidation | Cache tokens written and read before and after a tool description edit |

Run every program from the `ccdvf` folder, for example:

```
python run.py part1/05_context_and_cost/cache_miss.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
