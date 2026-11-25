# SICO AI agent release preparation — blocked on frontend build memory

**Not deployable yet. No deployment was executed.** The backend candidate is built
and validated. The full frontend build was OOM-killed, including the isolated
low-memory/unminified attempt. No frontend candidate image was produced, no release
seal was created, and the deployment script refuses execution in this state.

Release artifacts:
`C:\Users\sanad\AppData\Local\SICO_AI\agent-releases\agent-20261111-075055`

Reusable tools: `tools/sico_agent_release/`. The artifact directory contains a
frozen copy under `scripts/`, source/build contexts, manifests, actual validation
outputs, image archive, backup and restore-verification evidence. Backups and image
archives are outside OneDrive and were not added to Git.

## Actual images

| Component | Reference | Actual status |
| --- | --- | --- |
| Backend candidate | `sico-amro-backend:agent-20261111-075055` | Built and validated |
| Frontend candidate | `ghcr.io/sanaddiab6-del/grc_sc:sico-ai-next-agent-20261111-075055` | Planned reference only; image does not exist |
| Previous backend | `sico-amro-backend:rollback-agent-20261111-075055` | Exact preserved running image |
| Previous frontend | `sico-amro-frontend:rollback-agent-20261111-075055` | Exact preserved running image |

Backend candidate ID:
`sha256:c6465aa9b5c33768d7f2f5b4c7a3c6b8686ff3231c6072274b942845e0f5694a`

Previous backend ID:
`sha256:1a1fe422481d031287bfa9b57262e3fc4d944909ec70bef35f7e2dcae7b224fe`

Previous frontend ID:
`sha256:4292989b0bf487126317428b9ddef545d9c933c64eea2e4b6b1fd15e5ed5160a`

The existing services continue to use their previous images. No image was pushed.

## Source scope and configuration

The branch remains `feature/sico-ai-audit-risk-v1`, based on
`e1526292630998a09ee9f699b9455bca9d4eb1b4`. The running frontend's revision matches
that commit. Its source snapshot is that exact commit plus only the two modified
existing SICO route files:

- `frontend/src/routes/(app)/(internal)/sico-ai-next/+page.svelte`
- `frontend/src/routes/(app)/(internal)/sico-ai-next/+page.server.ts`

The running backend was behind several required local AI helper modules. A static
import closure, compared with the actual running image, identified 18 changed or
missing Python modules under `backend/ai_onboarding/`:

```text
capability_registry.py
capability_selection.py
engagement_approval_views.py
engagement_capability_views.py
engagement_plan.py
engagement_service.py
engagement_views.py
llm_config.py
llm_provider.py
sico_ai_agent.py
sico_ai_agent_tools.py
sico_ai_agent_views.py
sico_ai_router_views.py
sico_ai_tool_hub_views.py
sico_case_setup_adapter.py
sico_case_setup_proposal.py
sico_case_setup_views.py
urls.py
```

`source-manifest.json` records their raw/normalized hashes and why each module is
required; `backend-import-closure.json` records the complete dependency closure.
The actual image's files were verified against that manifest. Two release-only
files were also added to the image: `/code/sico-agent-start.sh` and
`/code/ciso_assistant/sico_agent_release_settings.py`.

Existing model and migration sources were checked against the deployed backend;
no schema delta is shipped. Source files in the working tree remain unchanged by
this preparation, apart from newly added release tooling and this report. Unrelated
uncommitted work was neither reset nor overwritten. No commit or push was made.

The original Compose order is preserved:

1. `docker-compose.amro-test.yml`
2. `%LOCALAPPDATA%\SICO_AI\ollama.override.yml`
3. `%LOCALAPPDATA%\SICO_AI\frontend-daec666.override.yml`
4. `%LOCALAPPDATA%\SICO_AI\coordinator-v2-safe.override.yml`
5. Versioned `release.override.yml` or `rollback.override.yml`, last.

Actual rendered Compose differences are restricted to backend/frontend image
references, backend safe entrypoint/empty command, and explicit settings/write-disable
environment entries. Existing mounts, networks, PostgreSQL, Caddy and other services
are preserved. The scripts use the literal project `grc_amro_test` and service
allowlist `backend frontend`, with `--no-deps --no-build --pull never`.

## Startup and AI write protection — verified

The candidate directly starts Gunicorn through `/code/sico-agent-start.sh`; both
the image and the final override select this launcher. It does not call the normal
`startup.sh`, `manage.py`, `migrate`, `storelibraries`, or `createsuperuser`.
It retains the existing Django secret and refuses a missing key rather than
generating a replacement.

The release settings wrapper forces Python values:

```python
SICO_ENGAGEMENT_COMMITS_ENABLED = False
SICO_AI_EXECUTION_STAGE_ALLOWLIST = ()
FORCE_CREATE_ADMIN = False
```

These values were verified even with environment strings attempting to enable them.
The registry remains four read-only tools. The real launcher started Gunicorn with
an unreachable database and no existing data mounts; an anonymous request to the
new agent endpoint returned **401**, proving the route exists and requires auth.

