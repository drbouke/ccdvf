# Grant Claims Desk Labs

In these labs you build Grant Desk, the claims assistant of the Acme Skills Fund, one component at a time. The Fund
collects training contributions from employers and pays them back as grants when an employer claims for a course its
staff attended. Every claim arrives with a scanned attendance list and the training provider's invoice, and an officer
checks it against the [grant guide](data/grant_guide.md). Grant Desk does that first check.

Each lab adds the component that its lesson teaches, and each one starts from the finished code of the lab before it,
so you never fall behind.

## The Labs

| # | Lab | Lesson | What you build |
|---|---|---|---|
| 1 | [First Request](lab01_first_request) | 0. Environment | The project's first request, with its stop reason, tokens, and cost |
| 2 | [Read the Documents](lab02_read_documents) | 2. Claude API | A streamed request that reads a scanned attendance list and a PDF invoice |
| 3 | [Structured Claim](lab03_structured_claim) | 3. Prompts and Output | Every claim turned into JSON that follows one schema |
| 4 | Grant Tools | 4. Tools | Tools for employers, providers, and balances, with an agent loop |
| 5 | Guide in the Cache | 5. Context and Cost | The grant guide cached once and read on every claim |
| 6 | Duplicate Auditor | 6. Agents | A subagent that finds overlapping claims |
| 7 | Grants Server | 8. Skills, Plugins, and MCP | An MCP server for the grants system and a Skill for the eligibility rules |
| 8 | Nightly Review | 9. Engineering and Lifecycle | A day of claims assessed in one batch |
| 9 | Desk Evaluation | 10. Debugging and Evaluation | A set of decided claims that measures Grant Desk |
| 10 | Safe Approvals | 11. Security and Safety | A hook that stops large approvals and a defense against planted text |

## How to Work

1. Open the lab's folder and read its README. The steps are numbered, and each step names what it should produce.
2. Complete the `TODO` steps in the lab's program, in order. Every `TODO` sits where its code goes.
3. Run the program from the `ccdvf` folder, as the README shows, and read what it prints.
4. Check the lab. The check runs your program and tells you which step is done and what is still missing.

```
python labs/check.py 1
```

Each README ends with hints that open one at a time. Open the first hint only after you have tried the step, and the
next hint only if you still need it.

## The Data

| # | File | Contents |
|---|---|---|
| 1 | `data/grant_guide.md` | The rules every claim must meet: attendance, fee caps, deadlines, duplicates, and outcomes |
| 2 | `data/claims/CLM-NNNNN/attendance.jpg` | The scanned attendance list, with each trainee's initials for every day attended |
| 3 | `data/claims/CLM-NNNNN/invoice.pdf` | The provider's invoice for the course |

All the labs use Claude Haiku 5.5. A lab run costs well under one US cent.
