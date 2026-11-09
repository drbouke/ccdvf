# Lab 1. First Request

Lesson 0, Environment. Grant Desk starts as one request: a system prompt that gives it its role, one question, and a
reply. You also read what the response says about itself, because every later lab watches the stop reason, the
tokens, and the cost.

Program: [`desk.py`](desk.py). Time: about 15 minutes.

## Steps

1. **Client.** Create an `anthropic.Anthropic()` client. It finds the key in the environment, so you pass nothing.
2. **Request.** Call `client.messages.create` with the model, `max_tokens=200`, the `SYSTEM` prompt in the `system`
   field, and `QUESTION` as the one user message. Wrap the call in `meter.add(...)`.
3. **Reply.** Print `Reply: ` followed by the reply text.
4. **Stop reason and cost.** Print `Stop reason: ` followed by the response's stop reason, then `meter.report()`.

Run it from the `ccdvf` folder:

```
python run.py labs/lab01_first_request/desk.py
```

You should see one sentence in which Grant Desk introduces itself, the stop reason `end_turn`, and one line with the
call count, the tokens, and the cost.

## Check

```
python labs/check.py 1
```

## Try Next

Set `max_tokens` to 10 and run again. Read the reply and the stop reason, and explain to yourself what changed and
why. Set it back to 200 before you check.

## Hints

<details><summary>Hint 1</summary>

The system prompt is not a message. It goes in its own `system` argument, next to `model`, `max_tokens`, and
`messages`.
</details>

<details><summary>Hint 2</summary>

`messages` is a list of dictionaries, each with a `role` and a `content`. One user message is enough here.
The stop reason is an attribute of the response, next to `content` and `usage`.
</details>

<details><summary>Hint 3</summary>

```python
response = meter.add(client.messages.create(
    model=MODEL, max_tokens=200, system=SYSTEM,
    messages=[{"role": "user", "content": QUESTION}]))
```
</details>
