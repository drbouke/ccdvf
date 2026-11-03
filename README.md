<p align="center">
  <img src="assets/ccdvf-logo.png" alt="Claude Certified Developer, Foundations logo" width="180">
</p>

<h1 align="center">Claude Certified Developer, Foundations</h1>

<p align="center">Exam code CCDV-F</p>

## The Certification

This certification validates that a developer can build, integrate, and ship production-grade applications, agents, and workflows on the Claude platform at a foundational level. It is intended for technical professionals who turn business requirements into working systems through API integration, agent and tool construction, prompt and context engineering, evaluation, security, and model selection.

| Exam | Details |
|---|---|
| Items | 53 multiple-choice and multiple-response |
| Time limit | 120 minutes |
| Passing score | 720 on a scale of 100 to 1,000 |

## The Domains

| Domain | Weight | What it covers | Where to learn it |
|---|---|---|---|
| [1. Agents and Workflows](#domain-1-agents-and-workflows) | 14.7% | Agent and workflow architecture, the Claude Agent SDK, hooks, design patterns, and frameworks | Platform lessons and [programs](domain1) |
| [2. Applications and Integration](#domain-2-applications-and-integration) | 33.1% | Requirements, the Claude API, software engineering practice, application design, and configuration | Platform lessons |
| [3. Claude Code](#domain-3-claude-code) | 3.1% | Core components, features, the CLAUDE.md hierarchy, and settings | Platform lessons |
| [4. Eval, Testing, and Debugging](#domain-4-eval-testing-and-debugging) | 2.6% | Error types, recovery strategies, and trace analysis | Platform lessons |
| [5. Model Selection and Optimization](#domain-5-model-selection-and-optimization) | 16.8% | LLM fundamentals, model tradeoffs, tokens, caching, and cost | Platform lessons |
| [6. Prompt and Context Engineering](#domain-6-prompt-and-context-engineering) | 11.0% | Context management, prompt design, and output validation | Platform lessons |
| [7. Security and Safety](#domain-7-security-and-safety) | 8.1% | Prompt injection defense, guardrails, hooks, and key management | Platform lessons |
| [8. Tools and MCPs](#domain-8-tools-and-mcps) | 10.6% | Tool implementation, MCP servers, and customization choices | Platform lessons |

Domain names and weights come from the CCDV-F Exam Guide, version 1.0, July 2026.

## Getting Started

Prepare the environment with [SETUP.md](SETUP.md), then run the setup check and the first agent.

```
python check_setup.py --ping
python run.py domain1/1.2_agent_construction/agent.py
```

Run every program from the main folder. Each lesson folder holds a `recorded_runs` folder with the real output of its programs, including tokens and cost.

## Domain 1. Agents and Workflows

### [Development Environment](domain1/1.0_environment)

Builds the course environment and follows the API key from a file to a request.

| Program | Concept | Output |
|---|---|---|
| `inject_key.py` | API key injection | The key at each stage, from the `.env` file to the request header |

### [1.1 Agent Architecture](domain1/1.1_agent_architecture) (4.5%)

Compares fixed workflows with agents and shows a supervisor directing subagents.

| Program | Concept | Output |
|---|---|---|
| `listing_chain.py` | Prompt chaining with a gate | Listings drafted from specifications, checked by code, then translated |
| `route_tickets.py` | Routing with parallel calls | 60 tickets sorted into five queues, with accuracy against the labels |
| `route_tickets.py --votes 3` | Parallelization by voting | The same routing with three votes per ticket |
| `translate_loop.py` | Evaluator-optimizer | A translator and a reviewer repeating until the glossary and facts are correct |
| `audit_subagents.py` | Supervisor and subagents | A lead agent auditing each duplicate charge through order-auditor subagents |

### [1.2 Agent Construction with Claude](domain1/1.2_agent_construction) (5.3%)

Builds an agent from one request to a complete loop, then adds tools and hooks.

| Program | Concept | Output |
|---|---|---|
| `first_call.py` | One request | A ticket triaged against the full policy, with stop reason and cost |
| `inspect_response.py` | Response object | Every field of one response as JSON |
| `round_trip.py` | Tool-use round trip | Each request and response in the loop, linked by tool use ID |
| `agent.py` | Tool-use loop | A two-issue complaint answered after customer, order, and policy lookups |
| `fix_tests.py` | Agent SDK on a code base | The agent finds and fixes the bug that the tests catch |
| `refund_agent.py` | Agent SDK, custom tools, hooks | Refund cases decided by an agent, with a hook enforcing approval limits |
| `hook_check.py` | Deterministic hooks | The same hook applied to store orders without a model |

### [1.3 Agent Patterns and Frameworks](domain1/1.3_agent_patterns) (4.9%)

Manages a long session with context editing and returns typed output through a framework.

| Program | Concept | Output |
|---|---|---|
| `context_clearing.py` | Context editing | A 30-order review with old tool results cleared |
| `context_clearing.py --off` | Context editing off | The same review without clearing, for comparison |
| `returns.py` | Pydantic AI, typed output | Return requests decided against the policy as validated objects |

## Domain 2. Applications and Integration

| Lesson | Weight | Focus |
|---|---|---|
| 2.1 Understanding Requirements | 3.4% | Functional and infrastructure requirements from business needs |
| 2.2 Systems Life Cycle | 2.8% | Developing, implementing, operating, and maintaining systems |
| 2.3 Claude API Mechanics | 6.8% | Messages, tools, streaming, vision, thinking, caching, and batch |
| 2.4 Software Engineering Foundations | 7.4% | REST, JSON, asynchronous code, version control, and refactoring |
| 2.5 Claude Application Design | 8.6% | Interfaces, content boundaries, schemas, sessions, and plugins |
| 2.6 Configuration Management | 4.1% | CLAUDE.md, settings.json, version pinning, and prompt versions |

## Domain 3. Claude Code

| Lesson | Weight | Focus |
|---|---|---|
| 3.1 Claude Code Operation | 3.1% | Rules, Skills, commands, agents, memory, sessions, and settings |

## Domain 4. Eval, Testing, and Debugging

| Lesson | Weight | Focus |
|---|---|---|
| 4.1 Debugging and Error Handling | 2.6% | Error types, recovery strategies, traces, and failure origin |

## Domain 5. Model Selection and Optimization

| Lesson | Weight | Focus |
|---|---|---|
| 5.1 LLM Fundamentals | 5.2% | Tokens, context windows, sampling, model options, and shot-based prompting |
| 5.2 Technical Fundamentals | 6.1% | Integrating with SDKs that wrap REST APIs, and websockets |
| 5.3 Model Selection and Tradeoffs | 2.7% | Opus, Sonnet, and Haiku, with quality, latency, and cost |
| 5.4 Cost and Token Management | 2.8% | Token budgets, usage tracking, cost models, and prompt caching |

## Domain 6. Prompt and Context Engineering

| Lesson | Weight | Focus |
|---|---|---|
| 6.1 Context Engineering | 3.8% | Context windows, drift and bloat, compaction, and isolation |
| 6.2 Prompt Engineering | 4.6% | Clear instructions, examples, placement, constraints, and refinement |
| 6.3 Output Handling | 2.6% | Structured output, response validation, and defensive parsing |

## Domain 7. Security and Safety

| Lesson | Weight | Focus |
|---|---|---|
| 7.1 AI Application Security | 3.2% | Prompt injection, jailbreaks, untrusted input, and data leakage |
| 7.2 Guardrails and Safe Deployment | 2.3% | Guardrail layers, secure design, and least privilege |
| 7.3 Claude Hooks | 1.0% | Hooks that prevent destructive actions |
| 7.4 Identity, Secrets, and Key Management | 1.6% | Credentials, API keys, authentication, and access monitoring |

## Domain 8. Tools and MCPs

| Lesson | Weight | Focus |
|---|---|---|
| 8.1 Tool Implementation | 4.4% | Function calling, tool descriptions, error handling, and approvals |
| 8.2 MCP Server Development | 2.1% | Server authoring, deployment, resources, tools, and transports |
| 8.3 Agentic Customization | 4.1% | Choosing among built-in tools, custom tools, Skills, and MCPs |

## Shared Folders

The running case is the support operation of Pintar, a Malaysian online electronics store. All lessons draw on these folders.

| Folder or file | Contents |
|---|---|
| `common/` | Modules that the lessons share, for cost measurement and store tools |
| `data/pintar.db` | SQLite store with 150 customers, 500 orders over three months, payments including 16 duplicate captures, shipments, 1,900 courier events, and earlier refunds |
| `data/refund_policy.md` | The returns, refunds, and delivery policy that agents follow |
| `data/tickets.jsonl` | 60 customer messages in English, Malay, and Malaysian English, each labeled with the correct queue |
| `data/product_specs.json` | Product facts for the listing programs |
| `data/glossary.json` | The English to Malay terms that Pintar requires |

The refund programs write to the store. To restore the original data, run `python data/build_data.py`.

## Cost

The programs use Claude Haiku 5.5, priced at USD 0.10 per million input tokens and USD 0.50 per million output tokens. Most runs cost well under one US cent, and routing 60 tickets costs less than one cent. `fix_tests.py` uses the default Claude Code model and costs about USD 0.20, with a limit of USD 2 set by `max_budget_usd`.
