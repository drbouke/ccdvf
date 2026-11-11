<p align="center">
  <img src="assets/ccdvf-logo.png" alt="Claude Certified Developer, Foundations logo" width="180">
</p>

<h1 align="center">Claude Certified Developer, Foundations</h1>

<p align="center">Course programs, in the order of the lessons</p>

This repository holds the programs of the CCDV-F course. The folders follow the lessons on the course platform:
first Core Concepts, then Part 1 and Part 2. Each lesson with programs has its own folder, numbered as the lesson is,
so the slide you are on always tells you where its code is. Every program also has its real output in a
`recorded_runs` folder, so you can read the result before you run it.

## Course Map

| # | Module | Lesson | Folder |
|---|---|---|---|
| 1 | Core Concepts | Core Concepts | [`core_concepts`](core_concepts) |
| 2 | Part 1 | 0. Environment | [`part1/00_environment`](part1/00_environment) |
| 3 | Part 1 | 1. Foundations | [`part1/01_foundations`](part1/01_foundations) |
| 4 | Part 1 | 2. Claude API | [`part1/02_claude_api`](part1/02_claude_api) |
| 5 | Part 1 | 3. Prompts and Output | [`part1/03_prompts_and_output`](part1/03_prompts_and_output) |
| 6 | Part 1 | 4. Tools | [`part1/04_tools`](part1/04_tools) |
| 7 | Part 1 | 5. Context and Cost | [`part1/05_context_and_cost`](part1/05_context_and_cost) |
| 8 | Part 1 | 6. Agents | [`part1/06_agents`](part1/06_agents) |
| 9 | Part 2 | 7. Claude Code | Slides only |
| 10 | Part 2 | 8. Skills, Plugins, and MCP | [`part2/08_skills_plugins_and_mcp`](part2/08_skills_plugins_and_mcp) |
| 11 | Part 2 | 9. Engineering and Lifecycle | [`part2/09_engineering_and_lifecycle`](part2/09_engineering_and_lifecycle) |
| 12 | Part 2 | 10. Debugging and Evaluation | [`part2/10_debugging_and_evaluation`](part2/10_debugging_and_evaluation) |
| 13 | Part 2 | 11. Security and Safety | [`part2/11_security_and_safety`](part2/11_security_and_safety) |
| 14 | Part 2 | 12. Exam Method | Slides only |

## Getting Started

1. Prepare the environment with [SETUP.md](SETUP.md), on a laptop or in GitHub Codespaces.
2. Check the environment. The check sends one small request and ends with `Ready.`

```
python check_setup.py --ping
```

3. Run a program from the `ccdvf` folder, giving its path:

```
python run.py core_concepts/first_request.py
python run.py part1/04_tools/agent.py
```

A program can also run with **F5** in VS Code, through the **Run this program** configuration.

## Core Concepts

Folder [`core_concepts`](core_concepts). The terms that every later lesson uses, each shown in running code.

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `tokens.py` | Tokens | The input tokens of a greeting, a question, an order id, and the refund policy |
| 2 | `first_request.py` | Request and response | The content blocks, stop reason, and token usage of one request |
| 3 | `history.py` | Stateless API | The same question asked without and with the earlier messages |
| 4 | `max_tokens.py` | Output limit | A reply cut at 60 tokens and the same reply finished with a higher limit |
| 5 | `stream.py` | Streaming | The time each of the first pieces of a reply arrives |
| 6 | `caching.py` | Prompt caching | Three tickets with the policy written to the cache once and then read |
| 7 | `batches.py` | Message Batches | Last night's 60 tickets labeled in one batch |
| 8 | `raw_http.py` | Raw web request | The same request sent with no SDK |
| 9 | `first_request.ts` | TypeScript SDK | The same request in TypeScript |
| 10 | `get_order_tool.py` | Tool definition | The name, description, and input schema Claude receives |
| 11 | `tool_request.py` | Tool request | The `tool_use` block Claude returns when it needs a tool |
| 12 | `agent_sdk.py` | Agent SDK | An agent that searches the data folder on its own and answers |

## Part 1. Building with Claude

### 0. Environment

Sections: 0.1 Environment and Key.

Folder [`part1/00_environment`](part1/00_environment).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `inject_key.py` | API key injection | The key at each stage, from the `.env` file to the request header |

### 1. Foundations

Sections: 1.1 Models and Behavior.

Folder [`part1/01_foundations`](part1/01_foundations).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `effort.py` | Effort | The same ticket at low and high effort, with its blocks and output tokens |
| 2 | `test_replies.py` | Testing varied output | Three wordings of one reply, an exact text test and a property test |

### 2. Claude API

Sections: 2.1 Requests with Files.

Folder [`part1/02_claude_api`](part1/02_claude_api).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `read_slip.py` | An image in a request | The courier slip read from a picture and checked against the store record |
| 2 | `files_api.py` | The Files API | The invoice uploaded once, two questions by file id, then deleted |
| 3 | `stream_events.py` | Streaming events (extra practice) | Each server-sent event of one reply, in arrival order |
| 4 | `stream_tool.py` | A streamed tool call (extra practice) | The tool input as it arrives, and when it becomes valid JSON |

