"""Checks a Grant Claims Desk lab step by step.

    python labs/check.py 1        check Lab 1
    python labs/check.py 10       check Lab 10

Run it from the ccdvf folder. It runs your program with your API key, reads what it prints and saves, and marks each
step [ok] or [fix], with what is still missing. A lab is done when every step shows [ok].
"""
import base64
import csv
import sqlite3
from types import SimpleNamespace
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

LABS = Path(__file__).resolve().parent
ROOT = LABS.parent
EXPECTED = json.loads((LABS / ".check" / "expected.json").read_text(encoding="utf-8"))
FOLDERS = {1: "lab01_first_request", 2: "lab02_read_documents", 3: "lab03_structured_claim", 4: "lab04_grant_tools",
           5: "lab05_guide_in_cache", 6: "lab06_duplicate_auditor", 7: "lab07_grants_server", 8: "lab08_nightly_review",
           9: "lab09_desk_evaluation", 10: "lab10_safe_approvals"}
TITLES = {1: "First Request", 2: "Read the Documents", 3: "Structured Claim", 4: "Grant Tools", 5: "Guide in the Cache",
          6: "Duplicate Auditor", 7: "Grants Server", 8: "Nightly Review", 9: "Desk Evaluation", 10: "Safe Approvals"}
ASSESSED = json.loads((LABS / ".check" / "assessments.json").read_text(encoding="utf-8"))
DB = LABS / "data" / "grants.db"
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


def decisions(*claim_ids, clear=False):
    """The decisions recorded for these claims; with clear=True, deletes them first."""
    con = sqlite3.connect(DB)
    ph = ",".join("?" * len(claim_ids))
    if clear:
        con.execute(f"DELETE FROM decisions WHERE claim_id IN ({ph})", claim_ids)
        con.commit()
    rows = {r[0]: {"outcome": r[1], "grant": r[2], "reasons": json.loads(r[3])}
            for r in con.execute(f"SELECT claim_id, outcome, grant_amount, reasons FROM decisions WHERE claim_id IN ({ph})",
                                 claim_ids)}
    con.close()
    return rows


def matches(got, claim_id):
    e = ASSESSED[claim_id]
    return bool(got) and got["outcome"] == e["outcome"] and sorted(got["reasons"]) == e["reasons"] \
        and abs(float(got["grant"]) - e["grant"]) < 1


def lab4(folder):
    try:
        grants = load(folder / "grants.py", "grants")
    except Exception as e:
        step(1, False, "Tool definition", f"grants.py does not load: {e}")
        return
    tool = next((t for t in grants.TOOLS if t.get("name") == "get_trainer"), None)
    ok1 = bool(tool) and len(tool.get("description", "")) > 20 and tool.get("input_schema", {}).get("required") == ["name"] \
        and tool["input_schema"].get("properties", {}).get("name", {}).get("type") == "string"
    step(1, ok1, "Tool definition", "Add get_trainer to TOOLS with a description and an input_schema whose one required "
                                    "property is the string name.")
    try:
        found, err1 = grants.run_tool("get_trainer", {"name": "Priya Nair"})
        missing, err2 = grants.run_tool("get_trainer", {"name": "Nobody Here"})
        ok2 = "valid_to" in found and not err1 and err2
    except Exception as e:
        ok2, found = False, f"{type(e).__name__}: {e}"
    step(2, ok2, "Tool code", "run_tool('get_trainer', ...) should return the trainer's row as JSON with is_error False, "
                              "and a helpful message with is_error True for an unknown name. It returned: " + str(found)[:120])
    if not (ok1 and ok2):
        return
    claims = ["CLM-24001", "CLM-24004", "CLM-24006"]
    decisions(*claims, clear=True)
    code, out = run(folder / "assess_agent.py", *claims)
    if code:
        step(3, False, "Stop or continue", "The program stopped with: " + last_error(out))
        return
    traced = "-> get_claim(" in out and "-> get_trainer(" in out
    got = decisions(*claims)
    step(3, traced or bool(got), "Stop or continue",
         "The agent ended after its first reply. When the stop reason is tool_use, append Claude's turn and continue.")
    step(4, traced, "Run the tools", 'Print a trace line "  -> name(arguments)" for every tool call and build its tool_result.')
    wrong = [c for c in claims if not matches(got.get(c), c)]
    step(5, not wrong, "Send the results, and every decision right",
         "These claims were not recorded as the officers decided: " + ", ".join(
             f"{c} (recorded {got.get(c, {}).get('outcome', 'nothing')}, expected {ASSESSED[c]['outcome']} "
             f"{ASSESSED[c]['reasons']})" for c in wrong))


