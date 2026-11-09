# Lab 3. Structured Claim

Lesson 3, Prompts and Output. In Lab 2 Claude answered in prose, which a person can read but code cannot check. Grant
Desk now asks for each claim as JSON that always follows one schema, and then applies the 80 percent rule of the
grant guide in code, where the arithmetic is exact. The model reads the documents; the code applies the rules.

Program: [`extract_claim.py`](extract_claim.py), with the Lab 2 blocks ready in [`documents.py`](documents.py).
Time: about 30 minutes.

## Steps

1. **Schema.** Complete the `items` of `trainees`: an object with `trainee_id` (string), `name` (string), and
   `days_present` (integer), all three required, and `additionalProperties` set to `false`.
2. **Request.** Send the request with `output_config={"format": {"type": "json_schema", "schema": SCHEMA}}`. With this
   setting the reply always parses and always has every required field.
3. **Parse.** The reply is one text block holding the JSON. Parse it with `json.loads` and return the dictionary.
4. **Rule in code.** `claimable` returns the trainees whose `days_present / training_days` is at least `0.8`. Read
   Section 4 of the [grant guide](../data/grant_guide.md) first: the percentage is not rounded.
5. **Save.** Write all the results to `out/claims.json` with `indent=2`, creating the `out` folder if it is missing.

Run it on every claim:

```
python run.py labs/lab03_structured_claim/extract_claim.py
```

You should see one line per claim, such as `CLM-24001: 4 trainees, 3 claimable, invoice USD 3,200.00`, then the
cost of the six requests. Open `out/claims.json` and compare one claim with its scan and invoice.

## Check

```
python labs/check.py 3
```

The check compares `out/claims.json` field by field with the documents and recomputes the claimable trainees.

## Try Next

Claim CLM-24005 runs over four days. Work out from the table in Section 4 of the guide how many days a trainee needs,
then find the trainee your code removes. Claim CLM-24006 bills USD 500 per trainee per day; note what Section 5 says
about that, because a later lab computes the grant.

## Hints

<details><summary>Hint 1</summary>

The `items` of an array is itself a schema, written the same way as the outer object: `type`, `properties`,
`required`, and `additionalProperties`.
</details>

<details><summary>Hint 2</summary>

`text(response)` returns the reply text, and `json.loads` turns it into a dictionary. For the rule, a list
comprehension over `data["trainees"]` is enough.
</details>

<details><summary>Hint 3</summary>

```python
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(results, indent=2), encoding="utf-8")
```
</details>
