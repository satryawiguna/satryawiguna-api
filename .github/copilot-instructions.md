# Satryawiguna API — Project Instructions

Loaded automatically into every agent. Contains shared facts that do not need to be repeated in individual agent files.

---

## Project Identity

**Type**: FastAPI REST API — personal portfolio backend  
**Stack**: Python 3.12 · FastAPI · SQLAlchemy 2.0 (async) · MySQL 8 · Redis · DigitalOcean Spaces (S3)  
**Base URL**: `https://api.satryawiguna.me` · **Swagger**: `/docs` (Basic Auth protected)

---

## Layer Hierarchy

Strict top-to-bottom dependency — never skip or reverse:

```
app/api/v1/          → Route handlers (HTTP boundary)
app/schemas/         → Pydantic request/response models
app/services/        → Business logic
app/repositories/    → Data access (SQLAlchemy 2.0 async)
app/models/          → SQLAlchemy ORM models
app/core/            → Config, database, security, exceptions
app/utils/           → Shared utilities (pagination, response, email, media)
alembic/versions/    → Database migration files
tests/               → pytest async integration tests (in-memory SQLite)
```

**Implementation order for any new resource**:  
Schema → Model → Migration → Repository → Service → API route → Register in `app/api/v1/__init__.py`

---

## Route Structure

| Prefix                     | Auth                                     | Purpose          |
| -------------------------- | ---------------------------------------- | ---------------- |
| `/api/v1/admin/{resource}` | JWT Bearer (`Depends(get_current_user)`) | Admin CRUD       |
| `/api/v1/{resource}`       | None                                     | Public read-only |
| `/api/v1/auth/*`           | None / JWT                               | Authentication   |
| `/api/v1/media/*`          | JWT Bearer                               | File uploads     |

All routers registered in `app/api/v1/__init__.py`.

---

## Response Envelope Contract

Every route must return via `APIResponse` from `app.utils.response`:

```python
# Success
return APIResponse.success(message="X retrieved successfully", data=XResponse.model_validate(obj).model_dump())

# Success with pagination
return APIResponse.success(message="...", data=[...], pagination=create_pagination_meta(...))

# Not-found (HTTP 200 envelope — do NOT raise HTTP 404)
return APIResponse.error(message="X not found", status=404)
```

**Never** return a raw dict, ORM object, or Pydantic model directly from a route.

---

## Error Handling Contract

```
Services   → raise AppError subclasses only (NotFoundError, DuplicateError,
             BusinessLogicError, AuthenticationError, AuthorizationError)
API routes → catch nothing; global handler in main.py translates AppError → HTTP response
           → OR call APIResponse.error() directly for route-level guards
NEVER      → raise HTTPException inside a service
```

---

## Code Conventions

### Naming

| Layer      | Class                                      | File                               | Method                                            |
| ---------- | ------------------------------------------ | ---------------------------------- | ------------------------------------------------- |
| Schema     | `XBase`, `XCreate`, `XUpdate`, `XResponse` | `app/schemas/x.py`                 | —                                                 |
| Model      | `X`                                        | `app/models/x.py`                  | —                                                 |
| Repository | `XRepository(BaseRepository[X])`           | `app/repositories/x_repository.py` | `get_x_by_id`, `get_paginated`                    |
| Service    | `XService`                                 | `app/services/x_service.py`        | `get_x_by_id`, `create_x`, `update_x`, `delete_x` |
| Route      | `router = APIRouter()`                     | `app/api/v1/x.py`                  | —                                                 |

### Style

- File docstring `"""..."""` at top of every `.py` file
- Import order: stdlib → third-party → internal (`app.*`)
- Enum values: `UPPER_SNAKE_CASE`
- `XResponse` always has `class Config: from_attributes = True`
- `Optional` user inputs validated with `Field(min_length=..., max_length=...)`

---

## Git Workflow

| Branch type       | Pattern                             | CI trigger                      |
| ----------------- | ----------------------------------- | ------------------------------- |
| Feature           | `feature/short-description`         | CI (lint + test) on push        |
| Bug fix           | `bugfix/short-description`          | CI (lint + test) on push        |
| Release candidate | `rc/vX.Y.Z`                         | CI + Build + Deploy-dev on push |
| Production        | merge from `rc/*` → manual dispatch | Deploy-prod                     |

**Commit messages follow Conventional Commits** (scoped format):

```
feat(api): add endorsement endpoint to experiences
fix(api): resolve not-found response returning HTTP 404 instead of 200 envelope
chore(db): add ix_experience_skills_experience_id index migration
refactor(core): extract pagination logic into base repository
test(service): add unit tests for experience service
docs(db): sync schema.dbml with endorsements table
```

---

## CI/CD Pipeline

```
feature/** / bugfix/**  →  ci.yml      (lint: ruff, test: pytest)
rc/**                   →  ci.yml      (lint + test gate)
                        →  build.yml   (Docker build + push :dev to Docker Hub)
                        →  deploy-dev.yml  (auto-deploy :dev to dev server :8001)
workflow_dispatch       →  deploy-prod.yml (promote :dev → :latest → prod :8002)
```

