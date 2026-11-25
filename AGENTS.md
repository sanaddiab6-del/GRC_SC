# SICO AI Next - STANDING RULES (read fully before every task)

## North star
SICO AI Next takes exactly THREE inputs: organization, authorized framework
(exact edition), and a plain-language assessment objective. From them it
proposes a NEW, complete, interconnected GRC case across the 16 activities,
using existing SICO models, services, RBAC, tenant scope and approval gates.
Everything generated is a PROPOSED DRAFT until a human approves it.

## Architecture rule
- SICO code does deterministic work: framework lookup, requirement lists,
  review placeholders (not_assessed), IDs, links, statuses, progress,
  checkpoints, aggregations, exports, permissions.
- The local model (Ollama qwen2.5:3b) does only specialist analysis:
  organization-specific processes/assets, threat-risk-control-evidence
  bundles, requirement review reasoning, finding and remediation proposals.
- The model is called in bounded multi-record BATCHES. Each record is parsed,
  validated and linked separately. One bad record never discards good ones.
- Extend the EXISTING planner/coordinator. NEVER build a parallel generator.

## Scope discipline
- Touch ONLY the files named in the task. Need another file? STOP and say why.
- Do not patch a single activity in isolation. Do not add dependencies.
- Do not ask for a new test organization or an old checkpoint.
- Do not copy any content from OPEN_PREVIEW_OFFLINE.html (visual reference only).
- Do not replace model analysis with hardcoded security text.

## Honesty rules (most important)
- Tag EVERY claim in your report as one of:
  [RAN-REAL] command actually run, raw output pasted
  [RAN-MOCK] test used a mocked model; proves wiring only, NOT quality
  [NOT-RUN]  not executed
  [DESIGN-ONLY] described but not implemented
- Never write "works", "fixed" or "complete" without a [RAN-REAL] tag and
  pasted output.
- Never invent a file, function, class or route name. Every name you cite
  must appear in a grep/ls/git output from THIS session, otherwise write
  NOT FOUND.
- Planned tasks are not generated records. 16 mocked contracts are not 16
  working activities. A schema-valid record is not a good record.

## Safety (non-negotiable)
- Never: docker compose down -v, prune, volume deletion, migrations, DB
  writes, destructive git commands, container restarts, frontend production
  build, broad installs, secrets in output.
- Protect all existing users, tenants, cases, volumes and backups
  (grc_amro_test, grc_sc, sanadcom).
- Keep tenant isolation, active-membership checks, RBAC, deny-by-default.

## Time
- Target 10-15 minutes. At the limit: stop, commit a checkpoint, write the
  report. Never start a second work package.

## Before finishing
Re-read the task's DONE WHEN list. Confirm each item with evidence or mark it
FAILED. A failed item reported honestly is a success; a hidden one is not.

## Required report format
1. Task as understood (2 lines)
2. Files changed (paste git diff --stat)
3. Commands run with raw output (trimmed, not paraphrased)
4. Claims, each tagged [RAN-REAL]/[RAN-MOCK]/[NOT-RUN]/[DESIGN-ONLY]
5. DONE WHEN checklist, item by item: PASS/FAIL + evidence
6. Not done / blockers
7. Exactly ONE proposed next step