def lab5(folder):
    try:
        mod = load(folder / "cached_desk.py", "cached_desk")
    except Exception as e:
        step(1, False, "Cached system prompt", f"The program does not load: {e}")
        return
    sysp = mod.SYSTEM
    ok1 = isinstance(sysp, list) and len(sysp) >= 1 and sysp[-1].get("cache_control") == {"type": "ephemeral"} \
        and "Training Grant Guide" in "".join(b.get("text", "") for b in sysp)
    step(1, ok1, "Cached system prompt", 'SYSTEM is a list of text blocks holding RULES and GUIDE, the last one marked '
                                         '"cache_control": {"type": "ephemeral"}.')
    m = mod.CacheMeter()
    usage = SimpleNamespace(input_tokens=100, cache_creation_input_tokens=None, cache_read_input_tokens=3000, output_tokens=50)
    try:
        m.add(SimpleNamespace(usage=usage))
        ok2 = (m.uncached, m.written, m.read, m.output) == (100, 0, 3000, 50)
    except Exception:
        ok2 = False
    step(2, ok2, "Count the cache", "add() adds input_tokens, cache_creation_input_tokens (or 0), cache_read_input_tokens "
                                    "(or 0), and output_tokens to their counters.")
    try:
        want = (100 * 0.10 + 3000 * 0.10 * 0.10 + 50 * 0.50) / 1_000_000
        ok3 = abs(m.cost() - want) < 1e-12
    except Exception:
        ok3 = False
    step(3, ok3, "Price the cache", "A read token costs 0.10 of the input price, a written one 1.25; output keeps its price.")
    if not (ok1 and ok2 and ok3):
        return
    code, out = run(folder / "cached_desk.py", "CLM-24002")
    reads = [int(x.replace(",", "")) for x in re.findall(r"call: [\d,]+ written, ([\d,]+) read", out)]
    saved = re.search(r"(\d+)% saved", out)
    step(4, code == 0 and len(reads) >= 3 and reads[-1] > 1000 and bool(saved) and int(saved.group(1)) >= 20,
         "Show each call, and the cache paying off",
         "Print one line per call such as '  call: 0 written, 3,412 read, 220 uncached'. Later calls should read the guide "
         "from the cache. " + (("Last error: " + last_error(out)) if code else ""))


def lab6(folder):
    out_file = folder / "out" / "audit.json"
    if out_file.exists():
        out_file.unlink()
    code, out = run(folder / "auditor.py", "2026-11-06")
    if code:
        step(1, False, "The subagent", "The program stopped with: " + last_error(out))
        return
    audits = re.findall(r"^  audit (\S+): (\d+) finding", out, re.M)
    step(1, any(int(n) > 0 for _, n in audits), "The subagent",
         "audit_course_run should send its own request and return the findings list.")
    step(2, len(audits) >= 4, "Delegate", 'Run the subagent for each class id the lead asks for and print '
                                          '"  audit <class_id>: <n> finding(s)".')
    data = json.loads(out_file.read_text(encoding="utf-8")) if out_file.exists() else {}
    want = {"CLM-24007": ("duplicate", "D1"), "CLM-24010": ("overlap", "O1"), "CLM-24011": ("overlap", "O1"),
            "CLM-24008": ("clear", "none"), "CLM-24009": ("clear", "none"), "CLM-24012": ("clear", "none")}
    wrong = [c for c, fk in want.items() if (data.get(c, {}).get("finding"), data.get(c, {}).get("code")) != fk]
    step(3, bool(data) and not wrong and "CLM-24001" not in data, "Save, with the right findings",
         "out/audit.json should hold one finding for each claim of the day, and not the older CLM-24001. "
         + ("Check: " + ", ".join(wrong) if data else "The file was not written."))
    step(4, "Lead:" in out and "Auditors:" in out, "Where the tokens went",
         'Print two usage lines starting "Lead:" and "Auditors:".')