Required GitHub Secrets: `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN`, `PROD_SSH_HOST`, `PROD_SSH_USER`, `PROD_SSH_KEY`, `PROD_SSH_APP_DIR`, `DEV_SSH_HOST`, `DEV_SSH_USER`, `DEV_SSH_KEY`, `DEV_SSH_APP_DIR`

---

## Test Conventions

- `asyncio_mode = auto` in `pytest.ini` — no `@pytest.mark.asyncio` needed
- Shared fixtures in `tests/conftest.py`: `db`, `client`, `test_user`, `auth_headers`
- Local model fixtures: `db.add()` + `await db.commit()` + `await db.refresh()`
- In-memory SQLite only — no production DB in tests
- Class per endpoint group: `TestGetX`, `TestCreateX`, `TestUpdateX`, `TestDeleteX`

---

## Agent Pipeline

```
@orchestrator → Full pipeline coordinator (delegates + gates on verdicts)
@architect    → "Should we?" — ADR + system-level decisions   (before @planner for major changes)
@planner      → Task table (feature decomposition)
@implementer  → Code (one task at a time, gated by verification)
@reviewer     → Code quality gate (APPROVED / NEEDS REVISION)
@tester       → Test file generation + pytest run
@documentation → DBML sync, Swagger annotations, README, docstrings
@security     → OWASP audit (pre-deploy gate)
@performance  → Latency audit (pre-deploy gate)
@devops       → Docker build, migrate, deploy
```

Each agent's scope is strictly bounded — agents do not duplicate each other's work.

---

## Shared Context

Product vision, business rules, glossary, and API contracts shared across all
sibling projects live in a dedicated GitHub repo. **Do not duplicate this content
in local files** — load it from the source via MCP when needed.

| Source      | URL                                                                       |
| ----------- | ------------------------------------------------------------------------- |
| Shared repo | `https://github.com/satryawiguna/satryawiguna-shared`                     |
| Raw base    | `https://raw.githubusercontent.com/satryawiguna/satryawiguna-shared/main` |

### Shared Context Files (by agent need)

| File                               | Purpose                                                 | Needed by                           |
| ---------------------------------- | ------------------------------------------------------- | ----------------------------------- |
| `business/glossary.md`             | Domain term definitions (User, Experience, Skill, etc.) | All agents                          |
| `business/business-rules.md`       | Domain invariants and constraints (BA-1 through BCF-26) | @architect, @planner, @reviewer     |
| `architecture/bounded-contexts.md` | 6 bounded contexts with entity ownership                | @architect                          |
| `architecture/api-contracts.md`    | Endpoint contracts consumed by frontend                 | @planner, @reviewer, @documentation |
| `product/vision.md`                | Product vision, audience, 5 key principles              | @architect                          |

### How to Load Shared Context via MCP GitHub

Use the GitHub MCP server to read files directly from the shared repo (no clone needed):

```
# Load glossary (most frequently needed)
→ Use MCP GitHub to read `business/glossary.md` from satryawiguna/satryawiguna-shared

# Load business rules before planning
→ Use MCP GitHub to read `business/business-rules.md` from satryawiguna/satryawiguna-shared

# Load API contracts when reviewing endpoint changes
→ Use MCP GitHub to read `architecture/api-contracts.md` from satryawiguna/satryawiguna-shared
```

**When to load**:
| Agent | Files to load | When |
|-------|--------------|------|
| @architect | `bounded-contexts.md` + `business-rules.md` | Before every architectural assessment |
| @planner | `business-rules.md` + `glossary.md` | Before decomposing any feature |
| @reviewer | `business-rules.md` | When plan fidelity involves domain rules |
| @implementer | (none) | Only if the task explicitly references a business rule |

---

## MCP Servers (Model Context Protocol)

MCP servers extend Copilot's capabilities with external tool access. Configured in `.vscode/mcp.json`.

| Server                  | Purpose                                                  | Active by default |
| ----------------------- | -------------------------------------------------------- | ----------------- |
| **MySQL**               | Query dev database directly from chat                    | ✅                |
| **GitHub**              | Create PRs, dispatch workflows, **read any public repo** | ✅                |
| **Filesystem**          | Full file read/write (project-scoped)                    | ✅                |
| **Sequential Thinking** | Structured reasoning for complex decisions               | ✅                |

**MCP usage rules**:

- MCP MySQL is for **read-only queries** on the dev database — never modify data via MCP
- MCP GitHub can read files from any public repo, create PRs, and dispatch workflows — but deploying to production still requires manual confirmation
- MCP Filesystem is scoped to this project directory only — cannot access files outside it
- If an MCP server is unavailable, fall back to standard tools (grep, terminal, docker exec, curl to raw GitHub URLs)

---

## Adapter Sync

This file is the **single source of truth** for project context. Adapter files in
`CLAUDE.md`, `.cursor/rules/`, and `.windsurf/rules/` are **pure routers** — they
contain zero duplicated content and only point here.

**When updating this file**: verify that adapter files remain thin routers. If an
adapter contains duplicated conventions, remove the duplication and ensure it
only references this file.
