# Lab 7. Grants Server

Lesson 8, Skills, Plugins, and MCP. Grant Desk's tools so far live inside one program. The Fund's officers also work in
Claude Code, and other teams build their own assistants, so the grants system becomes a Model Context Protocol (MCP)
server that any client can start and use. The way to use it, the eligibility checklist, becomes a Skill that Claude
loads only when an officer asks to assess a claim.

Files: [`grants_server.py`](grants_server.py), the Skill at
[`.claude/skills/grant-eligibility/SKILL.md`](.claude/skills/grant-eligibility/SKILL.md), the client
[`grants_client.py`](grants_client.py), and [`.mcp.json`](.mcp.json), which tells Claude Code how to start the server.
Time: about 35 minutes.

## Steps

1. **A tool.** Expose `get_claim` with `@server.tool()`. The function's docstring is the description Claude reads,
   and its `Args:` section describes the parameter. Return a helpful message for an unknown claim.
2. **A tool that writes.** Expose `save_decision`. Refuse an outcome outside Approve, Partial, Reject, and Refer, and
   save the rest with `grants.record_decision`.
3. **A resource.** Expose the guide at `grants://guide` with the MIME type `text/markdown`. A resource is data the
   client reads, where a tool is an action Claude calls.
4. **The Skill's description.** Claude reads only the name and description of every Skill until one fits the request,
   so the description says what the Skill does and when to use it.
5. **The Skill's checklist.** Write one numbered line per rule, each naming its tool and its reason code, in the order
   that stops at the first rejection.

Start the server through the client:

```
python run.py labs/lab07_grants_server/grants_client.py
```

You should see four tools with their required parameters, the guide resource, claim CLM-24004, the helpful message
for a malformed claim number, and the size of the guide.

With Claude Code installed, open a terminal in this folder, start `claude`, approve the `grants` server, and ask
"Assess claim CLM-24004". Claude loads the Skill and works through it with the server's tools.

## Check

```
python labs/check.py 7
```

## Try Next

Delete the `Args:` section of `get_claim`, run the client, and compare the input schema it prints. Then read the
Skill's description as Claude would and ask whether "check CLM-24020 for me" would load it.

## Hints

<details><summary>Hint 1</summary>

Follow `check_eligibility`, which is already a tool: decorator, typed parameters, docstring with `Args:`, JSON result.
</details>

<details><summary>Hint 2</summary>

`@server.resource("grants://guide", mime_type="text/markdown")` above a function that returns `GUIDE`.
</details>

<details><summary>Hint 3</summary>

A Skill's front matter has `name` and `description`. For example: "Assesses a training grant claim of the Acme Skills
Fund against the grant guide. Use it when an officer asks to assess, check, or decide a claim such as CLM-24001."
</details>
