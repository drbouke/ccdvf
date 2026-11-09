# Lab 4. Grant Tools

Lesson 4, Tools. A claim can be read from its documents, but deciding it needs facts that live in the grants system:
whether the employer is active, whether the trainer's accreditation covered every training day, whether the run was
claimed before. Grant Desk gets these facts through tools. Claude asks for a tool, your code runs it, and the result
goes back to Claude, until Claude records a decision.

Programs: [`grants.py`](grants.py) holds the tools, and [`assess_agent.py`](assess_agent.py) holds the agent loop.
Time: about 35 minutes.

## Steps

1. **Tool definition** (`grants.py`). Add the `get_trainer` definition to `TOOLS`: a `name`, a `description` that says
   what the tool returns, and an `input_schema` with one required string, `name`. The description is all Claude knows
   about the tool, so say exactly what it returns.
2. **Tool code** (`grants.py`). In `run_tool`, answer `get_trainer` from the `trainers` table. For an unknown name,
   return a message that tells Claude what to try, with `is_error` set to `True`.
3. **Stop or continue** (`assess_agent.py`). When the stop reason is not `tool_use`, return Claude's text. Otherwise
   add Claude's turn, `response.content`, to `messages` as an assistant message.
4. **Run the tools.** For every `tool_use` block, run the tool, print a trace line, and build a `tool_result` block
   with the block's `id`, the result text, and `is_error`.
5. **Send the results.** Append all the results in one user message, so the loop can send the next request.

Run the agent on three claims:

```
python run.py labs/lab04_grant_tools/assess_agent.py CLM-24001 CLM-24004 CLM-24006
```

You should see each tool call as a trace line, and three decisions: CLM-24001 Partial (one trainee below 80 percent),
CLM-24004 Approve, and CLM-24006 Reject. Read the trace of CLM-24006 and find the fact that rejects it.

## Check

```
python labs/check.py 4
```

The check clears the decisions of these three claims, runs your agent, and compares what it recorded with the
officers' decisions.

## Try Next

Run claim CLM-24007 and read how the agent finds that it duplicates an earlier claim. Then ask for a claim that does
not exist, such as CLM-99999, and see how the error message steers Claude.

## Hints

<details><summary>Hint 1</summary>

Copy the shape of `get_provider`: the same `input_schema`, with a description about the trainer's accreditation
number and the last day it is valid. The query in `run_tool` follows the `get_provider` branch the same way.
</details>

<details><summary>Hint 2</summary>

Claude's turn must go back exactly as it came, tool calls included: `{"role": "assistant", "content": response.content}`.
The results go back in a user message whose content is the list of `tool_result` blocks.
</details>

<details><summary>Hint 3</summary>

```python
result, is_error = run_tool(block.name, block.input)
print(f"  -> {block.name}({json.dumps(block.input)})")
results.append({"type": "tool_result", "tool_use_id": block.id,
                "content": result, "is_error": is_error})
```
</details>
