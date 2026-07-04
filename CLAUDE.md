# Satryawiguna API — Claude Context

This project's AI-native workflow is defined in `.github/`.  
**Do not duplicate** — load context from the canonical source.

## Quick start

| What                                                         | Where                                        |
| ------------------------------------------------------------ | -------------------------------------------- |
| **Project context** (layers, routes, contracts, conventions) | `.github/copilot-instructions.md`            |
| **10 specialized agents**                                    | `.github/agents/*.agent.md`                  |
| **Agent directory** (one-page overview)                      | `AGENTS.md`                                  |
| **Shared business context**                                  | `satryawiguna/satryawiguna-shared` on GitHub |

## Workflow

1. Read `.github/copilot-instructions.md` first — it defines the layer hierarchy, route structure, response envelope, error handling, naming conventions, and CI/CD pipeline
2. For a new feature → follow the pipeline design: plan → implement → review → test → secure → deploy
3. Before planning → load shared context from `satryawiguna/satryawiguna-shared`:
   - `business/glossary.md` — domain term definitions
   - `business/business-rules.md` — domain invariants
   - `architecture/api-contracts.md` — endpoint contracts
   - `architecture/bounded-contexts.md` — bounded contexts

## Before any feature

1. Read `.github/copilot-instructions.md` to understand layers, routes, contracts, error handling, and conventions
2. Read the relevant agent in `.github/agents/*.agent.md` for scope and tools
3. Load shared business context from `satryawiguna/satryawiguna-shared` (see Quick start)

All conventions are defined **only** in `.github/copilot-instructions.md` — always load from there.

## Live API

- **Base URL**: `https://api.satryawiguna.me`
- **Swagger**: `/docs` (Basic Auth protected)
