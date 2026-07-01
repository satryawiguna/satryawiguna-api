# AI Agent Registry

This project defines 10 specialized agents in `.github/agents/*.agent.md`.  
Each agent has a strict scope boundary and tool assignment.

## Pipeline order

```
orchestrator → architect → planner → implementer → reviewer → tester → documentation → security → performance → devops
```

## Agent table

| Agent              | Role                                                                                                             | Tools                       | Read-only? |
| ------------------ | ---------------------------------------------------------------------------------------------------------------- | --------------------------- | ---------- |
| **@orchestrator**  | Pipeline coordinator — classifies change type, delegates to agents, gates on verdicts                            | read, search                | ✅         |
| **@architect**     | Architecture decisions — ADRs, principles (P1–P7), domain modeling, API design, database design                  | read, search, edit          | —          |
| **@planner**       | Feature decomposition — context engineering, risk taxonomy (5 types), task table                                 | read, search                | ✅         |
| **@implementer**   | Code execution — implements plan one task at a time, import gate, git commit                                     | read, search, edit, execute | —          |
| **@reviewer**      | Code quality gate — plan fidelity, conventions, error contract, response format (BLOCKER / WARNING / SUGGESTION) | read, search                | ✅         |
| **@tester**        | Test generation — integration tests (HTTP) + unit tests (mocked repos), debug diagnosis (7-step table)           | read, search, edit, execute | —          |
| **@documentation** | Documentation — Swagger annotations, DBML schema, README, docstrings, release notes, ADR index                   | read, search, edit          | —          |
| **@security**      | Security audit — OWASP Top 10 (2021), STRIDE threat model, secure coding patterns                                | read, search, execute       | ✅         |
| **@performance**   | Performance audit — database indexes, N+1 queries, caching, connection pool, load analysis                       | read, search, execute       | ✅         |
| **@devops**        | DevOps — Docker, migrations, deploy, CI/CD, monitoring, MCP integration                                          | read, search, execute       | —          |

## Key contracts

All project contracts (response envelope, error handling, not-found behavior, auth) are defined in `.github/copilot-instructions.md`. Always load from there — never duplicate.

## Shared context

Cross-cutting knowledge lives in `satryawiguna/satryawiguna-shared` on GitHub:

| File                               | Contents                                |
| ---------------------------------- | --------------------------------------- |
| `business/glossary.md`             | Domain term definitions                 |
| `business/business-rules.md`       | Domain invariants (BA-1 through BCF-26) |
| `architecture/bounded-contexts.md` | 6 bounded contexts                      |
| `architecture/api-contracts.md`    | Endpoint contracts                      |
| `product/vision.md`                | Product vision and principles           |

## MCP servers (`.vscode/mcp.json`)

| Server              | Purpose                              |
| ------------------- | ------------------------------------ |
| MySQL               | Query dev database directly          |
| GitHub              | Read repos, manage PRs and workflows |
| Filesystem          | File operations (project-scoped)     |
| Sequential Thinking | Structured reasoning                 |