### 3. Prompts and Output

Sections: 3.1 Structured Output.

Folder [`part1/03_prompts_and_output`](part1/03_prompts_and_output).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `structured_ticket.py` | Structured outputs | Three tickets triaged as JSON that always parses |
| 2 | `label_prompts.py` | Output constraints and examples (extra practice) | The replies of each prompt on ten tickets, and how many are exact labels |

### 4. Tools

Sections: 4.1 Tools in Practice.

Folder [`part1/04_tools`](part1/04_tools).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `agent.py` | Tool-use loop | A two-issue complaint answered after customer, order, and policy lookups |
| 2 | `tool_errors.py` | Tool errors | Each tool call and result as a trace, then the answer |
| 3 | `tool_errors.py --generic` | Uninstructive errors | The same task when every error says only "failed" |

### 5. Context and Cost

Sections: 5.1 Context and Cost.

Folder [`part1/05_context_and_cost`](part1/05_context_and_cost).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `context_clearing.py` | Context editing | A 30-order review with old tool results cleared |
| 2 | `context_clearing.py --off` | Context editing off | The same review without clearing, for comparison |
| 3 | `cache_miss.py` | Cache invalidation | Cache tokens written and read before and after a tool description edit |

### 6. Agents

Sections: 6.1 Workflows and Agents in Practice.

Folder [`part1/06_agents`](part1/06_agents).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `routing.py` | Routing workflow | Three tickets labeled and answered by the specialist prompt for their label |


## Part 2. Shipping with Claude

### 7. Claude Code

Sections: 7.1 Project Context and Settings, 7.2 Permissions and Sessions.

This lesson is taught on the slides and has no programs.

### 8. Skills, Plugins, and MCP

Sections: 8.1 Skills and Plugins, 8.2 MCP Servers.

Folder [`part2/08_skills_plugins_and_mcp`](part2/08_skills_plugins_and_mcp).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `orders_client.py` | MCP client and server | The server's tool and resource, one order, and the policy size |
| 2 | `orders_server.py` | MCP server over stdio | A tool and a resource for Acme orders, started by the client |

### 9. Engineering and Lifecycle

Sections: 9.1 Requirements, 9.2 Lifecycle and Versioning, 9.3 Engineering Practice, 9.4 Application Design.

Folder [`part2/09_engineering_and_lifecycle`](part2/09_engineering_and_lifecycle).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `concurrency.py` | Bounded concurrency | 60 tickets labeled with at most 10 requests in flight, with the time taken |

### 10. Debugging and Evaluation

Sections: 10.1 Errors and Recovery, 10.2 Traces and Test Levels, 10.3 Evaluations.

Folder [`part2/10_debugging_and_evaluation`](part2/10_debugging_and_evaluation).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `errors.py` | Typed errors and retries | A rejected request and a successful one, each handled by its error class |
| 2 | `eval_replies.py` | A minimal eval | Six replies graded by code, with the average score |
| 3 | `judge.py` | A judge model | Two draft replies scored against the policy, with the reasoning |

### 11. Security and Safety

Sections: 11.1 Injection and Guardrails, 11.2 Hooks, 11.3 Keys and Secrets.

Folder [`part2/11_security_and_safety`](part2/11_security_and_safety).

| # | Program | Concept | Output |
|---|---|---|---|
| 1 | `injection.py` | Indirect prompt injection | The tools Claude asks for and its summary of a seller page |
| 2 | `try_hook.py` | Testing a hook | The hook's decision on three tool calls |
| 3 | `protect_files.py` | PreToolUse hook | Blocks edits to the key file, the store database, and the Git history |

### 12. Exam Method

Sections: 12.1 The Exam, 12.2 Decision Practice.

This lesson is taught on the slides and has no programs.

## Labs

Folder [`labs`](labs). Alongside the lessons you build Grant Desk, a claims assistant for a training fund, one
component per lab: reading scanned documents, structured output, tools, caching, agents, MCP, batches, evaluation, and
safety. Each lab has numbered steps, hints that open one at a time, and a check that tells you which step is done:

```
python labs/check.py 1
```


## Shared Folders

The running case is the support operation of Acme, an online electronics store. All lessons draw on these folders.

| # | Folder or file | Contents |
|---|---|---|
| 1 | `common/` | Modules that the lessons share: `store_tools.py` (the tools Claude may call) and `meter.py` (tokens and cost) |
| 2 | `data/store.db` | SQLite store with 150 customers, 500 orders over three months, payments, shipments, courier events, and earlier refunds |
| 3 | `data/refund_policy.md` | The returns, refunds, and delivery policy that the agents follow |
| 4 | `data/tickets.jsonl` | 60 customer messages, each labeled with the correct queue |
| 5 | `data/invoice_ord_20931.pdf` | The invoice of the blender order charged twice, built from the store records |
| 6 | `data/slip_ord_21044.png` | The courier's delivery exception notice for the parcel held at the hub |

To restore the original store data, run `python data/build_data.py`; to rebuild the invoice and the slip, run `python data/build_documents.py`.

## Cost

The programs use Claude Haiku 5.5, priced at USD 0.10 per million input tokens and USD 0.50 per million output tokens.
Most runs cost well under one US cent.
