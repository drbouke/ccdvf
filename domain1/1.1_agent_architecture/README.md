# 1.1 Agent Architecture

This lesson compares fixed workflows with agents and shows a supervisor directing subagents. Run each program from the `ccdvf` folder, for example `python run.py domain1/1.1_agent_architecture/listing_chain.py`.

| Program | Concept | Output |
|---|---|---|
| `listing_chain.py` | Prompt chaining with a gate | Listings drafted from specifications, checked by code, then translated |
| `route_tickets.py` | Routing with parallel calls | 60 tickets sorted into five queues, with accuracy against the labels |
| `route_tickets.py --votes 3` | Parallelization by voting | The same routing with three votes per ticket |
| `translate_loop.py` | Evaluator-optimizer | A translator and a reviewer repeating until the glossary and facts are correct |
| `audit_subagents.py` | Supervisor and subagents | A lead agent auditing each duplicate charge through order-auditor subagents |
