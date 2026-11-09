# Lab 8. Nightly Review

Lesson 9, Engineering and Lifecycle. During the day an officer waits for each answer, so Grant Desk runs as an agent.
At night nobody waits: every open claim is assessed in one Message Batch, which costs half the normal price and
returns within hours; this one usually takes about five minutes. In a batch there is no conversation, so code
gathers every fact first and each claim becomes a single request that returns a structured decision.

Program: [`nightly_review.py`](nightly_review.py). `facts()` already gathers each claim's facts in code. Time: about
30 minutes, including the wait for the batch.

## Steps

1. **One request.** `build_params` returns the parameters of one request: the model, `max_tokens`, the cached
   `SYSTEM`, `output_config` with the `DECISION` schema, and a user message with the claim's facts as JSON.
2. **The batch.** Create one batch with a request per claim, each with a `custom_id` (the claim id) and its `params`.
3. **Wait.** Until the batch's `processing_status` is `ended`, wait 15 seconds, retrieve it, and print its counts.
4. **Results.** Read every result. Results do not come back in order, so the `custom_id` tells you which claim each
   one belongs to. Turn each succeeded result into a decision with `parse_decision`, which also catches a reply cut
   off at `max_tokens`, and mark the other results as errors.
5. **Save.** Write `out/decisions.csv` and print the number of claims for each outcome.

Run it:

```
python run.py labs/lab08_nightly_review/nightly_review.py
```

You should see the batch id, a few progress lines, and the counts for 40 claims across Approve, Partial, Reject, and
Refer. Open `out/decisions.csv` and read three notes.

## Check

```
python labs/check.py 8
```

## Try Next

Look up the batch in the Claude Console under Batches. Then count how many decisions the batch made that the agent of
Lab 4 would need eight or more calls to reach, and estimate what the same night would cost with the agent.

## Hints

<details><summary>Hint 1</summary>

`build_params` returns exactly what you would pass to `client.messages.create(**params)`. The batch takes it as is.
</details>

<details><summary>Hint 2</summary>

```python
batch = client.messages.batches.create(
    requests=[{"custom_id": cid, "params": build_params(cid)} for cid in claim_ids])
```
</details>

<details><summary>Hint 3</summary>

A result has `custom_id` and `result`. When `result.type` is `succeeded`, `result.message` is a normal message, and
its text block holds the decision as JSON.
</details>
