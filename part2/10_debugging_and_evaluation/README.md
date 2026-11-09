# 10. Debugging and Evaluation

Part 2. Shipping with Claude. The lesson covers 10.1 Errors and Recovery, 10.2 Traces and Test Levels, and 10.3 Evaluations.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `errors.py` | Typed errors and retries | A rejected request and a successful one, each handled by its error class |
| 2 | `eval_replies.py` | A minimal eval | Six replies graded by code, with the average score |
| 3 | `judge.py` | A judge model | Two draft replies scored against the policy, with the reasoning |

Run every program from the `ccdvf` folder, for example:

```
python run.py part2/10_debugging_and_evaluation/errors.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
