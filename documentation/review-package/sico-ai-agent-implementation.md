# SICO AI Next agent implementation

Implemented in the existing repository and the existing SICO AI Next route. No new
page, database migration, application deployment, container restart, commit or push.
Existing unrelated uncommitted work was retained.

## Exact files changed by this task

Paths are relative to the repository root. This list excludes pre-existing dirty
files that this task did not edit.

1. `backend/ai_onboarding/sico_ai_agent.py` — new reusable execution loop.
2. `backend/ai_onboarding/sico_ai_agent_tools.py` — new reviewed read-tool registry.
3. `backend/ai_onboarding/sico_ai_agent_views.py` — new authenticated execution API.
4. `backend/ai_onboarding/test_sico_ai_agent.py` — new isolated engine/API checks.
5. `backend/ai_onboarding/llm_provider.py` — agent-specific structured schema and observation-aware prompt; earlier user changes retained.
6. `backend/ai_onboarding/urls.py` — appended execution route; existing local routes retained.
7. `backend/ai_onboarding/sico_ai_tool_hub_views.py` — extended existing, previously untracked catalog with authorized agent read tools; approval/commit implementation retained.
8. `frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts` — preserved planning, added execution and independent failure handling.
9. `frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte` — preserved existing UI and added visible execution results.
10. `tools/check_sico_ai_agent.py` — real ORM/security checks and optional unmocked Qwen API integration check against disposable fixtures.
11. `tools/check_sico_ai_frontend.cjs` — focused page compilation and server-action checks.
12. `documentation/review-package/sico-ai-agent-implementation.md` — this report.
13. `documentation/review-package/sico-ai-agent-real-qwen.json` — actual local-model test outcome/trace, explicitly labelled as fixture data.

## Execution and tool selection

`run_agent` in `sico_ai_agent.py` receives the instruction, a request-scoped
authorized registry and the existing local provider selection. It uses the existing
GRC capability-selection model configuration, including its fallback to the default
Qwen model. Each turn sends the task, authorized tool descriptions/argument schemas
and all bounded real observations to the model. A strict JSON union separates tool
decisions from final/blocked answers. The server validates the decision independently
of Ollama's schema enforcement. The chosen registry adapter validates its own exact
arguments and current permissions again before execution.

Every actual result or sanitized tool error returns to Qwen for its next decision.
The engine contains no keyword-based routing and no fixed sequence of stages.
Duplicate successful calls are refused, not re-executed; a stalled repetition moves
the next model turn to final/blocked synthesis. Final answers must cite
all successful observations; a final completion without verified results is refused.
The UI distinguishes model synthesis from stored record facts and from audit conclusions.
Citation validation does not mathematically prove every sentence of model prose;
the separately displayed authorized record results are the verified facts.

Bounds: six model decisions (the last reserved for a model-written final/blocked
account of verified results and unresolved work), 300 seconds overall, at most 90 seconds per provider
request (also capped by provider config and remaining budget), five-second database
read boundaries, 26,000 input-context characters, and 6,500 characters per tool
result. The provider independently refuses context overflow. A single schema-repair
turn may use sanitized constraint feedback; it consumes the same step/time budget
and never re-executes a tool or accepts an invalid response. Limits/failures return
partial verified observations and unresolved work; they never manufacture a final
answer. Cancellation callbacks and `InterruptedError` are handled. A WSGI browser
disconnect cannot reliably cancel an in-flight model call; its timeout still applies.
Database and final authorization cleanup may add bounded latency after the main deadline.

## Reviewed executable GRC capabilities

| Tool | Actual service/data source | Scope |
| --- | --- | --- |
| `frameworks.search` | Existing Framework ORM and shared RBAC helpers; reviewed bounded name/reference/URN adapter | Published shared library entries plus the selected exact folder |
| `compliance.list` | Existing ComplianceAssessment ORM and shared RBAC helpers | Selected exact folder and authorized framework ID |
| `compliance.requirements` | Existing engagement `_scoped_assessment` authorization, RequirementAssessment/RequirementNode ORM and shared RBAC helpers | Authorized assessment in the exact folder, plus authorized requirement references |
| `assets.list` | Existing workforce discovery `_scoped_category` service | Authorized asset records in the exact folder |

These services were executed against actual ORM records in a disposable test
database. They were not run against historical/customer records. The registry is
independent of the existing 11 engagement stages. New reviewed modules supply a
`ReadTool` definition, strict argument schema, permission model and fixed adapter;
the execution engine and its decision schema derive their tool vocabulary from
that registry. This is extensible coverage, not a claim that every platform function
has already been reviewed or connected.

## Authorization and data protection

DRF authenticates the API request. Before each tool and each model disclosure, the
registry reloads the active, unexpired user and refreshes the platform IAM snapshots.
Membership in this repository is represented by live direct/group RoleAssignments
covering folders. Exact-folder membership, module permission and object visibility
are checked independently of Qwen. A user-supplied organization hint can resolve only
one exact authorized name; model text cannot change tenant scope. Focus and explicit
folder conflicts are rejected. Without selected scope, only authorized published
framework-library lookup is available; company record tools are withheld.

