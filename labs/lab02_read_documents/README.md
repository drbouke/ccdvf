# Lab 2. Read the Documents

Lesson 2, Claude API. A claim arrives as two files: a scanned attendance list, where each trainee initials every day
attended, and the provider's invoice as a PDF. Grant Desk sends both to Claude in one request, asks it to compare
them, and streams the answer so the officer sees it as it is written.

Program: [`read_claim.py`](read_claim.py). Time: about 25 minutes.

Open [`../data/claims/CLM-24001/attendance.jpg`](../data/claims/CLM-24001/attendance.jpg) and
[`invoice.pdf`](../data/claims/CLM-24001/invoice.pdf) first, and find on your own who missed a day. You will compare
your answer with Claude's.

## Steps

1. **Image block.** `image_block` returns the scan as an image content block: `type` is `image`, and its `source` holds
   the type `base64`, the media type `image/jpeg`, and the file's bytes encoded as base64 text.
2. **Document block.** `pdf_block` returns the invoice the same way, as a `document` block with the media type
   `application/pdf`.
3. **Content.** The user message holds three blocks in this order: the image, the document, and `QUESTION` as a text
   block. Anthropic recommends placing long documents before the question.
4. **Stream.** Use `client.messages.stream(...)` as a context manager and print each piece of `stream.text_stream` as it
   arrives, with `end=""` and `flush=True`.
5. **Usage.** After the loop, `stream.get_final_message()` returns the whole response. Pass it to `meter.add()` and
   print the report.

Run it on the first claim, then on a longer one:

```
python run.py labs/lab02_read_documents/read_claim.py CLM-24001
python run.py labs/lab02_read_documents/read_claim.py CLM-24003
```

You should see the text appear piece by piece, each trainee with a count such as `4/5`, the invoice total, and the
trainees billed below 80 percent. Compare the counts with the scan. The input tokens are much higher than in Lab 1,
because the image and the PDF are counted as input.

## Check

```
python labs/check.py 2
```

The check tests your two block functions without calling Claude, then runs the program on claim CLM-24003.

## Try Next

Run claim CLM-24006 and work out from the grant guide which trainees are claimable and what the fee cap does to the
course fee. Lab 3 makes Claude return these facts as data that code can check.

## Hints

<details><summary>Hint 1</summary>

`base64.standard_b64encode(path.read_bytes())` returns bytes. The API needs text, so add `.decode()`.
</details>

<details><summary>Hint 2</summary>

```python
{"type": "image",
 "source": {"type": "base64", "media_type": "image/jpeg", "data": ...}}
```

The document block has the same shape with `"type": "document"`.
</details>

<details><summary>Hint 3</summary>

```python
with client.messages.stream(model=MODEL, max_tokens=1500, system=SYSTEM,
                            messages=[{"role": "user", "content": content}]) as stream:
    for piece in stream.text_stream:
        print(piece, end="", flush=True)
    final = stream.get_final_message()
```
</details>
