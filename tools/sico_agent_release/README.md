# SICO AI agent release tools

These tools prepare a release for the existing `grc_amro_test` Compose project and
the existing `/sico-ai-next` page. They do not create another site. Application
deployment and rollback are dry runs unless explicitly called with `-Execute`
after separate deployment approval. Preparation never calls Compose `up`.

Run Windows PowerShell with process-only execution-policy bypass; no machine policy
change is needed. Versioned artifacts default to
`%LOCALAPPDATA%\SICO_AI\agent-releases\agent-YYYYMMDD-HHMMSS`, outside OneDrive.
Database backups and image archives must remain private and must not be committed.

## Preparation and builds

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Prepare-Release.ps1
$release = 'C:\Users\sanad\AppData\Local\SICO_AI\agent-releases\<version>'
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Build-Release.ps1 -ReleaseDirectory $release
```

Preparation records exact running image/container identities, Compose-file order
and hashes, source hashes, schema-source parity, Git HEAD, and rollback tags. It
requires the deployed frontend revision to match HEAD, snapshots that commit, and
overlays only the two existing SICO page files. Backend source is resolved through
its static import closure and compared with the actual deployed image; only changed
or missing required AI-package modules are copied. Existing models and migrations
cannot be overlaid. Unrelated working-tree files are not checked out, reset or
copied into the release.

The Node dependency volume is mounted read-only, and its pnpm lock must match the
snapshot lock. Builds use a fresh disposable container with no network, data mounts
or published ports. Compiler caches are copied into the build snapshot only.
Production-only declaration emission is disabled in the disposable Vite config;
this skips `.d.ts` generation, not runtime translations or application features.

Build memory is bounded. A preflight checks actual Docker-VM available memory and
requires a further 512 MiB reserve. If a build fails, explicit resume is supported:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Build-Release.ps1 `
  -ReleaseDirectory $release -Resume -MemoryMiB 4000 -NodeHeapMiB 3000
```

Do not stop existing services or change Docker settings to make a build fit without
separate authorization. Failed builds leave the release unvalidated and undeployable.
For a constrained test-build host, `-LowMemoryFrontend` additionally disables JS
minification and compressed-size reporting only in the disposable build copy.
Application source/features are unchanged, but assets are larger. This tradeoff is
recorded in the build-dependency manifest and the image's
`sico.agent.frontend.minified` label and must be reviewed before deployment.

## Startup and write protection

The new backend image and final Compose override both select
`/code/sico-agent-start.sh` with an empty command. It reads the existing Django
secret (or existing environment value), refuses a missing key, and directly execs
Gunicorn. It does not invoke `startup.sh`, `manage.py`, `migrate`, `storelibraries`,
or `createsuperuser`. A release settings wrapper inherits the existing settings and
forces `SICO_ENGAGEMENT_COMMITS_ENABLED=False`, an empty stage allowlist, and
`FORCE_CREATE_ADMIN=False`, independently of environment-string values.

The agent registry still contains only four reviewed read adapters. This does not
enable commits, preparation dispatch or model-controlled permissions.

## Validation

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Validate-Release.ps1 -ReleaseDirectory $release -BackendOnly
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Validate-Release.ps1 -ReleaseDirectory $release
```

Backend tests import the implementation baked into the candidate image; only test
files/harnesses are mounted. Full validation runs 43 regressions, 13 in-memory ORM
security checks, six frontend action checks, compiled frontend route-set parity,
and actual backend/frontend HTTP startup probes. The backend smoke test uses the
real launcher with an unreachable database and no existing data mounts. PostgreSQL
read-only enforcement is additionally tested in a new, isolated fixture cluster;
PostgreSQL itself must reject an UPDATE even when the Python query guard is bypassed.
No existing database is used for these application tests.

## Database backup and restore verification

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Backup-Verify.ps1 -ReleaseDirectory $release
```

This performs only a read-only `pg_dump` against **amro-postgres**, after confirming
its project/service identity. Binary output is streamed without PowerShell text
conversion. Each dump has a new destination and a SHA-256 hash. The dump uses custom
format and excludes PostgreSQL ownership/ACL commands; business users, RBAC records,
evidence metadata and all other database tables remain included. Keep the existing
database role configuration when planning disaster recovery.

Restore is tested only inside a newly created, network-none PostgreSQL container,
using container-private PGDATA and no Docker volumes. `pg_restore` must complete
with `--exit-on-error --single-transaction`; structural and critical-table counts
are checked there. Cleanup verifies scratch ownership and never uses volume deletion.
The script cannot restore over an existing database. Image rollback does not restore
the database, because this release performs no migrations. Any disaster-recovery
cutover to a restored database requires a separate reviewed procedure and approval.

## Preserve images, stage and seal

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Preserve-Images.ps1 -ReleaseDirectory $release
powershell -NoProfile -ExecutionPolicy Bypass -File tools/sico_agent_release/Stage-Scripts.ps1 -ReleaseDirectory $release
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Seal-Release.ps1" -ReleaseDirectory $release
```

The previous images receive versioned rollback tags and are saved into a checked,
hashed local archive. Restore missing local image tags with
`docker image load --input "$release\previous-images.tar"`; this is an image-store
operation, not a service deployment or a database restore.

Sealing requires both validated release images, a verified database backup, intact
rollback archives, allowed Compose changes, and an unchanged protected-container
baseline. It hashes the exact scripts, state, overrides and evidence. A seal is not
deployment approval. A backup older than four hours blocks actual deployment;
create/verify a fresh dump and reseal before proceeding.

## Review-only deployment and rollback plans

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Deploy-Release.ps1" -ReleaseDirectory $release
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Rollback-Release.ps1" -ReleaseDirectory $release
```

The commands render the real Compose configuration and validate target identities.
The only application-changing command in either execution path is:

```text
docker compose --project-name grc_amro_test ... up -d --no-deps --no-build --pull never --force-recreate backend frontend
```

No `down`, volume deletion, broad stack restart, PostgreSQL or Caddy recreation is
used. Rollback reproduces the exact previous images, entrypoints and commands.

Only after the complete release passes validation, is sealed, and deployment is
separately approved:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Deploy-Release.ps1" -ReleaseDirectory $release -Execute
```

After separately authorized rollback:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File "$release\scripts\Rollback-Release.ps1" -ReleaseDirectory $release -Execute
```

## External Docker restarts

The guard refuses any unexpected container ID, image ID or start-time drift. Do not
silently replace that baseline. If the user explicitly confirms an external Docker
restart, `Record-ExternalRestart.ps1 -ExternalRestartConfirmed` can refresh only the
start-time baseline after proving every container/image identity is unchanged.
The original state and confirmation audit are retained. Image/configuration changes
require a new reviewed preparation rather than this restart-only mechanism.
