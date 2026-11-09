"""Checks a Grant Claims Desk lab step by step.

    python labs/check.py 1        check Lab 1
    python labs/check.py 3        check Lab 3

Run it from the ccdvf folder. It runs your program with your API key, reads what it prints and saves, and marks each
step [ok] or [fix], with what is still missing. A lab is done when every step shows [ok].
"""
import base64
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent
ROOT = LABS.parent
EXPECTED = json.loads((LABS / ".check" / "expected.json").read_text(encoding="utf-8"))
FOLDERS = {1: "lab01_first_request", 2: "lab02_read_documents", 3: "lab03_structured_claim"}
TITLES = {1: "First Request", 2: "Read the Documents", 3: "Structured Claim"}
METER = re.compile(r"^(\d+) call\(s\), [\d,]+ input \+ [\d,]+ output tokens, USD [\d.]+, [\d.]+ s, model (\S+)", re.M)
results = []


def step(n, ok, label, fix=""):
    results.append(ok)
    print(f"  [{'ok' if ok else 'fix'}]  Step {n}. {label}" + ("" if ok else f"\n          {fix}"))


def run(program, *args):
    """Runs a lab program through run.py, as the README does; returns (exit code, output)."""
    p = subprocess.run([sys.executable, str(ROOT / "run.py"), str(program), *args], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    return p.returncode, p.stdout + ("\n" + p.stderr if p.stderr.strip() else "")


def last_error(out):
    lines = [l for l in out.strip().splitlines() if l.strip()]
    return lines[-1].strip() if lines else ""


def load(path, name):
    sys.path[:0] = [str(path.parent)]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lab1(folder):
    src = (folder / "desk.py").read_text(encoding="utf-8")
    if not re.search(r"^client\s*=\s*anthropic\.Anthropic\(", src, re.M):
        step(1, False, "Client", "client is still None: create it with anthropic.Anthropic().")
        return
    step(1, True, "Client")
    code, out = run(folder / "desk.py")
    err = last_error(out) if code else ""
    if code:
        step(2, False, "Request", "The program stopped with: " + err)
        return
    reply = re.search(r"^Reply: (.+)$", out, re.M)
    meter = METER.search(out)
    step(2, bool(meter) and meter.group(1) == "1", "Request",
         "No request was counted: wrap client.messages.create(...) in meter.add(...)." if not meter or meter.group(1) == "0"
         else "Expected exactly one request.")
    step(3, bool(reply) and "grant desk" in reply.group(1).lower(), "Reply",
         'Print the reply on one line that starts with "Reply: ". It should name Grant Desk, as the SYSTEM prompt asks.')
    stop = re.search(r"^Stop reason: (\S+)", out, re.M)
    step(4, bool(stop) and stop.group(1) == "end_turn" and bool(meter) and meter.group(2) == "claude-haiku-5-5",
         "Stop reason and cost",
         'Print "Stop reason: " and the response\'s stop_reason, then meter.report(). '
         + (f"The stop reason was {stop.group(1)}: is max_tokens back at 200?" if stop and stop.group(1) != "end_turn" else ""))


def lab2(folder):
    try:
        mod = load(folder / "read_claim.py", "read_claim")
    except Exception as e:
        step(1, False, "Image block", f"The program does not load: {e}")
        return
    scan = LABS / "data" / "claims" / "CLM-24001" / "attendance.jpg"
    pdf = LABS / "data" / "claims" / "CLM-24001" / "invoice.pdf"
    for n, fn, path, kind, media in [(1, "image_block", scan, "image", "image/jpeg"), (2, "pdf_block", pdf, "document", "application/pdf")]:
        try:
            b = getattr(mod, fn)(path)
            src = b.get("source", {})
            ok = (b.get("type") == kind and src.get("type") == "base64" and src.get("media_type") == media
                  and isinstance(src.get("data"), str) and base64.b64decode(src["data"]) == path.read_bytes())
            why = (f'Expected {{"type": "{kind}", "source": {{"type": "base64", "media_type": "{media}", "data": <base64 text>}}}}; '
                   f"got the keys {list(b)}" + (f" and source {dict((k, v if k != 'data' else '...') for k, v in src.items())}" if src else ""))
        except Exception as e:
            ok, why = False, f"{fn} raised {type(e).__name__}: {e}"
        step(n, ok, "Image block" if n == 1 else "Document block", why)
    src = (folder / "read_claim.py").read_text(encoding="utf-8")
    code, out = run(folder / "read_claim.py", "CLM-24003")
    if code:
        step(3, False, "Content", "The program stopped with: " + last_error(out))
        return
    meter = METER.search(out)
    answer = out.split("Claim CLM-24003", 1)[-1]
    step(3, bool(meter) and "11,670" in answer.replace("USD", ""), "Content",
         "The reply should give the invoice total of claim CLM-24003. Do the image, the document, and QUESTION all reach the request?")
    step(4, ".stream(" in src and ("text_stream" in src or "content_block_delta" in src), "Stream",
         "Use client.messages.stream(...) and print stream.text_stream piece by piece.")
    truth = EXPECTED["CLM-24003"]
    wrong = []
    for t in truth["trainees"]:
        m = re.search(re.escape(t["name"]) + r"[^\n]{0,60}?(\d)\s*/\s*" + str(truth["training_days"]), answer)
        if not m or int(m.group(1)) != t["days_present"]:
            wrong.append(t["name"])
    step(5, bool(meter) and meter.group(1) == "1" and not wrong and "Tom Becker" in answer.split("80", 1)[-1], "Usage and the answer",
         ("Pass stream.get_final_message() to meter.add(), then print meter.report()." if not meter or meter.group(1) != "1"
          else "Compare the counts with the scan: " + ", ".join(wrong) if wrong
          else "Name the trainee billed below 80 percent after the counts."))


def lab3(folder):
    try:
        mod = load(folder / "extract_claim.py", "extract_claim")
    except Exception as e:
        step(1, False, "Schema", f"The program does not load: {e}")
        return
    item = mod.SCHEMA["properties"]["trainees"].get("items", {})
    props = item.get("properties", {})
    ok1 = (item.get("type") == "object" and {k: v.get("type") for k, v in props.items()} ==
           {"trainee_id": "string", "name": "string", "days_present": "integer"}
           and set(item.get("required", [])) == set(props) and item.get("additionalProperties") is False)
    step(1, ok1, "Schema", "Each trainee is an object with trainee_id (string), name (string) and days_present (integer), "
                           "all required, with additionalProperties false.")
    cases = [(5, [5, 4, 3]), (4, [4, 3]), (2, [2, 1]), (3, [3, 2])]
    got = [len(mod.claimable({"training_days": d, "trainees": [{"days_present": p} for p in ps]})) for d, ps in cases]
    rule_ok = got == [2, 1, 1, 1]
    if not ok1:
        step(4, rule_ok, "Rule in code", "claimable() keeps a trainee when days_present / training_days >= 0.8, unrounded.")
        return
    out_file = folder / "out" / "claims.json"
    if out_file.exists():
        out_file.unlink()
    code, out = run(folder / "extract_claim.py")
    if code:
        err = last_error(out)
        n = 2 if "content" in err or "NoneType" in err else 3
        step(n, False, "Request" if n == 2 else "Parse", "The program stopped with: " + err)
        return
    meter = METER.search(out)
    step(2, bool(meter) and meter.group(1) == str(len(EXPECTED)), "Request",
         f"Expected {len(EXPECTED)} requests counted by meter.add(), one per claim.")
    if not out_file.exists():
        step(3, True, "Parse")
        step(4, rule_ok, "Rule in code", "claimable() keeps a trainee when days_present / training_days >= 0.8, unrounded.")
        step(5, False, "Save", "out/claims.json was not written.")
        return
    data = json.loads(out_file.read_text(encoding="utf-8"))
    step(3, all(isinstance(v, dict) and v.get("trainees") for v in data.values()), "Parse", "Return json.loads(text(response)).")
    lines = dict(re.findall(r"^(CLM-\d+): \d+ trainees, (\d+) claimable", out, re.M))
    printed_ok = all(int(lines.get(c, -1)) == len(mod.claimable(d)) for c, d in data.items())
    step(4, rule_ok and printed_ok, "Rule in code",
         "claimable() keeps a trainee when days_present / training_days >= 0.8, unrounded. "
         f"On test claims it kept {got} trainees; the right counts are [2, 1, 1, 1].")
    misread = []
    for claim, truth in EXPECTED.items():
        d = data.get(claim, {})
        diffs = [k for k in ("class_id", "start_date", "end_date", "training_days", "invoice_number")
                 if str(d.get(k)) != str(truth[k])]
        diffs += [k for k in ("invoice_total", "fee_per_trainee_day") if abs(float(d.get(k) or 0) - truth[k]) > 0.01]
        theirs = {t.get("trainee_id"): t.get("days_present") for t in d.get("trainees", [])}
        diffs += [t["name"] for t in truth["trainees"] if theirs.get(t["trainee_id"]) != t["days_present"]]
        if len(theirs) != len(truth["trainees"]):
            diffs.append("number of trainees")
        if diffs:
            misread.append(f"{claim} ({', '.join(diffs)})")
    step(5, not misread, "Save, and every claim read as its documents show",
         "These fields differ from the documents: " + "; ".join(misread)
         + ". Open the scan and the invoice, and make the QUESTION or the SYSTEM prompt clearer where Claude misread them.")


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit() or int(sys.argv[1]) not in FOLDERS:
        sys.exit(__doc__)
    n = int(sys.argv[1])
    folder = LABS / FOLDERS[n]
    if "--dir" in sys.argv:
        folder = Path(sys.argv[sys.argv.index("--dir") + 1]).resolve()
    print(f"Lab {n}. {TITLES[n]}\n")
    [lab1, lab2, lab3][n - 1](folder)
    done = bool(results) and all(results)
    print("\n" + ("Lab complete." if done else "Fix the steps marked [fix], then check again."))
    sys.exit(0 if done else 1)


if __name__ == "__main__":
    main()
