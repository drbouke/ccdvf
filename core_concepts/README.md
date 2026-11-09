# Core Concepts

These programs show the terms of the Core Concepts lesson in running code: tokens, a request and its response, cost, the stateless conversation, the output limit, streaming, the kinds of SDK, a tool request, and the Agent SDK. Run each Python program from the `ccdvf` folder, for example `python run.py core_concepts/tokens.py`. Every program has its real output in `recorded_runs`.

| Program | Concept | Output |
|---|---|---|
| `tokens.py` | Tokens | The input tokens of a greeting, a question, an order id, and the refund policy |
| `first_request.py` | Request and response | The content blocks, stop reason, and token usage of one request |
| `history.py` | Stateless API | The same question asked without and with the earlier messages |
| `max_tokens.py` | Output limit | A reply cut at 60 tokens and the same reply finished with a higher limit |
| `stream.py` | Streaming | The time each of the first pieces of a reply arrives |
| `raw_http.py` | Raw web request | The same request sent with no SDK, using only the Python standard library |
| `first_request.ts` | TypeScript SDK | The same request in TypeScript |
| `get_order_tool.py` | Tool definition | The name, description, and input schema Claude receives |
| `tool_request.py` | Tool request | The `tool_use` block Claude returns when it needs a tool |
| `agent_sdk.py` | Agent SDK | An agent that searches the data folder on its own and answers |

To run the TypeScript program, install Node.js 22 or later, then run these commands in the `core_concepts` folder.

```
npm install
node --env-file=../.env first_request.ts
```