def lab7(folder):
    code, out = run(folder / "grants_client.py")
    if code:
        step(1, False, "A tool", "The client stopped with: " + last_error(out))
        return
    tools = dict(re.findall(r"^tool (\w+): (.*)$", out, re.M))
    step(1, "get_claim" in tools and "CLM-24004: Greenleaf Retail" in out and "24004: No claim" in out, "A tool",
         "Expose get_claim with @server.tool(), returning the claim as JSON or a helpful message.")
    try:
        server = load(folder / "grants_server.py", "grants_server")
        refused = "not one of" in server.save_decision("CLM-24004", "Maybe", 0, [], "x")
    except Exception:
        refused = False
    step(2, "save_decision" in tools and refused, "A tool that writes",
         "Expose save_decision with its five parameters and refuse an outcome outside the four allowed.")
    step(3, "resource grants://guide (text/markdown)" in out, "A resource",
         "Expose the guide at grants://guide as text/markdown.")
    skill = folder / ".claude" / "skills" / "grant-eligibility" / "SKILL.md"
    body_all = skill.read_text(encoding="utf-8") if skill.exists() else ""
    front = re.search(r"^---\n(.*?)\n---", body_all, re.S)
    desc = re.search(r"^description:\s*(.+)$", front.group(1), re.M) if front else None
    step(4, bool(desc) and len(desc.group(1)) > 40 and "claim" in desc.group(1).lower(), "The Skill's description",
         "Say what the Skill does and when to use it, in the description line of the front matter.")
    body = body_all[front.end():] if front else ""
    missing = [c for c in ("E1", "P1", "T1", "S1", "D1", "A1", "C1", "C2", "B2", "O1") if c not in body]
    step(5, not missing and len(re.findall(r"^\d+\.", body, re.M)) >= 6, "The Skill's checklist",
         "Write numbered steps that name each tool and every reason code. Missing: " + ", ".join(missing))


def lab8(folder):
    try:
        mod = load(folder / "nightly_review.py", "nightly_review")
        params = mod.build_params("CLM-24001")
        ok1 = bool(params.get("model")) and params.get("system") == mod.SYSTEM and \
            params.get("output_config", {}).get("format", {}).get("schema") == mod.DECISION and \
            "CLM-24001" in json.dumps(params.get("messages", ""))
    except Exception:
        ok1 = False
    step(1, ok1, "One request", "build_params returns model, max_tokens, system, output_config with DECISION, and "
                                "messages with the claim's facts.")
    out_file = folder / "out" / "decisions.csv"
    if not out_file.exists():
        step(2, False, "The batch", "Run the program first; this check reads out/decisions.csv from your run.")
        return
    rows = list(csv.DictReader(out_file.open(encoding="utf-8")))
    step(2, len(rows) == len(ASSESSED), "The batch", f"Expected {len(ASSESSED)} results, one per claim; found {len(rows)}.")
    step(3, len(rows) > 0, "Wait", "Wait until processing_status is ended before reading the results.")
    good = [r for r in rows if r["outcome"] in ("Approve", "Partial", "Reject", "Refer")]
    step(4, rows and len(good) == len(rows), "Results", "Every result should be a decision. Errored: "
                                                         + ", ".join(r["claim_id"] for r in rows if r not in good))
    agree = sum(r["outcome"] == ASSESSED.get(r["claim_id"], {}).get("outcome") for r in rows)
    step(5, agree >= 0.8 * len(ASSESSED), "Save, and the outcomes agree",
         f"{agree} of {len(ASSESSED)} outcomes agree with the officers; at least 80 percent should.")