## Actual validation results

- **43 regression tests passed against code baked into the backend image.** Only
  test files were mounted; the implementation was imported from `/code` in the image.
- **13 ORM/security checks passed** using disposable in-memory fixtures.
- **Six frontend source/action checks passed**, and the existing page compiled
  without warnings in the focused compiler check. This is source validation, not
  validation of a completed frontend release image.
- The actual backend source files matched the captured dependency manifest.
- Actual Gunicorn startup and authentication denial passed in a network-none
  disposable container with no existing data mounts.
- PostgreSQL read-only enforcement passed in a new isolated PostgreSQL fixture:
  `transaction_read_only=on`; PostgreSQL itself rejected an UPDATE after bypassing
  the Python query wrapper; the fixture row remained unchanged.
- Deployment and rollback **default dry runs passed** against real Compose
  rendering and captured image/startup identities. Neither invoked Compose `up`.
- The incomplete release was correctly refused by `Seal-Release.ps1`.

Evidence is under `validation/`, including `backend-results.json`,
`backend-guards.json`, `backend-http.json`, `backend-source-manifest.json`,
`postgres-guard.json`, `frontend-source.json`, `preparation-checks.json`, and both
dry-run logs. `readiness.json` explicitly records `readyForDeployment=false`.

## Backup and restore verification — completed

Read-only backup of **amro-postgres**:

```text
backup\20261111-081244\sico-test.dump
20,237,436 bytes
SHA-256 c0b87e4417132a6008a5cd78790f5092bb0dc1a91d5d5e4225ea081c2a2ef065
```

The custom-format dump was restored successfully with
`pg_restore --exit-on-error --single-transaction` in a new network-none PostgreSQL
container using private PGDATA and **no Docker volumes**. Verified restored counts:
332 public tables, 10 users, 46 role assignments, 157 frameworks, 8 compliance
assessments, 18 assets and 3 evidence records. No restore targeted an existing DB.
Only read-only `pg_dump` was run against the original test database. The old
`grc_sc` and `sanadcom` databases were not used for backup or validation.

Exact previous images were saved to `previous-images.tar`:

```text
599,110,656 bytes
SHA-256 5e05fcb940cab13e4c0b4db20bc7266b133660604b9327f75d579918130377ee
```

Their immutable IDs, local rollback tags and archive checksums were verified.
The rollback override restores the captured safe entrypoint/commands, not the old
image's normal migration-running startup. Image rollback performs no database restore.

## External Docker restart

The guard detected simultaneous start-time changes in all existing containers,
with unchanged container and image IDs. The user explicitly confirmed Docker was
restarted externally. The original baseline was retained, that confirmation was
audited, and only start times were rebaselined after proving identities unchanged.
No restart/deployment command against existing services was issued by this work.
The accepted baseline still matches at the final preparation checks.

## Remaining blocker and next commands

**Frontend build capacity is the remaining blocker.** Builds hit container OOM
(exit 137, `OOMKilled=true`), including the low-memory production-copy attempt.
Other attempts hit V8's heap limit. Larger attempts were refused by the headroom
guard before starting. The last readiness snapshot showed about 3.7 GiB available
inside the Docker VM and 2.6 GiB free host RAM; an adequate native build was not safe
either. No Docker settings or existing service limits were changed to free memory.

A larger isolated build worker or safely available build memory is required.
Then complete `Build-Release.ps1`, run full `Validate-Release.ps1`, refresh/verify
the backup if necessary, stage the exact scripts, and seal the complete release.
Full frontend-image route-parity and HTTP checks remain unverified until that build
exists. Authenticated browser validation follows a separately approved deployment.

The reviewed scripts are in the artifact's `scripts/` directory:

```text
Prepare-Release.ps1
Refresh-BackendContext.ps1
Build-Release.ps1
Validate-Release.ps1
Validate-PostgresGuard.ps1
Backup-Verify.ps1
Preserve-Images.ps1
Stage-Scripts.ps1
Test-Preparation.ps1
Record-Readiness.ps1
Seal-Release.ps1
Deploy-Release.ps1
Rollback-Release.ps1
Record-ExternalRestart.ps1
```

Review-only deployment plan (tested, no service changes):

```powershell
$release = "$env:LOCALAPPDATA\SICO_AI\agent-releases\agent-20261111-075055"
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Deploy-Release.ps1" -ReleaseDirectory $release
```

**Not runnable successfully yet.** Only after the missing frontend image is built,
the full release is validated/sealed, a verified backup is no older than four hours,
and actual deployment is separately approved:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Deploy-Release.ps1" -ReleaseDirectory $release -Execute
```

The rollback counterpart is `Rollback-Release.ps1` with the same directory and,
only when authorized, `-Execute`. Its default dry run was verified. Neither execution
path has been invoked. No existing database, Docker volume, source record or Git
history was reset, deleted or migrated by the preparation scripts.
