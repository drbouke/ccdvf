# Lab 9. Desk Evaluation

Lesson 10, Debugging and Evaluation. Before the Fund lets Grant Desk prepare decisions, it must show how often Grant
Desk agrees with its officers. The eval set holds twenty claims that officers have decided, chosen to cover every
outcome and most reason codes. Code grades what can be checked exactly: the outcome, the reason codes, and the grant.
A judge model grades what code cannot: whether the note gives the officer the reason and the guide section.

Program: [`evaluate.py`](evaluate.py), with the Lab 8 assessor ready in [`assess.py`](assess.py). The eval set is
[`../data/eval_set.jsonl`](../data/eval_set.jsonl). Time: about 30 minutes.

## Steps

1. **Load the set.** Read `eval_set.jsonl`: one JSON object per line, with the claim id and the officers' outcome,
   grant, and reasons.
2. **Run each case.** Assess each claim with one request built by `build_params`, and turn the reply into a decision
   with `parse_decision`. A reply cut off at `max_tokens` becomes an `Error` decision, which counts as a miss.
3. **Grade in code.** `grade` returns three checks: the same outcome, the same set of reason codes in any order, and a
   grant within USD 1.
4. **Judge the notes.** For the first five decisions, ask a judge model to score the note from 1 to 5 against the
   rubric in `JUDGE`, with output that follows `SCORE`.
5. **Report.** Compute the share of passed checks for outcome, reasons, and grant, and the mean judge score; print them
   and save `out/eval_report.json`.

Run the evaluation:

```
python run.py labs/lab09_desk_evaluation/evaluate.py
```

You should see one line per claim with its three checks, five judge scores with their reasons, and a summary line.
Read every line marked `MISS`: each one is either a Grant Desk error or a question about the guide.

## Check

```
python labs/check.py 9
```

The check recomputes your scores from the saved results and needs an outcome accuracy of at least 80 percent.

## Try Next

The judge's reasons show what the notes lack. Change the instruction about the note in `assess.py` (for example, to
start with the outcome and name every code with its section), run the evaluation again, and compare the judge mean.
That is one turn of the improvement loop: change, measure, keep or revert.

## Hints

<details><summary>Hint 1</summary>

`[json.loads(line) for line in EVAL_SET.read_text(encoding="utf-8").splitlines() if line.strip()]`
</details>

<details><summary>Hint 2</summary>

`client.messages.create(**build_params(case["claim_id"]))` sends the same request the batch sent for that claim.
</details>

<details><summary>Hint 3</summary>

`sorted(decision["reasons"]) == sorted(expected["reasons"])` compares the codes in any order.
</details>