def lab9(folder):
    out_file = folder / "out" / "eval_report.json"
    if out_file.exists():
        out_file.unlink()
    code, out = run(folder / "evaluate.py")
    if code:
        step(1, False, "Load the set", "The program stopped with: " + last_error(out))
        return
    rep = json.loads(out_file.read_text(encoding="utf-8")) if out_file.exists() else {}
    res = rep.get("results", [])
    step(1, len(res) == 20, "Load the set", f"Expected 20 cases from eval_set.jsonl; found {len(res)}.")
    step(2, bool(res) and all(r.get("decision", {}).get("outcome") for r in res), "Run each case",
         "Parse each reply into a decision.")
    regraded = [matches(r["decision"], r["claim_id"]) == all(r["checks"].values()) for r in res] if res else [False]
    step(3, all(regraded), "Grade in code", "grade() should compare outcome, reason codes in any order, and grant within USD 1.")
    judged = [r["judge"]["score"] for r in res if isinstance(r.get("judge"), dict)]
    step(4, len(judged) == 5, "Judge the notes", "Score the notes of the first five decisions with the judge model.")
    acc = rep.get("outcome_accuracy", 0)
    recomputed = sum(r["checks"]["outcome"] for r in res) / max(1, len(res))
    step(5, abs(acc - recomputed) < 1e-9 and acc >= 0.8 and "judge_mean" in rep, "Report",
         f"Save the accuracies and the judge mean. Outcome accuracy {acc:.0%} (recomputed {recomputed:.0%}); "
         "80 percent needed.")


def lab10(folder):
    code, out = run(folder / "try_guard.py")
    exits = [int(x) for x in re.findall(r"exit (\d)", out)]
    step(1, len(exits) == 4 and exits[0] == 0 and exits[1] == 2 and exits[3] == 0, "Guard: the threshold",
         "The USD 48,500 Approve must exit 2; the clean claim and the rejection must be allowed.")
    step(2, len(exits) == 4 and exits[2] == 2, "Guard: the computed grant",
         "The USD 2,500 Approve of CLM-24009 is above the computed USD 2,000 grant and must exit 2.")
    decisions("CLM-24009", clear=True)
    code, out = run(folder / "defended_intake.py")
    if code:
        step(3, False, "Untrusted documents", "The program stopped with: " + last_error(out))
        return
    found = re.search(r"^instructions found: (.*)$", out, re.M)
    src = (folder / "defended_intake.py").read_text(encoding="utf-8")
    mod_system = re.search(r"^SYSTEM = (.*?)\n(?=\S)", src, re.S | re.M)
    sys_text = mod_system.group(1).lower() if mod_system else ""
    step(3, bool(found) and "approve" in found.group(1).lower() and "evidence" in sys_text and "instruction" in sys_text,
         "Untrusted documents", "SYSTEM should say the documents are untrusted evidence, attendance comes only from the "
         "initials, and text addressed to the assessor is never followed but copied into instructions_found.")
    con = sqlite3.connect(DB)
    on_file = {t["name"]: t["days_present"] for t in json.loads(
        con.execute("SELECT trainees FROM claims WHERE claim_id = 'CLM-24009'").fetchone()[0])}
    con.close()
    read = {n: int(d) for n, d in re.findall(r"^(.+?): (\d)/2$", out, re.M)}
    framed = re.search(r'content = \[\{"type": "text", "text": "[^"]*(employer|evidence)', src, re.I)
    step(4, read == on_file and bool(framed), "Frame the documents", "The attendance read from the scan should match the initials. Check: "
         + ", ".join(f"{n} read as {read.get(n)}" for n in on_file if read.get(n) != on_file[n])
         + ("" if framed else " Start the content with a text block saying the documents come from the employer."))
    step(5, "decision: Refer" in out, "Decide in code", "With planted text found, the outcome is Refer.")
    got = decisions("CLM-24009").get("CLM-24009")
    step(6, "guard:" in out and bool(got) and got["outcome"] == "Refer", "Guard before saving",
         "Pass the decision through check(), print the guard's verdict, and save it when allowed.")


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit() or int(sys.argv[1]) not in FOLDERS:
        sys.exit(__doc__)
    n = int(sys.argv[1])
    folder = LABS / FOLDERS[n]
    if "--dir" in sys.argv:
        folder = Path(sys.argv[sys.argv.index("--dir") + 1]).resolve()
    print(f"Lab {n}. {TITLES[n]}\n")
    [lab1, lab2, lab3, lab4, lab5, lab6, lab7, lab8, lab9, lab10][n - 1](folder)
    done = bool(results) and all(results)
    print("\n" + ("Lab complete." if done else "Fix the steps marked [fix], then check again."))
    sys.exit(0 if done else 1)


if __name__ == "__main__":
    main()
