"""Acme support assistant: upload an invoice once, ask about it twice."""
import anthropic
from meter import text
from store_tools import DATA

client = anthropic.Anthropic()
uploaded = client.files.upload(file=DATA / "invoice_ord_20931.pdf")
print(f"uploaded {uploaded.filename}: {uploaded.id[:14]}..., "
      f"{uploaded.size_bytes} bytes")

questions = ["How many payments were captured, and for how much in all?",
             "By how much does the total charged exceed the order total?"]
for question in questions:
    response = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=1500,  # room for thinking and a short answer
        messages=[{"role": "user", "content": [
            {"type": "document",  # the PDF, by its file id: no bytes sent
             "source": {"type": "file", "file_id": uploaded.id}},
            {"type": "text", "text": question + " At most 12 words."},
        ]}],
    )
    print(f"[{response.usage.input_tokens} input tokens] {text(response)}")

client.files.delete(uploaded.id)  # files stay stored until deleted
print("deleted:", uploaded.id not in [f.id for f in client.files.list()])
