# 11. Security and Safety

Part 2. Shipping with Claude. The lesson covers 11.1 Injection and Guardrails, 11.2 Hooks, and 11.3 Keys and Secrets.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `injection.py` | Indirect prompt injection | The tools Claude asks for and its summary of a seller page |
| 2 | `try_hook.py` | Testing a hook | The hook's decision on three tool calls |
| 3 | `protect_files.py` | PreToolUse hook | Blocks edits to the key file, the store database, and the Git history |

Run every program from the `ccdvf` folder, for example:

```
python run.py part2/11_security_and_safety/injection.py
```

The `recorded_runs` folder holds the real output of each program, with its tokens and cost.
