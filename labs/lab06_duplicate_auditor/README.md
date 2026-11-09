# Lab 6. Duplicate Auditor

Lesson 6, Agents. Every evening the Fund audits the day's claims for duplicates and overlaps. A course run can carry
claims from months before, and reading them all in one conversation would fill the context with trainee lists. So a
lead agent lists the day's claims and hands each course run to an auditor subagent: a fresh conversation that sees
only that run's claims and returns short findings. The lead's context stays small, and each auditor works with only
what it needs.

Program: [`auditor.py`](auditor.py). Time: about 30 minutes.

## Steps

1. **The subagent.** In `audit_course_run`, send one request in a new conversation: the `AUDITOR` system prompt, the
   run's claims as JSON in the user message, and `output_config` that makes the reply follow `FINDINGS`. Count it with
   `sub_meter` and return the list of findings.
2. **Delegate.** When the lead calls `audit_course_run`, run the subagent for that class id, print a line with the
   number of findings, keep each finding by claim id, and return the findings to the lead as JSON.
3. **Save.** Write the findings of the day's claims to `out/audit.json`. The original of a duplicate is an older claim,
   so it stays out.
4. **Where the tokens went.** Print the lead's usage and the auditors' usage on two lines.

Run the audit of 6 November 2026:

```
python run.py labs/lab06_duplicate_auditor/auditor.py 2026-11-06
```

You should see one audit line per course run, the lead's three-sentence report, and two usage lines. The report names
one duplicate (D1) and one pair of overlapping claims (O1) and calls the rest clear.

## Check

```
python labs/check.py 6
```

## Try Next

Compare the two usage lines. Then change `AUDITOR` so it compares names instead of trainee ids, run again, and look
for a false duplicate: two different trainees can share a name.

## Hints

<details><summary>Hint 1</summary>

A subagent here is not a special object. It is a separate `messages.create` call with its own system prompt and its
own `messages` list, started fresh for each run.
</details>

<details><summary>Hint 2</summary>

`json.loads(text(response))["findings"]` returns the list. In the lead's loop, `block.input["class_id"]` is the run to
audit.
</details>

<details><summary>Hint 3</summary>

```python
todays = {r["claim_id"] for r in query("SELECT claim_id FROM claims WHERE submitted_on = ?", day)}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({k: v for k, v in findings.items() if k in todays}, indent=2), encoding="utf-8")
```
</details>
