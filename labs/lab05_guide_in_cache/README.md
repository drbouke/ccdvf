# Lab 5. Guide in the Cache

Lesson 5, Context and Cost. In Lab 4 Claude knew the rules only through the system prompt's summary. Grant Desk now
reads the whole grant guide on every turn, and an agent makes several turns per claim, so the same 3,000 tokens would
be paid for again and again. With prompt caching, the guide is written to the cache once and read back on every later
call at a tenth of the input price.

Program: [`cached_desk.py`](cached_desk.py). The agent loop is the one you wrote in Lab 4. Time: about 25 minutes.

## Steps

1. **Cached system prompt.** Build `SYSTEM` as a list with one text block holding `RULES` and then `GUIDE`, and mark the
   block with `"cache_control": {"type": "ephemeral"}`. Everything before the mark, the tools and then this block, is
   cached for five minutes.
2. **Count the cache.** In `CacheMeter.add`, add the response's `input_tokens`, `cache_creation_input_tokens`,
   `cache_read_input_tokens`, and `output_tokens` to their counters. The two cache fields can be `None`.
3. **Price the cache.** In `CacheMeter.cost`, a written token costs 1.25 times the input price and a read token
   0.10 times. Uncached tokens and output tokens keep their normal prices.
4. **Show each call.** Print one line per call with the tokens written, read, and not cached.

Run it on two claims:

```
python run.py labs/lab05_guide_in_cache/cached_desk.py CLM-24002 CLM-24005
```

You should see the first call write the cache and every later call read it, and a last line with the cost with and
without the cache and the share saved, about half. Run it again within five minutes: now even the first call reads.

## Check

```
python labs/check.py 5
```

## Try Next

Move `RULES` out of the cached block into a second text block placed after it, change one word of `RULES`, and run
twice. The cache still hits, because only what comes before the mark is cached. Then change one word of the guide
instead and watch the next run write the cache again.

## Hints

<details><summary>Hint 1</summary>

`system` accepts a string or a list of text blocks. Only a block can carry `cache_control`.
</details>

<details><summary>Hint 2</summary>

`u.cache_read_input_tokens or 0` turns `None` into 0. `input_tokens` counts only the tokens after the last cache mark.
</details>

<details><summary>Hint 3</summary>

```python
return (self.uncached * price_in + self.written * price_in * WRITE
        + self.read * price_in * READ + self.output * price_out)
```
</details>