Retained results are reauthorized before later prompts and final disclosure. Moved,
deleted or newly inaccessible records cause retained data/model quotations to be
withheld. Tools never accept caller/model-supplied URLs, SQL, import paths or function
names. PostgreSQL reads run in read-only transactions with statement/lock timeouts.
A SELECT-only execution guard also blocks accidental ORM writes, including SQLite
test writes. Missing IAM cache-version initialization fails closed instead of writing.

The agent cannot dispatch preparation, approval or commit tools, even if other
platform feature flags are enabled. Existing engagement fingerprints, review snapshots
and separate human-approval endpoints were preserved. No execution receipts or GRC
records are persisted by this loop.

## Existing page behavior

The existing authenticated server action requests the coordinator plan and agent
execution independently, so a failure in either does not discard the other result.
The existing layout, input, organization field, examples and planning display remain.
The new execution section shows each public model action description, selected
function, operation status, actual record names/IDs/stored status, next model
decision, citations, final synthesis, errors, unresolved work and write-approval
limitations. Record/model text is rendered as escaped Svelte text.

## Verification

- 43 focused no-database engine/router/tool-hub checks passed, covering chaining,
  actual observations fed into the next decision, unknown tools, premature answers,
  invalid citations, failures, duplicate calls, context/step/deadline limits,
  interruption, anonymous access and retained-data revocation.
- 13 real-ORM fixture checks passed, including two separate GRC modules,
  cross-tenant folders/objects, invalid IDs/extra arguments, inactive/unassigned users,
  live group-membership revocation, module-permission revocation, focus conflicts,
  retained moved records and write/arbitrary-dispatch denial.
- The existing Svelte page compiled without warnings. TypeScript transpilation and
  six focused server-action checks passed. Full-project `svelte-check` exceeded
  Node's default heap; full semantic type-checking and browser verification remain
  unverified.
- Real Qwen backend API execution was **verified with disposable ORM fixtures**.
  The saved final run used `qwen2.5:3b` for four model decisions: a real framework
  lookup, a compliance-assessment read using its returned ID, one duplicate call
  refused by the engine, and a final answer citing both successful observations.
  The returned assessment had stored status `in_progress`. Fixture record counts
  remained unchanged. Requirement inspection and asset reading also passed the
  real-ORM checks; they were not selected in this final saved model run.
  The complete outcome is recorded in `sico-ai-agent-real-qwen.json`.
  Its `real_qwen_verified` flag requires a completed unmocked local-model run,
  at least three decisions, real framework and compliance reads, a final answer and
  unchanged fixture record counts. Consult that flag and trace for the actual result.
  No live application database or historical records were used. PostgreSQL-specific
  read-only behavior and deployed browser behavior were not integration-tested.

The installed 3B model's recommendations remain advisory and can be brief. Earlier
real attempts repeated reads, exceeded their budgets or failed output validation;
those attempts returned partial results without a completion claim. The engine's
duplicate protection, final-turn reservation and bounded schema repair address
these observed failure modes. A single passing integration run is not a guarantee
that every future model request will complete successfully.

The integration harness overrides the database to `:memory:` before Django setup,
creates only a minimal disposable fixture schema, and runs no migrations. Unrelated
nullable FK targets are omitted and SQLite constraints are disabled in this fixture
harness; this is not a full PostgreSQL schema/constraint integration test. `--real-model`
invokes the actual DRF execution view with a test-authenticated principal and the
real configured provider, without mocking model decisions or GRC tool results.

## Reproduction in isolated containers

Use an existing backend image containing the repository's Python dependencies.
Override its startup entrypoint with `/code/.venv/bin/python`; never invoke the
application startup/migration script. Mount the repository read-only at `/workspace`,
set `PYTHONPATH=/workspace/backend`, `PYTHONDONTWRITEBYTECODE=1` and
`HUEY_FILE_PATH=/tmp/agent-huey.db`. Do not mount any existing data volumes.

No-database checks (container may use `--network none`):

```text
/workspace/backend/manage.py test ai_onboarding.test_sico_ai_agent ai_onboarding.test_sico_ai_router ai_onboarding.test_sico_ai_tool_hub --noinput
```

Real ORM checks (container may use `--network none`):

```text
/workspace/tools/check_sico_ai_agent.py
```

Local Qwen check (allow only the intended local Ollama connection):

```text
/workspace/tools/check_sico_ai_agent.py --real-model --report /report/sico-ai-agent-real-qwen.json
```

Set `LOCAL_AI_BASE_URL` to a permitted local/private IP running Ollama. `/report`
may mount only the intended review-output directory. The harness uses `qwen2.5:3b`
and refuses to claim verification if the complete read/answer chain fails.

Frontend checks: mount `frontend` read-only at `/source`, its installed `node_modules`
read-only at `/deps`, and `tools` read-only at `/checks`, then run Node 22:

```text
node /checks/check_sico_ai_frontend.cjs
```

## Before human-approved writes

Keep writes outside this agent until each proposed adapter has independently
validated serializers, exact scope/reference authorization, rollback-only preparation,
an immutable server-side payload fingerprint, separate human approval of that exact
snapshot, current permission rechecks, idempotency/concurrency protection and
PostgreSQL transaction/integration coverage. Register no commit capability merely
because the model asks for one. The existing approval components provide the
foundation; this change does not enable write integration or certify all platform tools.
