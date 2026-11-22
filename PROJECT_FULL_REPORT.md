# PROJECT_FULL_REPORT

Generated on 2026-07-05T14:17:02

## Project Overview
Sanadcom GRC Platform is a large full-stack governance, risk, and compliance system built around a Django REST backend, a SvelteKit frontend, a Python CLI/MCP layer, and an enterprise overlay.
The community core provides folder-scoped tenancy, RBAC, assessments, evidence management, library loading, notifications, integrations, webhooks, metrics, import/export, and reporting workflows.
The enterprise layer adds branded client settings and extra routes while reusing the same conceptual model and deployment pattern.

## Technology Stack
- Python 3.14, Django 6, Django REST Framework, allauth, Knox, SimpleJWT, Huey, PostgreSQL/SQLite, WeasyPrint, django-storages, boto3, structlog.
- SvelteKit 2, Svelte 5, TypeScript, Tailwind CSS v4, Skeleton UI, Paraglide-JS, Vitest, Playwright, Zod, SvelteKit Superforms.
- Docker, Docker Compose, Caddy, Helm charts, and optional S3-compatible storage.
- CLI tooling built on Python, Requests/httpx, Rich, YAML/CSV, and MCP support.

## Architecture Summary
- Django owns the business engine, persistence, auth, and background processing.
- SvelteKit owns the user experience and server-side route orchestration.
- The CLI and automation code reuse the same API surface for bulk operations and integrations.
- The enterprise overlay customizes the shared platform rather than replacing it.

## Execution Flow
- `manage.py` and `startup.sh` launch the backend.
- Settings are loaded from `backend/ciso_assistant/settings.py` or the enterprise overlay.
- Django wires routers, middleware, auth, and background jobs.
- Caddy routes browser traffic to the frontend and API traffic to Django.
- Huey runs periodic background tasks.
- ORM models and serializers move data to and from the database and file storage.

## Authentication and Authorization
- Knox tokens support interactive sessions.
- SimpleJWT supports stateless API access.
- django-allauth provides SSO, MFA, and headless auth flows.
- Folder-scoped RBAC decides object access and write permissions.
- The frontend injects CSRF, locale, token, and allauth session headers when proxying API calls.

## Database and Data Flow
- PostgreSQL is the primary production database; SQLite is the development/test fallback.
- Django migrations define and evolve schema across many domain apps.
- Attachments are stored locally by default or in S3-compatible storage when enabled.
- Requests typically flow from validation to ORM operations to background jobs to JSON or file responses.

## Background Processing
- Huey periodic tasks check expirations and send notifications.
- Management commands backfill, populate, and maintain domain data.
- Integration helpers sync external systems such as Jira and webhooks.

## Frontend
- Route groups split authenticated app pages, auth flows, third-party pages, and internal tool pages.
- The root layout renders sidebar navigation, breadcrumbs, command palette, notifications, and modal infrastructure.
- Utility modules centralize CRUD metadata, i18n, access control, and shared stores.

## Configuration
- Backend config lives in Python settings, Docker manifests, and Poetry metadata.
- Frontend config lives in package.json, Vite/Svelte configs, and Paraglide project files.
- CLI config lives in its own pyproject, requirements file, and MCP-specific support files.
- Deployment config lives in Docker Compose, Caddy, Helm, and certificate templates.

## Security
- The project enforces secure cookies, CSRF, HSTS, and X-Frame-Options in backend settings.
- The report does not fix vulnerabilities; it documents likely risks such as broad permission surfaces and many upload/export endpoints.
- Some settings and token flows are explicitly designed to block insecure SSO/local-auth mixes.

## Folder Analysis
### .git
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/hooks
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/info
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/logs
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/logs/refs/heads
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/logs/refs/remotes/origin
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/objects/pack
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/refs/heads
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .git/refs/remotes/origin
- Purpose: Supporting project file.
- Relationship: belongs to the .git area of the repository and is used by files underneath it.
- Important contents: 33 files exist in the same top-level area; see the file inventory for exact members.

### .github
- Purpose: Supporting project file.
- Relationship: belongs to the .github area of the repository and is used by files underneath it.
- Important contents: 1 files exist in the same top-level area; see the file inventory for exact members.

### automation
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/credentials
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/icons
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes/CisoAssistantService
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes/handlers
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes/registry
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes/types
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/n8n/n8n-nodes-ca/nodes/utils
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### automation/prowler_helpers
- Purpose: Automation and workflow helpers.
- Relationship: belongs to the automation area of the repository and is used by files underneath it.
- Important contents: 53 files exist in the same top-level area; see the file inventory for exact members.

### backend
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/app_tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/app_tests/api
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/cal
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/cal/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/cal/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/ciso_assistant
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/ciso_assistant/scripts
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/locale/fr/LC_MESSAGES
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/mappings
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/core
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/emails/en
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/emails/fr
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/registration
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/snippets
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templates/tprm
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/templatetags
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/core/tests/sandbox
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/crq
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/crq/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/data_wizard
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/data_wizard/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/ebios_rm
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/ebios_rm/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/ebios_rm/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/global_settings
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/global_settings/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam/sso
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam/sso/oidc
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam/sso/saml
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/iam/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/itsm
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/itsm/jira
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/itsm/servicenow
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/management
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/integrations/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/library
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/library/libraries
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/library/management
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/library/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/library/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/locale/en/LC_MESSAGES
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/locale/fr/LC_MESSAGES
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/logs
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/metrology
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/metrology/management
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/metrology/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/metrology/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/notifications
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/notifications/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/pmbok
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/pmbok/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/privacy
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/privacy/management
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/privacy/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/privacy/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/resilience
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/resilience/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/scripts
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/serdes
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/serdes/tests
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/tprm
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/tprm/management
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/tprm/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/tprm/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/tprm/test
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/webhooks
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/webhooks/management/commands
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### backend/webhooks/migrations
- Purpose: Django backend and server-side platform code.
- Relationship: belongs to the backend area of the repository and is used by files underneath it.
- Important contents: 896 files exist in the same top-level area; see the file inventory for exact members.

### caddy_data/caddy
- Purpose: Supporting project file.
- Relationship: belongs to the caddy_data area of the repository and is used by files underneath it.
- Important contents: 9 files exist in the same top-level area; see the file inventory for exact members.

### caddy_data/caddy/certificates/local/localhost
- Purpose: Supporting project file.
- Relationship: belongs to the caddy_data area of the repository and is used by files underneath it.
- Important contents: 9 files exist in the same top-level area; see the file inventory for exact members.

### caddy_data/caddy/pki/authorities/local
- Purpose: Supporting project file.
- Relationship: belongs to the caddy_data area of the repository and is used by files underneath it.
- Important contents: 9 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant-next
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant-next/templates
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant-next/templates/backend
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant-next/templates/frontend
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant-next/templates/ingress
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### charts/ciso-assistant/templates
- Purpose: Helm/Kubernetes chart packaging.
- Relationship: belongs to the charts area of the repository and is used by files underneath it.
- Important contents: 30 files exist in the same top-level area; see the file inventory for exact members.

### cli
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### cli/ca_mcp
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### cli/ca_mcp/tools
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### cli/ca_mcp/utils
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### cli/ciso_assistant_cli.egg-info
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### cli/tests
- Purpose: CLI and MCP tooling.
- Relationship: belongs to the cli area of the repository and is used by files underneath it.
- Important contents: 42 files exist in the same top-level area; see the file inventory for exact members.

### config
- Purpose: Configuration and certificates.
- Relationship: belongs to the config area of the repository and is used by files underneath it.
- Important contents: 17 files exist in the same top-level area; see the file inventory for exact members.

### config/extra
- Purpose: Configuration and certificates.
- Relationship: belongs to the config area of the repository and is used by files underneath it.
- Important contents: 17 files exist in the same top-level area; see the file inventory for exact members.

### config/templates
- Purpose: Configuration and certificates.
- Relationship: belongs to the config area of the repository and is used by files underneath it.
- Important contents: 17 files exist in the same top-level area; see the file inventory for exact members.

### db
- Purpose: Supporting project file.
- Relationship: belongs to the db area of the repository and is used by files underneath it.
- Important contents: 4 files exist in the same top-level area; see the file inventory for exact members.

### db-backup-sqlite-20260312-103213
- Purpose: Supporting project file.
- Relationship: belongs to the db-backup-sqlite-20260312-103213 area of the repository and is used by files underneath it.
- Important contents: 5 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/data/schemas/commands/applied_control
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/data/schemas/commands/evidence
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/data/schemas/commands/requirement_assessment
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/samples/kafka
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/samples/kafka/redpanda
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/samples/messages
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/tests
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/tests/integration
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### dispatcher/utils
- Purpose: Dispatcher/event processing helpers.
- Relationship: belongs to the dispatcher area of the repository and is used by files underneath it.
- Important contents: 24 files exist in the same top-level area; see the file inventory for exact members.

### documentation
- Purpose: Architecture and deployment documentation.
- Relationship: belongs to the documentation area of the repository and is used by files underneath it.
- Important contents: 19 files exist in the same top-level area; see the file inventory for exact members.

### documentation/architecture
- Purpose: Architecture and deployment documentation.
- Relationship: belongs to the documentation area of the repository and is used by files underneath it.
- Important contents: 19 files exist in the same top-level area; see the file inventory for exact members.

### documentation/functional_testing
- Purpose: Architecture and deployment documentation.
- Relationship: belongs to the documentation area of the repository and is used by files underneath it.
- Important contents: 19 files exist in the same top-level area; see the file inventory for exact members.

### documentation/review-package
- Purpose: Architecture and deployment documentation.
- Relationship: belongs to the documentation area of the repository and is used by files underneath it.
- Important contents: 19 files exist in the same top-level area; see the file inventory for exact members.

### enterprise
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/backend
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/backend/enterprise_core
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/backend/enterprise_core/migrations
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/config
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/config/templates
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/lib/assets
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/lib/components/Forms/ModelForm
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/lib/components/Logo
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/lib/components/SideBar
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/lib/utils
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/audit-log
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/components
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/campaigns/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/domain-analytics
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/details/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/extra/data-wizard
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/folders/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/folders/[id=uuid]/export
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/frameworks/inspect-requirement/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/insights/impact-analysis
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/insights/priority-review
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/insights/timeline-view
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/my-assignments
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/favicon
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/logo
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/[field=integration_field]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/configs/[id=uuid]/remote-objects
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/configs/[id=uuid]/rpc
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/jira
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/servicenow
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/test-connection
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/workflow-cases
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(app)/(internal)/workflow-cases/[id=uuid]
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/(authentication)/login
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/frontend/src/routes/favicon
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### enterprise/legacy
- Purpose: Enterprise overlay and packaging.
- Relationship: belongs to the enterprise area of the repository and is used by files underneath it.
- Important contents: 114 files exist in the same top-level area; see the file inventory for exact members.

### frontend
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/messages
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/project.inlang
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/server
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/assets
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Anchor
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Assets
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/BIA
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Breadcrumbs
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Calendar
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Chart
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/CommandPalette
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/CommentsPanel
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ContextMenu/applied-controls
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ContextMenu/ebios-rm
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ContextMenu/elementary-actions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ContextMenu/evidences
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ContextMenu/task-nodes
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/DataViz
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/DetailView
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Dropdown
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/EbiosRM
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/FocusMode
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Forms
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Forms/ModelForm
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Forms/OTP
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/FrameworkEquivalence
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/FrameworkMappingsChart
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/GanttView
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/List
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Logo
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Modals
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ModelTable
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ModelTable/field
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Notifications
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/RiskMatrix
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Settings
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/SideBar
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/SideBar/QuickStart
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Snippets/AutocompleteSelect
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/TableOfContents
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/TableRowActions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/Toast
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/TreeView
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/ValidationFlows
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/components/utils
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/lib/utils
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/params
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/[filter=filters]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/[field=fields]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/batch-action
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/export
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/[model=urlmodel]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/accreditations/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/actors/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/analytics
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/analytics/composer
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/analytics/gdpr
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/analytics/tprm
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/applied-controls/flash-mode
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/applied-controls/kanban-mode
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/dependencies
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/assets/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/assets/autocomplete
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/assets/graph
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/backup-restore
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/backup-restore/dump-db
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/report
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/visual
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/calendar
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/calendar/[year]/[month]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/csv
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/pdf
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/advanced-analytics
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/comparable_audits
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/evidences-list
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/csv
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/word
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/flash-mode
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/compliance-assessments/compare
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/content-types
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/contracts/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]/layout
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/report
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/visual
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/baseline
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/feared-events
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-2/ro-to
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/ecosystem
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/strategic-scenarios
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/elementary-actions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/operational-scenario
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-5/risk-analyses
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ebios-rm/batch-action
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/entities/graph
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/entity-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/batch-create
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/calendar-activity
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/circle-packing
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/ecosystem
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/graph
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/loss-exceedance
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/mapping
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/mapping/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/ordered-list
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/timeseries
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/experimental/yearly-tasks-review
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/md
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/pdf
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/folders/import-dummy
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/excel-template
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/generic-collections/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/incidents/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/export/md
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/export/pdf
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/libraries
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/license-management
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/tree
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/mapping-libraries
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/metric-instances/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-assignments
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile/change-password
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile/settings
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/components
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/utils
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/my-profile/settings/pat/components
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/edges
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/nodes
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operating-modes/default-ref-id
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/operational-scenarios/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/policies/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/rename
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/step/[stepId=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/upgrade
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/presets
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/presets/apply
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/processings/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-hypotheses/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-scenarios/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/executive-summary
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/key-metrics
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/quick-start
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/recap
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/registration-requests
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/reports
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/reports/dora-roi
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/reports/dora-roi/download
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/requirement-assessments/[id=uuid]/suggestions/applied-controls
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/requirement-mapping-sets/graph
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/export/excel
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/export/pdf
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/convert-to-quantitative
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/csv
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/pdf
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/xlsx
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/sync-to-actions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-matrices/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/sync-to-actions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/risk-scenarios/default-ref-id
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/scoring-assistant
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/security-exceptions/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings/saml/download-cert
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings/webhooks
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/settings/webhooks/event-types
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/stakeholders/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/tree
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/strategic-scenarios/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/sync-mappings/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/task-nodes/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/task-templates/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit/set-password
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/validation-flows/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/vulnerabilities/treemap
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/workflow-cases
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/x-rays
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(internal)/x-rays/inspect
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/auditee-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/auditee-dashboard
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/assignments
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/suggestions/applied-controls
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/sync-to-actions
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/table-mode
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/evidence-revisions/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/evidence-revisions/[id=uuid]/attachment
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/evidences/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/evidences/[id=uuid]/attachment
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/edit
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/assets/disaster-recovery-objectives
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/assets/security-objectives
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(app)/setup-mfa
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/first-connexion
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/login
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/login/mfa/components
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/login/mfa/utils
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/logout
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/password-reset
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/password-reset/confirm
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/register
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/(authentication)/sso/authenticate/[token]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/build
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/cascade-info/[model]/[id]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/comments
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/comments/[id]
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/user-preferences
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/src/routes/fe-api/waiting-risk-acceptances
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/static
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/static/vendor
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/functional
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/functional/detailed
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/functional/detailed/settings
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/functional/enterprise/settings
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/fuzz/open-redirect
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/hot-reload
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/keycloak
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/utils
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/utilsv2/base
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/utilsv2/core
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/utilsv2/derived
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### frontend/tests/utilsv2/derived/model-form
- Purpose: Primary SvelteKit frontend.
- Relationship: belongs to the frontend area of the repository and is used by files underneath it.
- Important contents: 809 files exist in the same top-level area; see the file inventory for exact members.

### git_hooks
- Purpose: Supporting project file.
- Relationship: belongs to the git_hooks area of the repository and is used by files underneath it.
- Important contents: 2 files exist in the same top-level area; see the file inventory for exact members.

### integration
- Purpose: Integration support or tests.
- Relationship: belongs to the integration area of the repository and is used by files underneath it.
- Important contents: 2 files exist in the same top-level area; see the file inventory for exact members.

### packaging/rhel
- Purpose: Packaging and release artifacts.
- Relationship: belongs to the packaging area of the repository and is used by files underneath it.
- Important contents: 12 files exist in the same top-level area; see the file inventory for exact members.

### packaging/rhel/SPECS
- Purpose: Packaging and release artifacts.
- Relationship: belongs to the packaging area of the repository and is used by files underneath it.
- Important contents: 12 files exist in the same top-level area; see the file inventory for exact members.

### packaging/rhel/scripts
- Purpose: Packaging and release artifacts.
- Relationship: belongs to the packaging area of the repository and is used by files underneath it.
- Important contents: 12 files exist in the same top-level area; see the file inventory for exact members.

### packaging/rhel/systemd
- Purpose: Packaging and release artifacts.
- Relationship: belongs to the packaging area of the repository and is used by files underneath it.
- Important contents: 12 files exist in the same top-level area; see the file inventory for exact members.

### packaging/rhel/templates
- Purpose: Packaging and release artifacts.
- Relationship: belongs to the packaging area of the repository and is used by files underneath it.
- Important contents: 12 files exist in the same top-level area; see the file inventory for exact members.

### perf_testing
- Purpose: Supporting project file.
- Relationship: belongs to the perf_testing area of the repository and is used by files underneath it.
- Important contents: 6 files exist in the same top-level area; see the file inventory for exact members.

### tests
- Purpose: Top-level tests and validation assets.
- Relationship: belongs to the tests area of the repository and is used by files underneath it.
- Important contents: 1 files exist in the same top-level area; see the file inventory for exact members.

### tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/3cf
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/AI-ACT
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/CCPA
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/CROE-FOR-FMI
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/Controlli-Minimi-AGID
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/Cyber_essentials_requirements
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/DGA
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ENS decreto
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ESRS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/EU
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/FNCS-v2
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/HDS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ITAR
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/K ISMS-P
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/NIS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/NIS2
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/NIS2/mappings
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/NIS2/tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/OTCC
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/PART-IS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/PSSIE
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/RGS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/TIBER
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/acn-it
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/adobe
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/adobe/mappings
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/aicpa
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/aircyber
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/anssi
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/anssi/tools/ad
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/anssi/tools/mon-aide-cyber
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/apra
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/bio2
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/bsi
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/canada
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/canada/tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ccb
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ccm
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cis
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cisa
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cisco
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cisco/mappings
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cjis
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/clausier-sante
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cmmc
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cnil
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/cra
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/dfs-500
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/dgssi
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/dora
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/dora/RTS
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/dora/RTS/tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/e-its
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ecc
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/enisa
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/essential-eight
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/etat_beninois
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/fadp
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/finma
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/gdpr
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/google
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/gsa
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ict-minimal
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/india
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/intuitem
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/intuitem/metrics
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/iso
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/iso27001
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/lpm
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/lt-nis2-kibernetinio-saugumo-istatymas
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/matrix
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/mcas
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/microsoft
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/mitre
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ncsc
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/ai-rmf
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/csf2-tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/privacy
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/sp-800-171
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/sp-800-218
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/sp-800-53
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/sp-800-66
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nist/sp-800-82
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/nzism
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/owasp
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pci-dss
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pci-dss/tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pgssi-s
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pqcc
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pspdv
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/pspf
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/rbi
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/ref_audit_ssi_tunisie
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/sama
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/sample
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/scf
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/scf/mappings
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/scf/tools
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/sikker-digital
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/standards-for-safeguarding-customer-information
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/swift
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/tisax
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/excel/vcsa
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/mapping_builder
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/misc
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

### tools/misc/questionnaires
- Purpose: Utility scripts and maintenance tools.
- Relationship: belongs to the tools area of the repository and is used by files underneath it.
- Important contents: 360 files exist in the same top-level area; see the file inventory for exact members.

## File Analysis
### .dockerignore
- .dockerignore | [file] | [important] | Supporting project file.

### .eslintrc.js
- .eslintrc.js | [code/config] | [important] | Supporting project file.

### .git
- .git/COMMIT_EDITMSG | [file] | [important] | Supporting project file.
- .git/config | [file] | [important] | Supporting project file.
- .git/description | [file] | [important] | Supporting project file.
- .git/HEAD | [file] | [important] | Supporting project file.
- .git/hooks/applypatch-msg.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/commit-msg.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/fsmonitor-watchman.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/post-update.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-applypatch.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-commit.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-merge-commit.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-push.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-rebase.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/pre-receive.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/prepare-commit-msg.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/push-to-checkout.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/sendemail-validate.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/hooks/update.sample | [file] | [important] | Configuration, sample data, or auxiliary artifact.
- .git/index | [file] | [important] | Supporting project file.
- .git/info/exclude | [file] | [important] | Supporting project file.
- .git/logs/HEAD | [file] | [important] | Supporting project file.
- .git/logs/refs/heads/AmroBranchAI | [file] | [important] | Supporting project file.
- .git/logs/refs/heads/main | [file] | [important] | Supporting project file.
- .git/logs/refs/remotes/origin/AmroBranchAI | [file] | [important] | Supporting project file.
- .git/logs/refs/remotes/origin/HEAD | [file] | [important] | Supporting project file.
- .git/objects/pack/pack-168e9675d394b5e0756a9c2185b7ee9543ee06fd.idx | [file] | [important] | Supporting project file.
- .git/objects/pack/pack-168e9675d394b5e0756a9c2185b7ee9543ee06fd.pack | [file] | [important] | Supporting project file.
- .git/objects/pack/pack-168e9675d394b5e0756a9c2185b7ee9543ee06fd.rev | [file] | [important] | Supporting project file.
- .git/packed-refs | [file] | [important] | Supporting project file.
- .git/refs/heads/AmroBranchAI | [file] | [important] | Supporting project file.
- .git/refs/heads/main | [file] | [important] | Supporting project file.
- .git/refs/remotes/origin/AmroBranchAI | [file] | [important] | Supporting project file.
- .git/refs/remotes/origin/HEAD | [file] | [important] | Supporting project file.

### .gitattributes
- .gitattributes | [file] | [important] | Supporting project file.

### .github
- .github/copilot-instructions.md | [doc] | [important] | Supporting project file.

### .gitignore
- .gitignore | [file] | [important] | Supporting project file.

### .pre-commit-config.yaml
- .pre-commit-config.yaml | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### CODE_OF_CONDUCT.md
- CODE_OF_CONDUCT.md | [doc] | [important] | Documentation or policy file.

### CONTRIBUTING.md
- CONTRIBUTING.md | [doc] | [important] | Documentation or policy file.

### Caddyfile
- Caddyfile | [file] | [important] | Supporting project file.

### Contributor License Agreement.md
- Contributor License Agreement.md | [doc] | [important] | Supporting project file.

### DEPLOYMENT.md
- DEPLOYMENT.md | [doc] | [important] | Documentation or policy file.

### LICENSE-AGPL.txt
- LICENSE-AGPL.txt | [doc] | [important] | Documentation or policy file.

### LICENSE.md
- LICENSE.md | [doc] | [important] | Documentation or policy file.

### PROJECT_FULL_REPORT.md
- PROJECT_FULL_REPORT.md | [doc] | [important] | Supporting project file.

### README.md
- README.md | [doc] | [important] | Documentation or policy file.

### SECURITY.md
- SECURITY.md | [doc] | [important] | Documentation or policy file.

### TECHNICAL_REPORT.md
- TECHNICAL_REPORT.md | [doc] | [important] | Documentation or policy file.

### X-RAYS_QUALITY_CHECKS.md
- X-RAYS_QUALITY_CHECKS.md | [doc] | [important] | Supporting project file.

### all_frameworks_export.csv
- all_frameworks_export.csv | [file] | [important] | Supporting project file.

### automation
- automation/.python-version | [file] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/.gitignore | [file] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/credentials/CisoAssistantApi.credentials.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/gulpfile.js | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/icons/myservice.svg | [file] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/CisoAssistantService/CisoAssistantService.node.json | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/CisoAssistantService/myservice.svg | [file] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/CisoAssistantService.node.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/AppliedControlHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/AssetHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/AuditHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/BaseResourceHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/DataBreachHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/DomainHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/EntityAssessmentHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/EntityHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/EvidenceHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/FindingHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/FindingsAssessmentHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/FrameworkHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/IncidentHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/index.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/PerimeterHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/RepresentativeHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/RightRequestHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/RiskAssessmentHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/RiskMatrixHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/RiskScenarioHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/SecurityExceptionHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/SolutionHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/SystemHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/TaskDefinitionHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/TaskOccurrenceHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/handlers/VulnerabilityHandler.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/myservice.svg | [file] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/registry/ResourceRegistry.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/types/index.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/utils/errors.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/utils/http.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/utils/index.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/utils/validation.test.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/nodes/utils/validation.ts | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/package-lock.json | [code/config] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/package.json | [code/config] | [critical] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/README.md | [doc] | [important] | Automation and workflow helpers.
- automation/n8n/n8n-nodes-ca/tsconfig.json | [code/config] | [important] | Automation and workflow helpers.
- automation/prefect_impl.py | [code/config] | [important] | Automation and workflow helpers.
- automation/prowler_helpers/__init__.py | [code/config] | [important] | Automation and workflow helpers.
- automation/prowler_helpers/utils.py | [code/config] | [important] | Automation and workflow helpers.
- automation/pyproject.toml | [code/config] | [critical] | Automation and workflow helpers.
- automation/README.md | [doc] | [important] | Automation and workflow helpers.
- automation/settings.sample.json | [code/config] | [important] | Automation and workflow helpers.
- automation/uv.lock | [generated] | [generated/artifact] | Automation and workflow helpers.

### backend
- backend/.dockerignore | [file] | [important] | Django backend and server-side platform code.
- backend/.gitignore | [file] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_applied_controls.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_assets.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_compliance_assessments.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_evidences.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_folders.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_libraries.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_load_backup.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_perimeters.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_personal_access_tokens.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_policies.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_reference_controls.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_requirement_assessments.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_requirement_nodes.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_risk_acceptances.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_risk_assessments.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_risk_scenarios.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_soa.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_threats.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_user_groups.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_users.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_api_workflow_cases.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_parent_field_permission.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/api/test_utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/conftest.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/app_tests/sample_640x480.jpg | [artifact] | [generated/artifact] | Django backend and server-side platform code.
- backend/app_tests/test_file.txt | [doc] | [important] | Django backend and server-side platform code.
- backend/app_tests/test_image.jpg | [artifact] | [generated/artifact] | Django backend and server-side platform code.
- backend/app_tests/test_vars.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/cal/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/cal/admin.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/cal/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/cal/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/cal/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/cal/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/cal/tests/__init__.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/cal/tests/test_models.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/cal/tests/test_utils.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/cal/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/asgi.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/build.json | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/meta.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/scripts/generate_build_file.sh | [code/config] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/settings.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/ciso_assistant/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/ciso_assistant/VERSION | [file] | [important] | Django backend and server-side platform code.
- backend/ciso_assistant/wsgi.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/admin_config.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/audit_visibility.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/base_models.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/constants.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/context.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/custom_middleware.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/dora.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/email_utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/excel.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/focus_middleware.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/generators.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/helpers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/instance_metrics.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/locale/fr/LC_MESSAGES/django.mo | [file] | [important] | Django backend and server-side platform code.
- backend/core/locale/fr/LC_MESSAGES/django.po | [file] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/audit_visibility.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/backfill_workflow_cases.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/clone_instance.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/dump_permissions.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/generate_soa.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/mapping.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/metrics_server.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_assets.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_domains.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_findings.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_incidents.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_security_exceptions.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_tasks.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/populate_vulnerabilities.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/prune_auditlog.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/README_clone_instance.md | [doc] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/README_metrics_server.md | [doc] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/reset_audit.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/reset_mail.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/set_assessment_results.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/status.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/management/commands/welcome_mail.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/mappings/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/mappings/engine.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0002_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0003_alter_riskscenario_strength_of_knowledge.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0004_complianceassessment_is_published_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0005_alter_project_lc_status_alter_securitymeasure_effort.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0006_remove_securitymeasure_security_function_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0007_alter_requirementlevel_framework_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0008_alter_complianceassessment_status_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0009_framework_max_score_framework_min_score_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0010_rename_score_definition_framework_scores_definition_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0011_auto_20240501_1342.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0012_alter_appliedcontrol_updated_at_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0013_requirementnode_typical_evidence.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0014_auto_20240522_1731.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0015_remove_complianceassessment_result_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0016_riskscenario_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0017_requirementassessment_mapping_inference_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0018_appliedcontrol_csf_function_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0018_framework_translations_loadedlibrary_translations_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0019_merge_20240726_2156.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0020_fix_libraries_objects_meta.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0021_alter_framework_urn_alter_loadedlibrary_urn_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0022_riskscenario_qualifications.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0023_alter_appliedcontrol_status.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0024_appliedcontrol_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0025_complianceassessment_folder_riskassessment_folder_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0026_appliedcontrol_cost.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0027_requirementassessment_answer_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0028_complianceassessment_observation_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0029_alter_appliedcontrol_link_alter_evidence_link.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0030_appliedcontrol_start_date.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0031_vulnerability_riskscenario_vulnerabilities.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0032_vulnerability_applied_controls_filteringlabel_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0033_fix_mitre_lib_version.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0034_fix_loaded_libraries_objects_meta.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0035_riskscenario_existing_applied_controls.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0036_asset_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0037_appliedcontrol_priority.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0038_asset_disaster_recovery_objectives_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0039_make_urn_lowercase.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0040_riskscenario_ref_id.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0041_add_ref_id_to_project_appliedcontrol_assessment.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0042_asset_filtering_labels.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0043_historicalmetric.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0044_qualification.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0045_alter_appliedcontrol_category_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0046_riskassessment_ebios_rm_study.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0047_loadedlibrary_publication_date_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0048_alter_asset_security_objectives.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0049_complianceassessment_show_documentation_score_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0050_appliedcontrol_progress_field.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0051_rename_project_perimeter_alter_perimeter_options_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0052_securityexception_appliedcontrol_security_exceptions_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0053_asset_ref_id_alter_riskscenario_ref_id.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0054_alter_appliedcontrol_is_published_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0055_alter_storedlibrary_content.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0056_data_store_matrix_json_as_dict_not_str.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0057_store_storedlibrary_content_as_dict_not_str.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0058_findingsassessment_finding.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0059_complianceassessment_assets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0060_fix_matrix_json_definition.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0061_findingsassessment_ref_id.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0062_appliedcontrol_filtering_labels_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0063_appliedcontrol_assets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0064_incident_timelineentry.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0064_replace_slash_in_folder_names.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0065_vulnerability_assets_alter_finding_severity_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0066_evidence_filtering_labels.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0067_appliedcontrol_control_impact_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0068_tasktemplate_tasknode.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0069_auto_20250414_2023.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0070_auto_fix_finding_folider.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0071_remove_requirementassessment_answer_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0072_assetclass_asset_asset_class_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0073_alter_asset_security_objectives.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0074_tasktemplate_findings_assessment.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0075_incident_detection_incident_reported_at.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0076_finding_due_date_finding_eta.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0077_incident_link.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0078_complianceassessment_evidences.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0079_finding_evidences_findingsassessment_evidences.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0080_auto_20250703_1217.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0081_campaign_complianceassessment_campaign.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0082_riskscenario_inherent_impact_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0083_fix_nis2_framework.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0084_perimeter_default_assignee.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0085_auto_20250725_0939.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0086_riskassessment_risk_tolerance.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0087_appliedcontrol_observation_asset_observation_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0088_tasktemplate_link.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0089_organisationissue_organisationobjective.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0090_complianceassessment_is_locked_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0091_appliedcontrol_objectives_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0092_terminology.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0093_alter_asset_parent_assets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0094_alter_incident_qualifications_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0095_delete_qualification.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0096_appliedcontrol_cost_to_json.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0097_evidence_lifecycle_schema.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0098_evidence_lifecycle_data_migration.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0099_incident_entities.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0100_alter_terminology_field_path.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0101_alter_tasktemplate_assigned_to.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0102_alter_vulnerability_status.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0103_alter_terminology_field_path.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0104_add_info_severity.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0105_publish_terminologies.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0106_alter_terminology_is_published.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0107_asset_recovery_capabilities_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0108_requirementnode_importance_requirementnode_weight.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0109_alter_asset_asset_class.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0110_alter_riskscenario_justification.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0111_finding_priority.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0112_storedlibrary_autoload.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0113_autoload_mappingsets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0114_asset_dora_criticality_assessment_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0115_riskscenario_operational_scenario.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0116_validationflow_flowevent.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0117_evidencerevision_task_node_tasktemplate_evidences.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0118_riskscenario_antecedent_scenarios_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0119_libraryfilteringlabel_storedlibrary_filtering_labels.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0119_securityexception_observation.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0120_alter_terminology_field_path.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0121_merge_20251223_1523.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0122_complianceassessment_extended_result_enabled_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0123_organisationobjective_metrics.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0124_evidencerevision_attachment_hash.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0125_team_actor.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0126_data_backfill_actors.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0127_remove_appliedcontrol_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0128_alter_organisationobjective_assigned_to_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0129_data_backfill_organisationobjective_tasktemplete_databreach_processing_actor.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0130_remove_organisationobjective_new_assigned_to_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0131_remove_findingsassessment_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0132_complianceassessment_score_calculation_method.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0133_organisationissue_expiration_date_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0133_riskscenario_folder_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0134_populate_riskscenario_folder.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0135_requirementassignment.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0136_incident_filtering_labels.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0137_add_threats_to_finding.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0138_validationflow_accreditations_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0139_tasknode_scheduled_date.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0140_populate_tasknode_scheduled_date.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0141_complianceassessment_auto_sync_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0142_alter_requirementassignment_options_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0143_comment.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0144_presetjourney_presetjourneystep.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0145_alter_team_leader.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0146_organisationobjective_closing_date_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0147_repair_requirementnode_questions_column.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0148_workflowcase_workflowcaseapprovalstep_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0150_soa_models.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/0151_add_riskmatrix_editing_fields.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/core/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/pagination.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/permissions.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/sandbox.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/serializer_fields.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/startup.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/tasks.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/templates/core/action_plan_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/audit_report.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/audit_report_template.docx | [file] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/audit_report_template_en.docx | [file] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/audit_report_template_en.pptx | [file] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/audit_report_template_fr.docx | [file] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/base_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/findings_assessment_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/incident_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/mp_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/ra_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/risk_action_plan_pdf.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/soa_export_ar.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/core/soa_export_en.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/applied_control_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/applied_control_expiring_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/assignment_activated.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/assignment_reviewed.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/assignment_submitted.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/compliance_assessment_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/compliance_assessment_due_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/evidence_expiring_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/expired_controls.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/expired_evidences.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/risk_scenario_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/task_node_due_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/task_node_overdue.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/task_template_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/validation_deadline.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/validation_flow_created.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/en/validation_flow_updated.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/applied_control_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/applied_control_expiring_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/assignment_activated.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/assignment_reviewed.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/assignment_submitted.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/compliance_assessment_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/compliance_assessment_due_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/evidence_expiring_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/expired_controls.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/expired_evidences.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/risk_scenario_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/task_node_due_soon.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/task_node_overdue.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/task_template_assignment.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/validation_deadline.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/validation_flow_created.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/emails/fr/validation_flow_updated.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/registration/first_connexion_email.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/registration/first_connexion_email_sso.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/registration/password_reset_email.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/mp_data.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/ra_data.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/req_node.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/ri_list_nested.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/risk_legend.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/risk_matrix.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/risk_matrix_swapaxes.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/risk_matrix_swapaxes_vflip.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/snippets/risk_matrix_vflip.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templates/tprm/third_party_email.html | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templatetags/core_extras.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/templatetags/core_forms_extras.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/tests/__init__.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/fixtures.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/sandbox/conftest.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/sandbox/test_sandbox_functional.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/sandbox/test_sandbox_isolation.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_actor.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_audit_word_export.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_backfill_workflow_cases.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_excel.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_helpers.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_models.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_requirement_assessment.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_task.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_views.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_vulnerability.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/tests/test_workflow_case.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/core/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/utilities.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/validators.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/core/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/core/webhooks.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/crq/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/crq/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/crq/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/crq/migrations/0002_fix_folder_inheritance.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/crq/migrations/0002_quantitativeriskscenario_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/crq/migrations/0003_remove_quantitativeriskscenario_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/crq/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/crq/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/crq/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/crq/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/crq/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/crq/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/crq/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/data_wizard/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/admin.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/arm_helpers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/ebios_rm_excel_helpers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/data_wizard/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/data_wizard/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/data_wizard/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/data_wizard/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/data_wizard/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/Dockerfile | [file] | [critical] | Django backend and server-side platform code.
- backend/ebios_rm/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ebios_rm/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ebios_rm/helpers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0002_alter_roto_target_objective.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0003_remove_ebiosrmstudy_risk_assessments.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0004_remove_roto_pertinence_alter_roto_feared_events.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0005_remove_operationalscenario_attack_paths_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0006_alter_attackpath_stakeholders.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0007_ebiosrmstudy_meta.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0008_remove_attackpath_ro_to_couple_strategicscenario_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0009_alter_roto_activity.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0010_alter_ebiosrmstudy_risk_matrix.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0011_alter_roto_risk_origin.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0012_ebiosrmstudy_quotation_method_alter_roto_risk_origin_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0013_add_risk_origin_fk.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0014_migrate_risk_origin.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0015_replace_risk_origin.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0016_alter_fearedevent_qualifications.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0017_alter_operationalscenario_operating_modes_description.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0018_convert_stakeholder_category_to_terminology.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0019_alter_ebiosrmstudy_quotation_method.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0020_alter_fearedevent_ebios_rm_study.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0021_strategicscenario_focused_feared_event.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0022_ebiosrmstudy_new_authors_ebiosrmstudy_new_reviewers.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0023_remove_ebiosrmstudy_new_authors_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/0024_remove_operatingmode_elementary_actions_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/ebios_rm/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/ebios_rm/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/ebios_rm/tests/fixtures.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/ebios_rm/tests/test_ebios_rm_study.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/ebios_rm/tests/test_feared_event.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/ebios_rm/tests/test_ro_to.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/ebios_rm/tests/test_stakeholder.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/ebios_rm/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/ebios_rm/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/global_settings/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/global_settings/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/global_settings/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/global_settings/migrations/0002_alter_globalsettings_folder.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/global_settings/migrations/0003_alter_globalsettings_name.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/global_settings/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/global_settings/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/global_settings/routers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/global_settings/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/global_settings/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/global_settings/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/global_settings/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/adapter.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/cache_builders.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/jwt_auth.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0002_purge_validator.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0003_alter_folder_updated_at_alter_role_updated_at_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0004_ssosettings_user_is_sso.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0005_alter_user_managers.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0006_alter_role_folder_alter_roleassignment_folder_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0007_alter_folder_content_type.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0008_user_is_third_party.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0009_create_allauth_emailaddress_objects.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0010_user_preferences.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0011_replace_slash_in_folder_names.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0012_user_keep_local_login.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0013_personalaccesstoken.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0014_user_observation.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0015_user_expiry_date.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0016_folder_filtering_labels.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0017_alter_folder_is_published.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0018_cacheversion.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0019_add_view_globalsettings_in_custom_roles.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0020_folder_create_iam_groups.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0021_fix_auditee_iam_groups.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0022_add_role_tier.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0023_registrationrequest.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/0024_soa_models.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/iam/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/snapshot_cache.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/errors.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/oidc/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/oidc/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/oidc/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/saml/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/saml/defaults.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/sso/saml/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/saml/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/sso/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/tests/__init__.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/iam/tests/test_models.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/iam/tests/test_user.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/iam/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/iam/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/iam/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/integrations/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/base.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/jira/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/jira/client.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/jira/integration.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/jira/mapper.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/jira/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/servicenow/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/servicenow/client.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/servicenow/integration.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/itsm/servicenow/mapper.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/management/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/management/commands/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/management/commands/create_sync_mapping.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/management/commands/setup_jira_integration.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/integrations/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/integrations/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/integrations/registry.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/integrations/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/integrations/tasks.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/integrations/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/integrations/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/library/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/helpers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/3cf-ed1-v1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/3cf-v2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/adobe-ccf-v5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ai-act.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/aircyber-v1.5.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/annex-nis2-regulation--2024-2690-with-technical-implementation-guidance-by-enisa.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-architectures-si-sensibles-dr.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-genai-security-recommendations-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-guide-admin-securisee-si.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-guide-des-mecanismes-cryptographiques.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-guide-hygiene-detail.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-guide-hygiene.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-maturite-gestion-crise-1.0.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-mon-aide-cyber.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-points-de-controle-active-directory.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-rec-secu-interco-si-internet.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-rec-secu-ipsec.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-rec-secu-ssh.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-rec-secu-sys-ctrl-acces-phys-videoprot.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-recommandations-configuration-systeme-gnu-linux.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-recommandations-pour-la-protection-des-sie.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-recommandations-securite-architecture-systeme-journalisation.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-recommandations-securite-relatives-tls.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/anssi-referentiel-general-de-securite-annexe-b2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/asf-baseline-v2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bio2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-app-anwendungen.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-con-konzeption-und-vorgehensweisen.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-der-detektion-und-reaktion.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-ind-industrielle-it.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-inf-infrastruktur.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-isms-sicherheitsmanagement.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-net-netze-und-kommunikation.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-ops-betrieb.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-orp-organisation-und-personal.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bs-it-gs-2023-sys-it-systeme.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bsi-c5-2020.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/bsi-externer-cloud-dienste.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ccb-cff-2023-03-01.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ccpa act.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ccpa_regulations.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/checklist-dossier-homologation.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cis-benchmark-kubernetes.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cisa-cpg-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cisa-vendor-scrm.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cisco-ccf-v3.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cjis-version-5.9.5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cjis.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/clausier-sante-v2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cloud-sovereignty-framework.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cmmc-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cnil-guide-securite.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/Controlli-minimi-AGID.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/core_cybersecurity_metrics.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cps-230.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cps-234.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cra-regulation-annexes.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/critical_risk_matrix_3x3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/critical_risk_matrix_5x5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/croe-for-fmi.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cyber_essentials.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cyfun-small-self-assessment_new.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/cyfun2025.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/d3fend.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/de-tekniske-minimumskrav.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/dfs-500-2023-11.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/dnssi-2023-2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/doc-pol.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/dora.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/dynamic-questionnaire.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/e-its-2024.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ecc-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/enisa-5g-scm-v1.3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ens-decreto.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/esrs-p1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/esrs-p2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/esrs-p3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/essential-eight.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/fadp.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/fedramp-rev5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/finma-2023-01.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/fncs-v2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/formulaire-sdi-secnum-2216.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/framework-nazionale-cs-dp.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/gdpr-checklist.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/gdpr.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/gl-on-costs-and-losses.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/google-saif.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/hds-v2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ict-minimal.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/igi-1300.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/II-901_new.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/india-dpdpa-2023.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/intuitem-common-catalog.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/iso22301-2019.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/iso27001-2013.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/iso42001-2023.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/itar-compliance-program-guidelines.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/Itil_v4.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/its-incident-reporting.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/itsp.10.171.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/k-isms-p.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/label-ebios-risk-manager.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/loi05-20-maroc-06082020.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/lpm-oiv-2019.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/lt-nis2-kibernetinio-saugumo-istatymas.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/map-DNSSI_2023-iso27001_2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/map-iso27001-2022-loi-05-20.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/map-iso27001_2022-DNSSI_2023.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/map-nist-csf-1.1-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/map-nist-csf-1.1-nist-csf-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-bsi-c5-2020.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-cyber_essentials_requirements_for_it_infrastructure.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-fedramp-rev5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-nist-csf-1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-pcidss-4_0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-adobe-ccf-v5-and-soc2-2017-rev-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-annex-technical-and-methodological-requirements-nis2-and-ccb-cff-2023-03-01.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-annex-technical-and-methodological-requirements-nis2-and-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-annex-technical-and-methodological-requirements-nis2-and-nist-csf-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-ccb-cff-2023-03-01-and-ccb-cyfun2025.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-ccb-cff-2023-03-01-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cis-controls-v8-and-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cis-controls-v8-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-bsi-c5-2020.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-esquema-nacional-de-seguridad.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-fedramp-rev5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-ncsc-caf-3.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-nist-800-171-rev2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-nist-800-171-rev3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-nist-ssdf-1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-pcidss-4_0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-secnumcloud-3.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cisco-ccf-v3.0-and-soc2-2017-rev-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-cjis-policy-5.9.4-to-cjis-policy-5.9.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-dora-and-finma-2023-01.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-india-dpdpa-2023-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-iso27001-2013-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-iso27001-2022-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-iso27001-2022-to-itil4.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-iso27001-2022-to-secnumcloud-3.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-iso42001-2023-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-csf-2.0-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-csf-2.0-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-sp-800-53-rev5-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-sp-800-66-rev2-to-nist-csf-1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-sp-800-66-rev2-to-nist-csf-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-nist-sp-800-66-rev2-to-nist-sp-800-53-rev5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-pcidss-4_0-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-scf-2025.2.2-and-swift-cscf-v2025.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-secnumcloud-3.2-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-soc2-2017-rev-2022-and-scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping-soc2-2017-rev-2022-to-iso27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mapping_Loi-05-20_ISO27001-2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mas-threats.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/matrice-des-risques-critiques-3x3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mcas-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mcsb-v1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/mitre-attack.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nca-ccc-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nca-cscc-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nca-dcc-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nca-pdpl-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nca-tcc-1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ncsc-caf-3.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nis1-rules-fr.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nis2-directive.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-800-171-rev2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-800-171-rev3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-ai-rmf-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-csf-1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-csf-2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-privacy-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-sp-800-53-rev5.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-sp-800-66-rev2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-sp-800-82-annex-f.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nist-ssdf-1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/norea.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/nzism-3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/otcc.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/owasp-asvs-4.0.3.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/owasp-asvs-5.0.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/owasp-llm-checklist.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/owasp-masvs-v2.1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/owasp-top-10-web.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/part-is.d.or.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pcidss-4_0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pdis.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pgssi-s-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pqc-migration-roadmap.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-belgian-cyfun.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-cyber-resilience.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-dora-financial.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-eu-saas-startup.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-french-homologation.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-french-sme-anssi.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-iso27001-full.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-nis2-readiness.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-small-business-cisa-cpg.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/preset-us-soc2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pspf.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pssie-benin.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/pssie.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rbi-itgrcap-2023-2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/ref_audit_ssi_tunisie.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rgs-v2.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-3x3-mult.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-4x4-ebios-rm.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-4x4-pgssi-s-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-4x4-with-5-levels.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-5x5-iso-27005.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-5x5-sensitive.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk-matrix-6x6-detailed.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/risk_matrix_cyber_maroc-V1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/RNSI-Algerie-2020.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-dora-ict-related-incidents.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-dora-ict-risk-management.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-dora-ictservices-supporting.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-dora-incident-reporting_official.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-on-jet.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-ovs-conduct.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/rts-threat-led-penetration-tests.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/sama-csf-1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/scf-2024-2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/scf-2025.2.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/secnumcloud-3.2-annexe-2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/secnumcloud-3.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/soc2-2017.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/soc2_2017_with_rev_2022.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/standards-for-safeguarding-customer-information.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/swift-cscf-v2025v1.0.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/tiber-eu-2018.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/tisax-v5.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/tisax-v6.0.2.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/vcsa-v1.1.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/libraries/vendor-due-diligence.yaml | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/management/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/management/commands/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/management/commands/autoloadlibraries.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/management/commands/storelibraries.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/preset_executor.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/library/tests/__init__.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/library/tests/test_custom_library_import.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/library/tests/test_store_library_content.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/library/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/validators.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/library/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/locale/en/LC_MESSAGES/django.mo | [file] | [important] | Django backend and server-side platform code.
- backend/locale/en/LC_MESSAGES/django.po | [file] | [important] | Django backend and server-side platform code.
- backend/locale/fr/LC_MESSAGES/django.mo | [file] | [important] | Django backend and server-side platform code.
- backend/locale/fr/LC_MESSAGES/django.po | [file] | [important] | Django backend and server-side platform code.
- backend/logs/.gitignore | [file] | [important] | Django backend and server-side platform code.
- backend/manage.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/metrology/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/builtin_metrics.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/management/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/management/commands/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/management/commands/backfill_builtin_metrics.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/management/commands/cleanup_builtin_metrics.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/metrology/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/metrology/migrations/0002_metricinstance_new_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/metrology/migrations/0003_remove_metricinstance_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/metrology/migrations/0004_custommetricsample_evidence_revision_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/metrology/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/metrology/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/metrology/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/metrology/tasks.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/metrology/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/metrology/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/mypy.ini | [code/config] | [important] | Django backend and server-side platform code.
- backend/notifications/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/notifications/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/notifications/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/notifications/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/notifications/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/notifications/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/notifications/signals.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/notifications/tasks.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/notifications/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/notifications/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pmbok/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/pmbok/admin.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/pmbok/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/pmbok/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/pmbok/migrations/0002_alter_accreditation_author.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/pmbok/migrations/0003_remove_accreditation_new_author_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/pmbok/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/pmbok/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pmbok/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pmbok/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/pmbok/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pmbok/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/poetry.lock | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/admin.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/management/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/management/commands/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/management/commands/populate_privacy_data.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0002_alter_datacontractor_relationship_type_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0003_migrate_privacy_prefixes.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0004_migrate_privacy_prefixes_fix.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0005_alter_datacontractor_country_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0006_personaldata_assets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0007_rightrequest.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0008_purpose_legal_basis.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0009_processing_assigned_to_databreach.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0010_alter_datacontractor_country_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0011_processing_evidences.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0012_rightrequest_new_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0013_remove_rightrequest_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0014_remove_processing_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0015_remove_databreach_new_assigned_to_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0016_alter_datacontractor_name_alter_datarecipient_name_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/0017_data_split_legal_basis_choices.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/privacy/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/privacy/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/privacy/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/privacy/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/privacy/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pyproject.toml | [code/config] | [critical] | Django backend and server-side platform code.
- backend/pytest.ini | [code/config] | [important] | Django backend and server-side platform code.
- backend/README.md | [doc] | [important] | Django backend and server-side platform code.
- backend/resilience/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/resilience/admin.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/resilience/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/resilience/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/0002_businessimpactanalysis_is_locked.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/0003_alter_escalationthreshold_qualifications.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/0004_businessimpactanalysis_new_authors_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/0005_remove_businessimpactanalysis_new_authors_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/0006_alter_businessimpactanalysis_perimeter.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/resilience/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/resilience/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/resilience/tests.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/resilience/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/resilience/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/scripts/convert_ccm_v2.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/scripts/convert_library_v2.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/scripts/prep_cis_v2.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/serdes/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/serdes/permissions.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/serdes/README.md | [doc] | [important] | Django backend and server-side platform code.
- backend/serdes/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/serdes/tests/__init__.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/serdes/tests/test_dump.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/serdes/tests/test_utils.py | [code/config] | [optional] | Django backend and server-side platform code.
- backend/serdes/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/serdes/utils.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/serdes/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/startup.sh | [code/config] | [critical] | Django backend and server-side platform code.
- backend/test_fixtures.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/dora_export.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/dora_linter.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/management/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/management/commands/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/management/commands/populate_tprm_data.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0002_alter_entity_reference_link.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0003_entityassessment_representatives.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0004_remove_entityassessment_project_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0005_solution_assets.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0006_entityassessment_is_locked.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0007_entity_relationship.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0008_entity_country_entity_currency_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0009_migrate_solution_to_solutions.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0010_contract_new_owner_entityassessment_new_authors_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0011_remove_contract_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0012_alter_entityassessment_perimeter.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0013_rename_enclaves_to_entity_name.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/0014_alter_solution_dora_alternative_providers_identified.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/tprm/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/tprm/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/tprm/test/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/test/test_apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/test/test_models.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/test/test_serializers.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/tprm/views.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/webhooks/__init__.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/apps.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/config.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/management/commands/sync_event_types.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/migrations/0001_initial.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/webhooks/migrations/0002_webhookendpoint_new_owner.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/webhooks/migrations/0003_remove_webhookendpoint_new_owner_and_more.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/webhooks/migrations/__init__.py | [generated] | [generated/artifact] | Django backend and server-side platform code.
- backend/webhooks/models.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/webhooks/registry.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/serializers.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/webhooks/service.py | [code/config] | [important] | Django backend and server-side platform code.
- backend/webhooks/tasks.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/webhooks/urls.py | [code/config] | [critical] | Django backend and server-side platform code.
- backend/webhooks/views.py | [code/config] | [critical] | Django backend and server-side platform code.

### backup-20260312-103121.json
- backup-20260312-103121.json | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### caddy_data
- caddy_data/caddy/certificates/local/localhost/localhost.crt | [file] | [important] | Supporting project file.
- caddy_data/caddy/certificates/local/localhost/localhost.json | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.
- caddy_data/caddy/certificates/local/localhost/localhost.key | [file] | [important] | Supporting project file.
- caddy_data/caddy/instance.uuid | [file] | [important] | Supporting project file.
- caddy_data/caddy/last_clean.json | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.
- caddy_data/caddy/pki/authorities/local/intermediate.crt | [file] | [important] | Supporting project file.
- caddy_data/caddy/pki/authorities/local/intermediate.key | [file] | [important] | Supporting project file.
- caddy_data/caddy/pki/authorities/local/root.crt | [file] | [important] | Supporting project file.
- caddy_data/caddy/pki/authorities/local/root.key | [file] | [important] | Supporting project file.

### charts
- charts/ciso-assistant/.helmignore | [file] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/Chart.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/README.md | [doc] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/_helpers.tpl | [file] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/configmap.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/ingress.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/secret.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/service.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/templates/statefulset.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/values.schema.json | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant/values.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/.helmignore | [file] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/.schema.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/Chart.lock | [generated] | [generated/artifact] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/Chart.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/generate_schema.py | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/README.md | [doc] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/README.md.gotmpl | [file] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/_helpers.tpl | [file] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/backend/deployment.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/backend/persistentvolumeclaim.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/backend/secret.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/backend/service.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/frontend/deployment.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/frontend/service.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/ingress/ingress.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/ingress/tls-secret.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/templates/serviceaccount.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/values.schema.json | [code/config] | [important] | Helm/Kubernetes chart packaging.
- charts/ciso-assistant-next/values.yaml | [code/config] | [important] | Helm/Kubernetes chart packaging.

### check_ar.py
- check_ar.py | [code/config] | [important] | Supporting project file.

### check_frameworks.py
- check_frameworks.py | [code/config] | [important] | Supporting project file.

### check_iam.py
- check_iam.py | [code/config] | [important] | Supporting project file.

### check_status.py
- check_status.py | [code/config] | [important] | Supporting project file.

### check_ug_fields.py
- check_ug_fields.py | [code/config] | [important] | Supporting project file.

### check_untranslated.py
- check_untranslated.py | [code/config] | [important] | Supporting project file.

### cli
- cli/.clica.env.template | [file] | [important] | CLI and MCP tooling.
- cli/.gitignore | [file] | [important] | CLI and MCP tooling.
- cli/.mcp.env.example | [file] | [important] | CLI and MCP tooling.
- cli/.python-version | [file] | [important] | CLI and MCP tooling.
- cli/ca_mcp/__init__.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/client.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/config.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/resolvers.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/server.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/__init__.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/analysis_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/ebios_rm_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/library_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/read_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/tprm_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/update_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/tools/write_tools.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/utils/__init__.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp/utils/response_formatter.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ca_mcp.py | [code/config] | [important] | CLI and MCP tooling.
- cli/ciso_assistant_cli.egg-info/dependency_links.txt | [doc] | [important] | CLI and MCP tooling.
- cli/ciso_assistant_cli.egg-info/PKG-INFO | [file] | [important] | CLI and MCP tooling.
- cli/ciso_assistant_cli.egg-info/requires.txt | [doc] | [important] | CLI and MCP tooling.
- cli/ciso_assistant_cli.egg-info/SOURCES.txt | [doc] | [important] | CLI and MCP tooling.
- cli/ciso_assistant_cli.egg-info/top_level.txt | [doc] | [important] | CLI and MCP tooling.
- cli/clica.py | [code/config] | [important] | CLI and MCP tooling.
- cli/evidences.csv | [file] | [important] | CLI and MCP tooling.
- cli/mcp.md | [doc] | [important] | CLI and MCP tooling.
- cli/MCP_SETUP_GUIDE.md | [doc] | [important] | CLI and MCP tooling.
- cli/pyproject.toml | [code/config] | [critical] | CLI and MCP tooling.
- cli/RA_sample.csv | [file] | [important] | CLI and MCP tooling.
- cli/README.md | [doc] | [important] | CLI and MCP tooling.
- cli/requirements.txt | [doc] | [important] | CLI and MCP tooling.
- cli/sample_assets.csv | [file] | [important] | CLI and MCP tooling.
- cli/sample_controls.csv | [file] | [important] | CLI and MCP tooling.
- cli/smiling.png | [artifact] | [generated/artifact] | CLI and MCP tooling.
- cli/tests/__init__.py | [code/config] | [optional] | CLI and MCP tooling.
- cli/tests/pytest.ini | [code/config] | [optional] | CLI and MCP tooling.
- cli/tests/requirements.txt | [doc] | [optional] | CLI and MCP tooling.
- cli/tests/test_cli.py | [code/config] | [optional] | CLI and MCP tooling.
- cli/tests/test_mcp.py | [code/config] | [optional] | CLI and MCP tooling.
- cli/uv.lock | [generated] | [generated/artifact] | CLI and MCP tooling.

### config
- config/.gitignore | [file] | [important] | Configuration and certificates.
- config/certificates.yaml | [code/config] | [important] | Configuration and certificates.
- config/docker-compose-barebone.yml | [code/config] | [critical] | Configuration and certificates.
- config/docker-compose.sh | [code/config] | [critical] | Configuration and certificates.
- config/extra/docker-compose-build-upgrade.sh | [code/config] | [critical] | Configuration and certificates.
- config/extra/docker-compose-pg-build.yml | [code/config] | [critical] | Configuration and certificates.
- config/gen_local_cert.sh | [code/config] | [important] | Configuration and certificates.
- config/init-custom-ca-certificates.sh | [code/config] | [important] | Configuration and certificates.
- config/make_config.py | [code/config] | [important] | Configuration and certificates.
- config/README.md | [doc] | [important] | Configuration and certificates.
- config/requirements.txt | [doc] | [important] | Configuration and certificates.
- config/templates/docker-compose-postgresql-bunkerweb.yml.j2 | [file] | [critical] | Configuration and certificates.
- config/templates/docker-compose-postgresql-caddy.yml.j2 | [file] | [critical] | Configuration and certificates.
- config/templates/docker-compose-postgresql-traefik.yml.j2 | [file] | [critical] | Configuration and certificates.
- config/templates/docker-compose-sqlite-bunkerweb.yml.j2 | [file] | [critical] | Configuration and certificates.
- config/templates/docker-compose-sqlite-caddy.yml.j2 | [file] | [critical] | Configuration and certificates.
- config/templates/docker-compose-sqlite-traefik.yml.j2 | [file] | [critical] | Configuration and certificates.

### conventional_commits.md
- conventional_commits.md | [doc] | [important] | Supporting project file.

### core_objects.png
- core_objects.png | [artifact] | [generated/artifact] | Binary asset or data artifact.

### cspell.json
- cspell.json | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### db
- db/django_secret_key | [file] | [important] | Supporting project file.
- db/huey.db | [file] | [important] | Supporting project file.
- db/huey.db-shm | [file] | [important] | Supporting project file.
- db/huey.db-wal | [file] | [important] | Supporting project file.

### db-backup-sqlite-20260312-103213
- db-backup-sqlite-20260312-103213/ciso-assistant.sqlite3-shm | [file] | [generated/artifact] | Supporting project file.
- db-backup-sqlite-20260312-103213/ciso-assistant.sqlite3-wal | [file] | [generated/artifact] | Supporting project file.
- db-backup-sqlite-20260312-103213/huey.db | [file] | [important] | Supporting project file.
- db-backup-sqlite-20260312-103213/huey.db-shm | [file] | [important] | Supporting project file.
- db-backup-sqlite-20260312-103213/huey.db-wal | [file] | [important] | Supporting project file.

### dispatcher
- dispatcher/.dockerignore | [file] | [important] | Dispatcher/event processing helpers.
- dispatcher/.gitignore | [file] | [important] | Dispatcher/event processing helpers.
- dispatcher/data/schemas/commands/applied_control/update_applied_control_v1.json | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/data/schemas/commands/evidence/upload_attachment_v1.json | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/data/schemas/commands/requirement_assessment/update_requirement_assessment_v1.json | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/dispatcher.py | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/Dockerfile | [file] | [critical] | Dispatcher/event processing helpers.
- dispatcher/entrypoint.sh | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/filtering.py | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/messages.py | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/pyproject.toml | [code/config] | [critical] | Dispatcher/event processing helpers.
- dispatcher/README.md | [doc] | [important] | Dispatcher/event processing helpers.
- dispatcher/samples/kafka/redpanda/redpanda.yaml | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/samples/kafka/redpanda-basic.yml | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/samples/kafka/redpanda-sasl.yml | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/samples/kafka/zk-single-kafka-single.yml | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/samples/messages/update_requirement_assessment.json | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/settings.py | [code/config] | [critical] | Dispatcher/event processing helpers.
- dispatcher/tests/__init__.py | [code/config] | [optional] | Dispatcher/event processing helpers.
- dispatcher/tests/integration/__init__.py | [code/config] | [optional] | Dispatcher/event processing helpers.
- dispatcher/tests/integration/test_messages.py | [code/config] | [optional] | Dispatcher/event processing helpers.
- dispatcher/utils/api.py | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/utils/kafka.py | [code/config] | [important] | Dispatcher/event processing helpers.
- dispatcher/uv.lock | [generated] | [generated/artifact] | Dispatcher/event processing helpers.

### docker-compose-build.sh
- docker-compose-build.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose-build.yml
- docker-compose-build.yml | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose.dev-frontend.yml
- docker-compose.dev-frontend.yml | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose.prod.yml
- docker-compose.prod.yml | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose.ps1
- docker-compose.ps1 | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose.sh
- docker-compose.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### docker-compose.yml
- docker-compose.yml | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### documentation
- documentation/architecture/data-model.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/architecture/event-streaming.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/architecture/outgoing-webhooks.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/assignment-workflow.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/createmodal-order.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/data_wizard_analysis.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/dora-roi-specification.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/functional_testing/architecture.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/functional_testing/hot-reloader.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/notification-system.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/01-technical-package.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/02-academic-package.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/03-practitioner-package.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/04-nda-template.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/05-one-page-overview.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/06-evaluation-scope.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/review-package/README.md | [doc] | [important] | Architecture and deployment documentation.
- documentation/sap.typ | [file] | [important] | Architecture and deployment documentation.
- documentation/system-architecture.png | [artifact] | [generated/artifact] | Architecture and deployment documentation.

### enterprise
- enterprise/backend/.gitignore | [file] | [important] | Enterprise overlay and packaging.
- enterprise/backend/__init__.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/Dockerfile | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/__init__.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/apps.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/migrations/0001_initial.py | [generated] | [generated/artifact] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/migrations/0002_clientsettings_show_images_unauthenticated_and_more.py | [generated] | [generated/artifact] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/migrations/0003_alter_clientsettings_favicon.py | [generated] | [generated/artifact] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/migrations/__init__.py | [generated] | [generated/artifact] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/models.py | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/permissions.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/serializers.py | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/settings.py | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/signals.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/urls.py | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/enterprise_core/views.py | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/manage.sh | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/backend/poetry.lock | [generated] | [generated/artifact] | Enterprise overlay and packaging.
- enterprise/backend/pyproject.toml | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/backend/README.md | [doc] | [important] | Enterprise overlay and packaging.
- enterprise/config/.gitignore | [file] | [important] | Enterprise overlay and packaging.
- enterprise/config/certificates.yaml | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/config/docker-compose.sh | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/config/gen_local_cert.sh | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/config/init-custom-ca-certificates.sh | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/config/make_config.py | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/config/requirements.txt | [doc] | [important] | Enterprise overlay and packaging.
- enterprise/config/templates/docker-compose-postgresql-caddy.yml.j2 | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/config/templates/docker-compose-postgresql-traefik.yml.j2 | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/config/templates/docker-compose-sqlite-caddy.yml.j2 | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/config/templates/docker-compose-sqlite-traefik.yml.j2 | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/docker-compose-build.yml | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/frontend/.gitignore | [file] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/.prettierignore | [file] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/.prettierrc | [file] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/Dockerfile | [file] | [critical] | Enterprise overlay and packaging.
- enterprise/frontend/Makefile | [file] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/README.md | [doc] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/assets/ciso.svg | [file] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/components/Forms/ModelForm/EbiosRmForm.svelte | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/components/Forms/ModelForm/FolderForm.svelte | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/components/Logo/Logo.svelte | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/components/SideBar/navData.ts | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/lib/utils/client-settings.ts | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/+page.server.ts | [code/config] | [critical] | [route /audit-log] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/+page.svelte | [code/config] | [critical] | [route /audit-log] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/+server.ts | [code/config] | [important] | [route /audit-log] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/+page.server.ts | [code/config] | [critical] | [route /audit-log/[id]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/+page.svelte | [code/config] | [critical] | [route /audit-log/[id]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/components/LogEntryChange.svelte | [code/config] | [important] | [route /audit-log/[id]/components] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/components/M2MAdd.svelte | [code/config] | [important] | [route /audit-log/[id]/components] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/audit-log/[id]/components/RecursiveLogEntryChanges.svelte | [code/config] | [important] | [route /audit-log/[id]/components] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/campaigns/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /campaigns/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/campaigns/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /campaigns/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/+page.server.ts | [code/config] | [critical] | [route /domain-analytics] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/+page.svelte | [code/config] | [critical] | [route /domain-analytics] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/details/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /domain-analytics/details/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/details/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /domain-analytics/details/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/domain-analytics/TreeView.svelte | [code/config] | [important] | [route /domain-analytics] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/extra/data-wizard/+layout.svelte | [code/config] | [critical] | [route /extra/data-wizard] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/extra/data-wizard/+page.server.ts | [code/config] | [critical] | [route /extra/data-wizard] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/extra/data-wizard/+page.svelte | [code/config] | [critical] | [route /extra/data-wizard] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/folders/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /folders/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/folders/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /folders/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/folders/[id=uuid]/export/+server.ts | [code/config] | [important] | [route /folders/[id=uuid]/export] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/TreeViewItemContent.svelte | [code/config] | [important] | [route /frameworks/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/frameworks/inspect-requirement/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /frameworks/inspect-requirement/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/frameworks/inspect-requirement/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /frameworks/inspect-requirement/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/impact-analysis/+page.server.ts | [code/config] | [critical] | [route /insights/impact-analysis] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/impact-analysis/+page.svelte | [code/config] | [critical] | [route /insights/impact-analysis] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/priority-review/+layout.svelte | [code/config] | [critical] | [route /insights/priority-review] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/priority-review/+page.server.ts | [code/config] | [critical] | [route /insights/priority-review] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/priority-review/+page.svelte | [code/config] | [critical] | [route /insights/priority-review] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/priority-review/ImpactEffortMatrix.svelte | [code/config] | [important] | [route /insights/priority-review] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/timeline-view/+layout.svelte | [code/config] | [critical] | [route /insights/timeline-view] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/timeline-view/+page.server.ts | [code/config] | [critical] | [route /insights/timeline-view] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/insights/timeline-view/+page.svelte | [code/config] | [critical] | [route /insights/timeline-view] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/my-assignments/+page.server.ts | [code/config] | [critical] | [route /my-assignments] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/my-assignments/+page.svelte | [code/config] | [critical] | [route /my-assignments] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/+page.svelte | [code/config] | [critical] | [route /settings] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/+page.server.ts | [code/config] | [critical] | [route /settings/client-settings] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/+page.svelte | [code/config] | [critical] | [route /settings/client-settings] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/+server.ts | [code/config] | [important] | [route /settings/client-settings] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/favicon/+server.ts | [code/config] | [important] | [route /settings/client-settings/favicon] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/client-settings/logo/+server.ts | [code/config] | [important] | [route /settings/client-settings/logo] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/[field=integration_field]/+server.ts | [code/config] | [important] | [route /settings/integrations/[field=integration_field]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/configs/[id=uuid]/remote-objects/+server.ts | [code/config] | [important] | [route /settings/integrations/configs/[id=uuid]/remote-objects] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/configs/[id=uuid]/rpc/+server.ts | [code/config] | [important] | [route /settings/integrations/configs/[id=uuid]/rpc] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/jira/+page.server.ts | [code/config] | [critical] | [route /settings/integrations/jira] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/jira/+page.svelte | [code/config] | [critical] | [route /settings/integrations/jira] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/servicenow/+page.server.ts | [code/config] | [critical] | [route /settings/integrations/servicenow] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/servicenow/+page.svelte | [code/config] | [critical] | [route /settings/integrations/servicenow] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/integrations/test-connection/+server.ts | [code/config] | [important] | [route /settings/integrations/test-connection] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/constants.ts | [code/config] | [important] | [route /settings/webhooks/endpoints] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/workflow-cases/+page.server.ts | [code/config] | [critical] | [route /workflow-cases] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/workflow-cases/+page.svelte | [code/config] | [critical] | [route /workflow-cases] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/workflow-cases/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /workflow-cases/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/(internal)/workflow-cases/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /workflow-cases/[id=uuid]] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/+layout.server.ts | [code/config] | [critical] | [route /] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(app)/+layout.svelte | [code/config] | [critical] | [route /] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(authentication)/login/+page.svelte | [code/config] | [critical] | [route /login] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/(authentication)/login/Greetings.svelte | [code/config] | [important] | [route /login] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/+layout.server.ts | [code/config] | [critical] | [route /] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/+layout.svelte | [code/config] | [critical] | [route /] | Enterprise overlay and packaging.
- enterprise/frontend/src/routes/favicon/+server.ts | [code/config] | [important] | [route /favicon] | Enterprise overlay and packaging.
- enterprise/legacy/docker-compose-build.sh | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/legacy/docker-compose-pg.yml | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/legacy/docker-compose-remote-api.yml | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/legacy/docker-compose-remote.yml | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/legacy/docker-compose.sh | [code/config] | [critical] | Enterprise overlay and packaging.
- enterprise/legacy/update-ciso-assistant-enterprise.sh | [code/config] | [important] | Enterprise overlay and packaging.
- enterprise/LICENSE.md | [doc] | [important] | Enterprise overlay and packaging.
- enterprise/offline-deployment.md | [doc] | [important] | Enterprise overlay and packaging.
- enterprise/README.md | [doc] | [important] | Enterprise overlay and packaging.

### features.png
- features.png | [artifact] | [generated/artifact] | Binary asset or data artifact.

### fill_ar_pass2.py
- fill_ar_pass2.py | [code/config] | [important] | Supporting project file.

### fill_ar_pass3.py
- fill_ar_pass3.py | [code/config] | [important] | Supporting project file.

### fill_ar_pass4.py
- fill_ar_pass4.py | [code/config] | [important] | Supporting project file.

### fill_ar_translations.py
- fill_ar_translations.py | [code/config] | [important] | Supporting project file.

### fix-favicon.js
- fix-favicon.js | [code/config] | [important] | Supporting project file.

### fix-logo-shield.js
- fix-logo-shield.js | [code/config] | [important] | Supporting project file.

### fix-logo.js
- fix-logo.js | [code/config] | [important] | Supporting project file.

### frameworks_summary.csv
- frameworks_summary.csv | [file] | [important] | Supporting project file.

### frontend
- frontend/.dockerignore | [file] | [important] | Primary SvelteKit frontend.
- frontend/.eslintrc.cjs | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/.gitignore | [file] | [important] | Primary SvelteKit frontend.
- frontend/.npmrc | [file] | [important] | Primary SvelteKit frontend.
- frontend/.prettierignore | [file] | [important] | Primary SvelteKit frontend.
- frontend/.prettierrc | [file] | [important] | Primary SvelteKit frontend.
- frontend/Caddyfile | [file] | [important] | Primary SvelteKit frontend.
- frontend/Caddyfile-sso | [file] | [important] | Primary SvelteKit frontend.
- frontend/ciso-theme.css | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/Dockerfile | [file] | [critical] | Primary SvelteKit frontend.
- frontend/eslint.config.mjs | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/ar.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/cs.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/da.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/de.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/el.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/en.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/es.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/fr.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/hi.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/hr.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/hu.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/id.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/it.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/lt.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/nl.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/pl.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/pt.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/ro.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/sv.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/tr.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/uk.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/ur.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/messages/zh.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/package-lock.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/package.json | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/playwright.config.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit/index.js | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit/package.json | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit/pnpm-lock.yaml | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit/secure-redirect.js | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/plugins/eslint/eslint-plugin-intuitem-sveltekit/secure-redirect.test.js | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/pnpm-lock.yaml | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/project.inlang/.gitignore | [file] | [important] | Primary SvelteKit frontend.
- frontend/project.inlang/project_id | [file] | [important] | Primary SvelteKit frontend.
- frontend/project.inlang/settings.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/README.md | [doc] | [important] | Primary SvelteKit frontend.
- frontend/server/index.js | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/app.css | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/app.d.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/app.html | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/hooks.client.ts | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/src/hooks.server.ts | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/src/lib/allauth.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/assets/ciso.svg | [file] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/assets/favicon.ico | [artifact] | [generated/artifact] | Primary SvelteKit frontend.
- frontend/src/lib/assets/sico-logo.svg | [file] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Anchor/Anchor.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Assets/AssetDependencyGraph.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Assets/ObjectivesComparisonTable.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/BIA/TimelineTable.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Breadcrumbs/Breadcrumbs.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Calendar/Calendar.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Calendar/Day.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/ALEComparisonChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/ALETimelineRaceChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/BarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/CalendarHeatmap.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/ComparisonRadarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/DashboardWidgetChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/DonutChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/EcosystemCircularRadarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/EcosystemRadarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/ExceptionSankeyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/FindingsSankeyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/GDPRSankeyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/GroupedBarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/HalfDonutChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/IncidentMonthlyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/LognormalDistribution.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/LossExceedanceCurve.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/MetricSampleChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/NightingaleChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/PriorityRadarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/RadarChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/SankeyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/StackedBarsNormalized.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/SunburstChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/TimeSeriesChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/TreeChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/TreemapChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/VulnerabilitySankeyChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Chart/WaterfallChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/CommandPalette/CommandPalette.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/CommandPalette/paletteData.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/CommentsPanel/CommentsPanel.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/applied-controls/ChangeCsfFunction.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/applied-controls/ChangeEffort.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/applied-controls/ChangeImpact.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/applied-controls/ChangePriority.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/applied-controls/ChangeStatus.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/ebios-rm/SelectObject.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/elementary-actions/ChangeAttackStage.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/evidences/ChangeStatus.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ContextMenu/task-nodes/ChangeStatus.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/ActivityTracker.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/Article.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/Card.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/CardGroup.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/ForceCirclePacking.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/GraphExplorer.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/LineHeatmap.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/RingProgress.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/SimpleCard.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DataViz/WorldMap.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/DetailView/DetailView.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Dropdown/Dropdown.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/EbiosRM/AttackPathFlowText.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/EbiosRM/AttackPathGraph.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/FocusMode/FocusModeSelector.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/FocusMode/FolderTreeNode.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/AutocompleteSelect.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/BackgroundCheckbox.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Checkbox.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Duration.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/FieldMapper.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/FileInput.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Form.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/HiddenInput.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/LegalIdentifierField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ListSelector.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/MarkdownField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/AccreditationForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/AppliedControlPolicyForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/AssetAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/AssetForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/AttackPathForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/BusinessImpactAnalysisForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/CampaignForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ComplianceAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ContractForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/CustomMetricSampleForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DashboardBuiltinWidgetForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DashboardForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DashboardTextWidgetForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DashboardWidgetForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DataBreachForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DataContractorForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DataRecipientForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DataSubjectForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/DataTransferForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EbiosRmForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ElementaryActionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EntityAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EntityForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EscalationThresholdForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EvidenceForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/EvidenceRevisionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FearedEventForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FeatureFlagsSettingForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FilteringLabelForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FindingForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FindingsAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FolderForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/FrameworkForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/GeneralSettingForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/GenericCollectionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/IncidentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/KillChainForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/MetricDefinitionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/MetricInstanceForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/OperatingModeForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/OperationalScenarioForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/OrganisationIssueForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/OrganisationObjectiveForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/PerimeterForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/PersonalDataForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ProcessingForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/PurposeForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/QuantitativeRiskHypothesisForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/QuantitativeRiskScenarioForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/QuantitativeRiskStudyForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ReferenceControlForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RepresentativeForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RequirementAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RightRequestForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RiskAcceptanceForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RiskAssessmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RiskScenarioForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RoleAssignmentForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RoleForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/RoToForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/SecurityExceptionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/SolutionForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/SsoSettingForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/StakeholderForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/StrategicScenarioForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/TaskNodeForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/TaskTemplateForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/TeamForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/TerminologyForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ThreatForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/TimelineEntryForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/UserForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/ValidationFlowForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm/VulnerabilitiesForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/ModelForm.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/NumberField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/OTP/OTPInput.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/OTP/OTPItem.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Question.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/RadioGroup.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Score.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/Select.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/TableMarkdownField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/TextArea.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/TextField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/TranslationField.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Forms/WebhookSecretGenerator.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/FrameworkEquivalence/FrameworlEquivalence.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/FrameworkMappingsChart/FrameworkMappingsChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/GanttChart.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/GanttView/MyGantt.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/List/List.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Logo/Logo.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/MarkdownRenderer.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/ApplyPresetModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/BatchActionModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/ChoicesModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/CompareAuditModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/ConfirmModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/CreateModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/DeleteConfirmModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/DisplayJSONModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/ExternalLinkConfirmModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/FirstLoginModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/Modal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/ProblematicScenariosModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/PromptConfirmModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/SelectExistingModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/stores.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/SyncToActionsRiskModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/UpdateModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Modals/UploadLibraryModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/actions.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/BatchActionBar.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/EvidenceFilePreview.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/FrameworkName.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/LanguageDisplay.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/LecChartPreview.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/LibraryActions.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/LibraryOverview.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/MarkdownDescription.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/field/UserGroupNameDisplay.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/handler.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/ModelTable.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/Pagination.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/RowCount.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/RowsPerPage.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/Search.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/Th.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/ThFilter.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ModelTable/types.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Notifications/NotificationBell.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/OrderedEntryList.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/Cell.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/Legend.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/RiskMatrix.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/RiskScenarioItem.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/utils.test.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/RiskMatrix/utils.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Settings/FeatureFlagsSettings.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Settings/GeneralSettings.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Settings/SSOSettings.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Settings/WebhooksSettings.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/driver-custom.css | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/navData.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/QuickStart/QuickStartModal.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBar.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarCategory.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarFooter.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarHeader.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarItem.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarNavigation.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/SideBar/SideBarToggle.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Snippets/AutocompleteSelect/FrameworkResultSnippet.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TableOfContents/TableOfContents.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TableRowActions/TableRowActions.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Toast/stores.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/Toast/Toast.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TreeView/RecursiveTreeView.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TreeView/RecursiveTreeViewItem.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TreeView/TreeView.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TreeView/TreeViewItem.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/TreeView/types.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/utils/LoadingSpinner.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/utils/transitions.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/components/ValidationFlows/ValidationFlowsSection.svelte | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/django.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/feature-flags.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/access-control.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/actions.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/breadcrumbs.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/constants.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/cookies.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/crud.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/csrf.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/datetime.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/external-links.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/helpers.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/i18n.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/load.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/locales.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/related-visibility.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/schemas.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/sidebar-config.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/stores.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/table.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/toc.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/types.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/lib/utils/webhooks.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/fields.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/filters.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/integration_field.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/lang.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/thirdparty_urlmodels.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/urlmodel.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/urn.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/params/uuid.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/+layout.server.ts | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/+layout.server.ts | [code/config] | [critical] | [route /[model=urlmodel]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/+page.server.ts | [code/config] | [critical] | [route /[model=urlmodel]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/+page.svelte | [code/config] | [critical] | [route /[model=urlmodel]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/+server.ts | [code/config] | [important] | [route /[model=urlmodel]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[filter=filters]/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/[filter=filters]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/[field=fields]/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/[id=uuid]/[field=fields]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/edit/+layout.server.ts | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/edit/+layout.svelte | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /[model=urlmodel]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/batch-action/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/batch-action] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/export/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/export] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/[model=urlmodel]/export/xlsx/+server.ts | [code/config] | [important] | [route /[model=urlmodel]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/accreditations/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /accreditations/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/accreditations/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /accreditations/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/actors/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /actors/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/actors/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /actors/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/+layout.svelte | [code/config] | [critical] | [route /analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/+page.server.ts | [code/config] | [critical] | [route /analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/+page.svelte | [code/config] | [critical] | [route /analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/composer/+page.server.ts | [code/config] | [critical] | [route /analytics/composer] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/composer/+page.svelte | [code/config] | [critical] | [route /analytics/composer] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/ComposerSelect.svelte | [code/config] | [important] | [route /analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/CounterCard.svelte | [code/config] | [important] | [route /analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/gdpr/+page.server.ts | [code/config] | [critical] | [route /analytics/gdpr] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/gdpr/+page.svelte | [code/config] | [critical] | [route /analytics/gdpr] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/gdpr/Card.svelte | [code/config] | [important] | [route /analytics/gdpr] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/tprm/+layout.svelte | [code/config] | [critical] | [route /analytics/tprm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/tprm/+page.server.ts | [code/config] | [critical] | [route /analytics/tprm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/tprm/+page.svelte | [code/config] | [critical] | [route /analytics/tprm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/analytics/tprm/FlippableCard.svelte | [code/config] | [important] | [route /analytics/tprm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/applied-controls/flash-mode/+page.server.ts | [code/config] | [critical] | [route /applied-controls/flash-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/applied-controls/flash-mode/+page.svelte | [code/config] | [critical] | [route /applied-controls/flash-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/applied-controls/kanban-mode/+page.server.ts | [code/config] | [critical] | [route /applied-controls/kanban-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/applied-controls/kanban-mode/+page.svelte | [code/config] | [critical] | [route /applied-controls/kanban-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /asset-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /asset-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /asset-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /asset-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/dependencies/+page.server.ts | [code/config] | [critical] | [route /asset-assessments/[id=uuid]/dependencies] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/asset-assessments/[id=uuid]/dependencies/+page.svelte | [code/config] | [critical] | [route /asset-assessments/[id=uuid]/dependencies] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/[id=uuid]/+layout.server.ts | [code/config] | [critical] | [route /assets/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /assets/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/[id=uuid]/+server.ts | [code/config] | [important] | [route /assets/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/autocomplete/+server.ts | [code/config] | [important] | [route /assets/autocomplete] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/graph/+page.server.ts | [code/config] | [critical] | [route /assets/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/assets/graph/+page.svelte | [code/config] | [critical] | [route /assets/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/backup-restore/+layout.svelte | [code/config] | [critical] | [route /backup-restore] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/backup-restore/+page.server.ts | [code/config] | [critical] | [route /backup-restore] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/backup-restore/+page.svelte | [code/config] | [critical] | [route /backup-restore] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/backup-restore/dump-db/+server.ts | [code/config] | [important] | [route /backup-restore/dump-db] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/export/xlsx/+server.ts | [code/config] | [important] | [route /business-impact-analysis/[id=uuid]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/report/+page.server.ts | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/report] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/report/+page.svelte | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/report] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/visual/+page.server.ts | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/visual] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/business-impact-analysis/[id=uuid]/visual/+page.svelte | [code/config] | [critical] | [route /business-impact-analysis/[id=uuid]/visual] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/calendar/+page.server.ts | [code/config] | [critical] | [route /calendar] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/calendar/[year]/[month]/+page.server.ts | [code/config] | [critical] | [route /calendar/[year]/[month]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/calendar/[year]/[month]/+page.svelte | [code/config] | [critical] | [route /calendar/[year]/[month]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/csv/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/action-plan/export/csv] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/pdf/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/action-plan/export/pdf] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/action-plan/export/xlsx/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/action-plan/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/advanced-analytics/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/advanced-analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/advanced-analytics/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/advanced-analytics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/comparable_audits/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/comparable_audits] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/evidences-list/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/evidences-list] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/evidences-list/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/evidences-list] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/evidences-list/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/evidences-list] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/export] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/csv/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/export/csv] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/word/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/export/word] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/export/xlsx/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/flash-mode/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/flash-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/[id=uuid]/flash-mode/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/flash-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/compare/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/compare] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/compliance-assessments/compare/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/compare] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/content-types/+server.ts | [code/config] | [important] | [route /content-types] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/contracts/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /contracts/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/contracts/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /contracts/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /dashboards/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /dashboards/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]/layout/+page.server.ts | [code/config] | [critical] | [route /dashboards/[id=uuid]/layout] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/dashboards/[id=uuid]/layout/+page.svelte | [code/config] | [critical] | [route /dashboards/[id=uuid]/layout] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/+page.server.ts | [code/config] | [critical] | [route /ebios-rm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/+page.svelte | [code/config] | [critical] | [route /ebios-rm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/+server.ts | [code/config] | [important] | [route /ebios-rm] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/+layout.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/+server.ts | [code/config] | [important] | [route /ebios-rm/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/export/xlsx/+server.ts | [code/config] | [important] | [route /ebios-rm/[id=uuid]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/report/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/report] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/report/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/report] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/Tile.svelte | [code/config] | [important] | [route /ebios-rm/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/visual/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/visual] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/visual/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/visual] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/baseline/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/baseline] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/baseline/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/baseline] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/ebios-rm-study] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/ebios-rm-study] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/edit/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/edit/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/ebios-rm-study/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/feared-events/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/feared-events] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-1/feared-events/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-1/feared-events] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-2/ro-to/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-2/ro-to] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-2/ro-to/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-2/ro-to] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/ecosystem/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-3/ecosystem] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/ecosystem/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-3/ecosystem] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/strategic-scenarios/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-3/strategic-scenarios] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-3/strategic-scenarios/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-3/strategic-scenarios] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/elementary-actions/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-4/elementary-actions] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/elementary-actions/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-4/elementary-actions] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/operational-scenario/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-4/operational-scenario] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-4/operational-scenario/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-4/operational-scenario] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-5/risk-analyses/+page.server.ts | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-5/risk-analyses] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/[id=uuid]/workshop-5/risk-analyses/+page.svelte | [code/config] | [critical] | [route /ebios-rm/[id=uuid]/workshop-5/risk-analyses] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ebios-rm/batch-action/+server.ts | [code/config] | [important] | [route /ebios-rm/batch-action] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/entities/graph/+page.server.ts | [code/config] | [critical] | [route /entities/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/entities/graph/+page.svelte | [code/config] | [critical] | [route /entities/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/entity-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /entity-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/entity-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /entity-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/+layout.svelte | [code/config] | [critical] | [route /experimental] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/+page.svelte | [code/config] | [critical] | [route /experimental] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/batch-create/+page.server.ts | [code/config] | [critical] | [route /experimental/batch-create] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/batch-create/+page.svelte | [code/config] | [critical] | [route /experimental/batch-create] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/calendar-activity/+page.svelte | [code/config] | [critical] | [route /experimental/calendar-activity] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/circle-packing/+page.svelte | [code/config] | [critical] | [route /experimental/circle-packing] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/ecosystem/+page.server.ts | [code/config] | [critical] | [route /experimental/ecosystem] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/ecosystem/+page.svelte | [code/config] | [critical] | [route /experimental/ecosystem] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/graph/+page.server.ts | [code/config] | [critical] | [route /experimental/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/graph/+page.svelte | [code/config] | [critical] | [route /experimental/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/loss-exceedance/+page.svelte | [code/config] | [critical] | [route /experimental/loss-exceedance] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/mapping/+page.server.ts | [code/config] | [critical] | [route /experimental/mapping] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/mapping/+page.svelte | [code/config] | [critical] | [route /experimental/mapping] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/mapping/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /experimental/mapping/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/mapping/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /experimental/mapping/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/ordered-list/+page.svelte | [code/config] | [critical] | [route /experimental/ordered-list] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/timeseries/+page.svelte | [code/config] | [critical] | [route /experimental/timeseries] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/yearly-tasks-review/+page.server.ts | [code/config] | [critical] | [route /experimental/yearly-tasks-review] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/experimental/yearly-tasks-review/+page.svelte | [code/config] | [critical] | [route /experimental/yearly-tasks-review] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /findings-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /findings-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/+server.ts | [code/config] | [important] | [route /findings-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /findings-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /findings-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/md/+server.ts | [code/config] | [important] | [route /findings-assessments/[id=uuid]/export/md] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/pdf/+server.ts | [code/config] | [important] | [route /findings-assessments/[id=uuid]/export/pdf] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/findings-assessments/[id=uuid]/export/xlsx/+server.ts | [code/config] | [important] | [route /findings-assessments/[id=uuid]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/folders/import-dummy/+server.ts | [code/config] | [important] | [route /folders/import-dummy] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /frameworks/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /frameworks/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/+server.ts | [code/config] | [important] | [route /frameworks/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/excel-template/+server.ts | [code/config] | [important] | [route /frameworks/[id=uuid]/excel-template] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/TreeViewItemContent.svelte | [code/config] | [important] | [route /frameworks/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/frameworks/[id=uuid]/TreeViewItemLead.svelte | [code/config] | [important] | [route /frameworks/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/generic-collections/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /generic-collections/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/generic-collections/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /generic-collections/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /incidents/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /incidents/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/export/md/+server.ts | [code/config] | [important] | [route /incidents/[id=uuid]/export/md] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/incidents/[id=uuid]/export/pdf/+server.ts | [code/config] | [important] | [route /incidents/[id=uuid]/export/pdf] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/libraries/+page.server.ts | [code/config] | [critical] | [route /libraries] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/libraries/+page.svelte | [code/config] | [critical] | [route /libraries] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/license-management/+page.server.ts | [code/config] | [critical] | [route /license-management] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/license-management/+page.svelte | [code/config] | [critical] | [route /license-management] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /loaded-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /loaded-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/+page.ts | [code/config] | [important] | [route /loaded-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/+server.ts | [code/config] | [important] | [route /loaded-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/tree/+server.ts | [code/config] | [important] | [route /loaded-libraries/[id=uuid]/tree] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/loaded-libraries/[id=uuid]/TreeViewItemContent.svelte | [code/config] | [important] | [route /loaded-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/mapping-libraries/+server.ts | [code/config] | [important] | [route /mapping-libraries] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/metric-instances/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /metric-instances/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/metric-instances/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /metric-instances/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-assignments/+layout.svelte | [code/config] | [critical] | [route /my-assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-assignments/+page.server.ts | [code/config] | [critical] | [route /my-assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-assignments/+page.svelte | [code/config] | [critical] | [route /my-assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-assignments/AuditCard.svelte | [code/config] | [important] | [route /my-assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-assignments/HalfGauge.svelte | [code/config] | [important] | [route /my-assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/+page.server.ts | [code/config] | [critical] | [route /my-profile] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/+page.svelte | [code/config] | [critical] | [route /my-profile] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/change-password/+page.server.ts | [code/config] | [critical] | [route /my-profile/change-password] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/change-password/+page.svelte | [code/config] | [critical] | [route /my-profile/change-password] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/+layout.svelte | [code/config] | [critical] | [route /my-profile/settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/+page.server.ts | [code/config] | [critical] | [route /my-profile/settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/+page.svelte | [code/config] | [critical] | [route /my-profile/settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/components/ActivateTOTPModal.svelte | [code/config] | [important] | [route /my-profile/settings/mfa/components] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/components/ListRecoveryCodesModal.svelte | [code/config] | [important] | [route /my-profile/settings/mfa/components] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/utils/schemas.ts | [code/config] | [important] | [route /my-profile/settings/mfa/utils] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/mfa/utils/stores.ts | [code/config] | [important] | [route /my-profile/settings/mfa/utils] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/my-profile/settings/pat/components/CreatePATModal.svelte | [code/config] | [important] | [route /my-profile/settings/pat/components] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /operating-modes/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /operating-modes/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/+server.ts | [code/config] | [important] | [route /operating-modes/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/edges/LogicEdge.svelte | [code/config] | [important] | [route /operating-modes/[id=uuid]/graph/edges] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/EditorSidebar.svelte | [code/config] | [important] | [route /operating-modes/[id=uuid]/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/nodes/ActionNode.svelte | [code/config] | [important] | [route /operating-modes/[id=uuid]/graph/nodes] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/nodes/StageColumnNode.svelte | [code/config] | [important] | [route /operating-modes/[id=uuid]/graph/nodes] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/[id=uuid]/graph/OperatingModeGraph.svelte | [code/config] | [important] | [route /operating-modes/[id=uuid]/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operating-modes/default-ref-id/+server.ts | [code/config] | [important] | [route /operating-modes/default-ref-id] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operational-scenarios/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /operational-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/operational-scenarios/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /operational-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/policies/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /policies/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/policies/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /policies/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/policies/[id=uuid]/+server.ts | [code/config] | [important] | [route /policies/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /preset-journeys/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /preset-journeys/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/+server.ts | [code/config] | [important] | [route /preset-journeys/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/rename/+server.ts | [code/config] | [important] | [route /preset-journeys/[id=uuid]/rename] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/step/[stepId=uuid]/+server.ts | [code/config] | [important] | [route /preset-journeys/[id=uuid]/step/[stepId=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/preset-journeys/[id=uuid]/upgrade/+server.ts | [code/config] | [important] | [route /preset-journeys/[id=uuid]/upgrade] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/presets/+page.server.ts | [code/config] | [critical] | [route /presets] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/presets/+page.svelte | [code/config] | [critical] | [route /presets] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/presets/apply/+server.ts | [code/config] | [important] | [route /presets/apply] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/processings/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /processings/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/processings/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /processings/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/processings/[id=uuid]/+server.ts | [code/config] | [important] | [route /processings/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-hypotheses/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-hypotheses/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-hypotheses/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-hypotheses/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-scenarios/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-scenarios/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/action-plan/+server.ts | [code/config] | [important] | [route /quantitative-risk-studies/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/executive-summary/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/executive-summary] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/executive-summary/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/executive-summary] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/key-metrics/+page.server.ts | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/key-metrics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quantitative-risk-studies/[id=uuid]/key-metrics/+page.svelte | [code/config] | [critical] | [route /quantitative-risk-studies/[id=uuid]/key-metrics] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/quick-start/+page.server.ts | [code/config] | [critical] | [route /quick-start] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/recap/+layout.svelte | [code/config] | [critical] | [route /recap] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/recap/+page.server.ts | [code/config] | [critical] | [route /recap] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/recap/+page.svelte | [code/config] | [critical] | [route /recap] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/registration-requests/+page.server.ts | [code/config] | [critical] | [route /registration-requests] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/registration-requests/+page.svelte | [code/config] | [critical] | [route /registration-requests] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/+page.server.ts | [code/config] | [critical] | [route /reports] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/+page.svelte | [code/config] | [critical] | [route /reports] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/dora-roi/+page.server.ts | [code/config] | [critical] | [route /reports/dora-roi] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/dora-roi/+page.svelte | [code/config] | [critical] | [route /reports/dora-roi] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/dora-roi/download/+server.ts | [code/config] | [important] | [route /reports/dora-roi/download] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/reports/ReportTile.svelte | [code/config] | [important] | [route /reports] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/requirement-assessments/[id=uuid]/suggestions/applied-controls/+server.ts | [code/config] | [important] | [route /requirement-assessments/[id=uuid]/suggestions/applied-controls] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/requirement-mapping-sets/graph/+page.server.ts | [code/config] | [critical] | [route /requirement-mapping-sets/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/requirement-mapping-sets/graph/+page.svelte | [code/config] | [critical] | [route /requirement-mapping-sets/graph] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/+layout.server.ts | [code/config] | [critical] | [route /risk-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /risk-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /risk-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/+page.server.ts | [code/config] | [critical] | [route /risk-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/+page.svelte | [code/config] | [critical] | [route /risk-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/action-plan] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/export/excel/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/action-plan/export/excel] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/action-plan/export/pdf/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/action-plan/export/pdf] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/convert-to-quantitative/+page.server.ts | [code/config] | [critical] | [route /risk-assessments/[id=uuid]/convert-to-quantitative] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/convert-to-quantitative/+page.svelte | [code/config] | [critical] | [route /risk-assessments/[id=uuid]/convert-to-quantitative] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/csv/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/export/csv] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/pdf/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/export/pdf] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/export/xlsx/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/export/xlsx] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-assessments/[id=uuid]/sync-to-actions/+server.ts | [code/config] | [important] | [route /risk-assessments/[id=uuid]/sync-to-actions] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-matrices/[id=uuid]/+layout.server.ts | [code/config] | [critical] | [route /risk-matrices/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-matrices/[id=uuid]/+layout.svelte | [code/config] | [critical] | [route /risk-matrices/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-matrices/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /risk-matrices/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-matrices/[id=uuid]/+server.ts | [code/config] | [important] | [route /risk-matrices/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /risk-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /risk-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /risk-scenarios/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /risk-scenarios/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/edit/RiskLevel.svelte | [code/config] | [important] | [route /risk-scenarios/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/[id=uuid]/sync-to-actions/+server.ts | [code/config] | [important] | [route /risk-scenarios/[id=uuid]/sync-to-actions] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/risk-scenarios/default-ref-id/+server.ts | [code/config] | [important] | [route /risk-scenarios/default-ref-id] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /ro-to/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /ro-to/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /ro-to/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/ro-to/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /ro-to/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/scoring-assistant/+page.server.ts | [code/config] | [critical] | [route /scoring-assistant] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/scoring-assistant/+page.svelte | [code/config] | [critical] | [route /scoring-assistant] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/scoring-assistant/selector.svelte | [code/config] | [important] | [route /scoring-assistant] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/scoring-assistant/utils.ts | [code/config] | [important] | [route /scoring-assistant] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/security-exceptions/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /security-exceptions/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/security-exceptions/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /security-exceptions/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/security-exceptions/[id=uuid]/+server.ts | [code/config] | [important] | [route /security-exceptions/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/+layout.svelte | [code/config] | [critical] | [route /settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/+page.server.ts | [code/config] | [critical] | [route /settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/+page.svelte | [code/config] | [critical] | [route /settings] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/saml/download-cert/+server.ts | [code/config] | [important] | [route /settings/saml/download-cert] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/+layout.server.ts | [code/config] | [critical] | [route /settings/webhooks] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /settings/webhooks/endpoints/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /settings/webhooks/endpoints/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/constants.ts | [code/config] | [important] | [route /settings/webhooks/endpoints] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/endpoints/WebhookEndpointCreateModal.svelte | [code/config] | [important] | [route /settings/webhooks/endpoints] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/settings/webhooks/event-types/+server.ts | [code/config] | [important] | [route /settings/webhooks/event-types] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stakeholders/[id=uuid]/edit/+layout.svelte | [code/config] | [critical] | [route /stakeholders/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stakeholders/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /stakeholders/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stakeholders/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /stakeholders/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /stored-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /stored-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/+page.ts | [code/config] | [important] | [route /stored-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/+server.ts | [code/config] | [important] | [route /stored-libraries/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/stored-libraries/[id=uuid]/tree/+server.ts | [code/config] | [important] | [route /stored-libraries/[id=uuid]/tree] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/strategic-scenarios/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /strategic-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/strategic-scenarios/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /strategic-scenarios/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/sync-mappings/[id=uuid]/+server.ts | [code/config] | [important] | [route /sync-mappings/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/task-nodes/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /task-nodes/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/task-nodes/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /task-nodes/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/task-templates/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /task-templates/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/task-templates/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /task-templates/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /users/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /users/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit/set-password/+page.server.ts | [code/config] | [critical] | [route /users/[id=uuid]/edit/set-password] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/users/[id=uuid]/edit/set-password/+page.svelte | [code/config] | [critical] | [route /users/[id=uuid]/edit/set-password] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/validation-flows/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /validation-flows/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/validation-flows/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /validation-flows/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/vulnerabilities/treemap/+page.server.ts | [code/config] | [critical] | [route /vulnerabilities/treemap] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/vulnerabilities/treemap/+page.svelte | [code/config] | [critical] | [route /vulnerabilities/treemap] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/workflow-cases/+page.server.ts | [code/config] | [critical] | [route /workflow-cases] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/workflow-cases/+page.svelte | [code/config] | [critical] | [route /workflow-cases] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/x-rays/+page.server.ts | [code/config] | [critical] | [route /x-rays] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/x-rays/+page.svelte | [code/config] | [critical] | [route /x-rays] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/x-rays/inspect/+layout.svelte | [code/config] | [critical] | [route /x-rays/inspect] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/x-rays/inspect/+page.server.ts | [code/config] | [critical] | [route /x-rays/inspect] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(internal)/x-rays/inspect/+page.svelte | [code/config] | [critical] | [route /x-rays/inspect] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/+layout.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/+page.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/+page.svelte | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/+server.ts | [code/config] | [important] | [route /[model=thirdparty_urlmodels]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/+layout.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/+server.ts | [code/config] | [important] | [route /[model=thirdparty_urlmodels]/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/edit/+layout.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/[model=thirdparty_urlmodels]/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /[model=thirdparty_urlmodels]/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/auditee-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /auditee-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/auditee-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /auditee-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/auditee-dashboard/+page.server.ts | [code/config] | [critical] | [route /auditee-dashboard] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/auditee-dashboard/+page.svelte | [code/config] | [critical] | [route /auditee-dashboard] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/assignments/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/assignments/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/assignments/TreeViewItemContentSimple.svelte | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/assignments/TreeViewItemLeadSimple.svelte | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/assignments] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/suggestions/applied-controls/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/suggestions/applied-controls] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/sync-to-actions/+server.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]/sync-to-actions] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/table-mode/+page.server.ts | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/table-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/table-mode/+page.svelte | [code/config] | [critical] | [route /compliance-assessments/[id=uuid]/table-mode] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/TreeViewItemContent.svelte | [code/config] | [important] | [route /compliance-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/TreeViewItemLead.svelte | [code/config] | [important] | [route /compliance-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/compliance-assessments/[id=uuid]/types.ts | [code/config] | [important] | [route /compliance-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidence-revisions/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /evidence-revisions/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidence-revisions/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /evidence-revisions/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidence-revisions/[id=uuid]/attachment/+server.ts | [code/config] | [important] | [route /evidence-revisions/[id=uuid]/attachment] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidences/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /evidences/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidences/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /evidences/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/evidences/[id=uuid]/attachment/+server.ts | [code/config] | [important] | [route /evidences/[id=uuid]/attachment] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/+page.server.ts | [code/config] | [critical] | [route /requirement-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/+page.svelte | [code/config] | [critical] | [route /requirement-assessments/[id=uuid]] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/edit/+layout.svelte | [code/config] | [critical] | [route /requirement-assessments/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/edit/+page.server.ts | [code/config] | [critical] | [route /requirement-assessments/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/(third-party)/requirement-assessments/[id=uuid]/edit/+page.svelte | [code/config] | [critical] | [route /requirement-assessments/[id=uuid]/edit] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/+error.svelte | [code/config] | [important] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/+layout.server.ts | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/+layout.svelte | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/+page.server.ts | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/+page.svelte | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/assets/disaster-recovery-objectives/+server.ts | [code/config] | [important] | [route /assets/disaster-recovery-objectives] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/assets/security-objectives/+server.ts | [code/config] | [important] | [route /assets/security-objectives] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/setup-mfa/+page.server.ts | [code/config] | [critical] | [route /setup-mfa] | Primary SvelteKit frontend.
- frontend/src/routes/(app)/setup-mfa/+page.svelte | [code/config] | [critical] | [route /setup-mfa] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/first-connexion/+page.server.ts | [code/config] | [critical] | [route /first-connexion] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/first-connexion/+page.svelte | [code/config] | [critical] | [route /first-connexion] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/+page.server.ts | [code/config] | [critical] | [route /login] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/+page.svelte | [code/config] | [critical] | [route /login] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/FormCard.svelte | [code/config] | [important] | [route /login] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/Greetings.svelte | [code/config] | [important] | [route /login] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/mfa/components/MFAAuthenticateModal.svelte | [code/config] | [important] | [route /login/mfa/components] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/login/mfa/utils/schemas.ts | [code/config] | [important] | [route /login/mfa/utils] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/logout/+server.ts | [code/config] | [important] | [route /logout] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/password-reset/+page.server.ts | [code/config] | [critical] | [route /password-reset] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/password-reset/+page.svelte | [code/config] | [critical] | [route /password-reset] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/password-reset/confirm/+page.server.ts | [code/config] | [critical] | [route /password-reset/confirm] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/password-reset/confirm/+page.svelte | [code/config] | [critical] | [route /password-reset/confirm] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/register/+page.server.ts | [code/config] | [critical] | [route /register] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/register/+page.svelte | [code/config] | [critical] | [route /register] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/register/RegisterForm.svelte | [code/config] | [important] | [route /register] | Primary SvelteKit frontend.
- frontend/src/routes/(authentication)/sso/authenticate/[token]/+page.server.ts | [code/config] | [critical] | [route /sso/authenticate/[token]] | Primary SvelteKit frontend.
- frontend/src/routes/+error.svelte | [code/config] | [important] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/+layout.server.ts | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/+layout.svelte | [code/config] | [critical] | [route /] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/build/+server.ts | [code/config] | [important] | [route /fe-api/build] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/cascade-info/[model]/[id]/+server.ts | [code/config] | [important] | [route /fe-api/cascade-info/[model]/[id]] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/comments/+server.ts | [code/config] | [important] | [route /fe-api/comments] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/comments/[id]/+server.ts | [code/config] | [important] | [route /fe-api/comments/[id]] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/user-preferences/+server.ts | [code/config] | [important] | [route /fe-api/user-preferences] | Primary SvelteKit frontend.
- frontend/src/routes/fe-api/waiting-risk-acceptances/+server.ts | [code/config] | [important] | [route /fe-api/waiting-risk-acceptances] | Primary SvelteKit frontend.
- frontend/static/favicon.ico | [artifact] | [generated/artifact] | Primary SvelteKit frontend.
- frontend/static/favicon.svg | [file] | [important] | Primary SvelteKit frontend.
- frontend/static/vendor/frappe-gantt.css | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/svelte.config.js | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/tests/docker-compose.e2e-tests.yml | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/tests/Dockerfile | [file] | [critical] | Primary SvelteKit frontend.
- frontend/tests/e2e-tests.sh | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/backup-restore.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/analytics.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/business-impact-analysis.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/common.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/compliance-assessments.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/ebios-rm.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/findings-assessments.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/incidents.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/libraries.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/login.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/mappings.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/my-assignments.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/settings/general.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/settings/sso.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/detailed/tprm.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/domain-import.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/enterprise/settings/client.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/i18n.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/my-profile-settings.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/nav.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/pdf-export.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/startup.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/user-permissions.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/functional/user-route.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/fuzz/open-redirect/open-redirect.test.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/fuzz/open-redirect/payloads.txt | [doc] | [optional] | Primary SvelteKit frontend.
- frontend/tests/hot-reload/_main.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/keycloak/test-realm.json | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/README.md | [doc] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/analytics-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/base-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/form-content.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/layout.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/login-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/mail-content.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/mailer.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/page-content.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/page-detail.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/sidebar.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test-data.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test-utils.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test_favicon.ico | [artifact] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test_file.txt | [doc] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test_image.png | [artifact] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utils/test_logo.png | [artifact] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/base/create-modal.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/base/list-view-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/base/model-form.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/base/model-table.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/base.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/element.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/fixtures.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/hot-reloader.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/test-data.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/core/utils.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/analytics-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/create-modal.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/list-view.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/login-page.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/model-form/folder-create-form.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/sidebar.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tests/utilsv2/derived/toast.ts | [code/config] | [optional] | Primary SvelteKit frontend.
- frontend/tsconfig.json | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/vite.config.ts | [code/config] | [critical] | Primary SvelteKit frontend.
- frontend/vitest-setup.ts | [code/config] | [important] | Primary SvelteKit frontend.
- frontend/vitest.config.ts | [code/config] | [important] | Primary SvelteKit frontend.

### gh_banner.png
- gh_banner.png | [artifact] | [generated/artifact] | Binary asset or data artifact.

### git_hooks
- git_hooks/post-commit | [file] | [important] | Supporting project file.
- git_hooks/post-merge | [file] | [important] | Supporting project file.

### integration
- integration/basic.py | [code/config] | [important] | Integration support or tests.
- integration/oscf_parser.py | [code/config] | [important] | Integration support or tests.

### local_db_backup.dump
- local_db_backup.dump | [artifact] | [generated/artifact] | Binary asset or data artifact.

### missing_ar_keys.txt
- missing_ar_keys.txt | [doc] | [important] | Configuration, sample data, or auxiliary artifact.

### packaging
- packaging/rhel/.gitignore | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/build-rpm.sh | [code/config] | [important] | Packaging and release artifacts.
- packaging/rhel/CHECKLIST.md | [doc] | [important] | Packaging and release artifacts.
- packaging/rhel/QUICKSTART.md | [doc] | [important] | Packaging and release artifacts.
- packaging/rhel/README.md | [doc] | [important] | Packaging and release artifacts.
- packaging/rhel/scripts/post-install-setup.sh | [code/config] | [important] | Packaging and release artifacts.
- packaging/rhel/SPECS/ciso-assistant.spec | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/systemd/ciso-assistant-backend.service | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/systemd/ciso-assistant-frontend.service | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/systemd/ciso-assistant-huey.service | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/templates/backend.env | [file] | [important] | Packaging and release artifacts.
- packaging/rhel/templates/frontend.env | [file] | [important] | Packaging and release artifacts.

### perf_testing
- perf_testing/add_latency.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.
- perf_testing/check_latency.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.
- perf_testing/docker-compose.yml | [code/config] | [critical] | Configuration, sample data, or auxiliary artifact.
- perf_testing/README.md | [doc] | [important] | Documentation or policy file.
- perf_testing/remove_latency.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.
- perf_testing/setup_toxiproxy.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### posture.png
- posture.png | [artifact] | [generated/artifact] | Binary asset or data artifact.

### provision_role_users.py
- provision_role_users.py | [code/config] | [important] | Supporting project file.

### pyrightconfig.json
- pyrightconfig.json | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### reformat.sh
- reformat.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### resources.md
- resources.md | [doc] | [important] | Supporting project file.

### sanadcom-postgres-20260701-110303.dump
- sanadcom-postgres-20260701-110303.dump | [artifact] | [generated/artifact] | Binary asset or data artifact.

### sanadcom-postgres-20260701-111128.dump
- sanadcom-postgres-20260701-111128.dump | [artifact] | [generated/artifact] | Binary asset or data artifact.

### setup_jwt.sh
- setup_jwt.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### single_hub.png
- single_hub.png | [artifact] | [generated/artifact] | Binary asset or data artifact.

### soa_sample.pdf
- soa_sample.pdf | [artifact] | [generated/artifact] | Binary asset or data artifact.

### test_roles.ps1
- test_roles.ps1 | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

### tests
- tests/gen_random_domains_with_assets.py | [code/config] | [optional] | Top-level tests and validation assets.

### tools
- tools/check_missing_i18n_keys.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/convert_library_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/convert_v1_to_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/example_framework.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/example_metric_definitions.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/example_questionnaire.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/3cf/3cf-ed1-v1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/3cf/3cf-v2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/acn-it/Framework-Nazionale-CS-DP.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/adobe-ccf-v5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/adobe-ccf-v5_mapping_exporter.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/adobe/convert_ccf.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-bsi-c5-2020.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-cyber_essentials_requirements_for_it_infrastructure.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-fedramp-rev5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-nist-csf-1.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-pcidss-4_0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/mappings/mapping-adobe-ccf-v5-and-soc2-2017-rev-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/adobe/Open_Source_CCF.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/AI-ACT/AI-act.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/aicpa/mapping-soc2-2017-rev-2022-to-iso27001-2022_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/aicpa/soc2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/aicpa/SOC2_2017_with_rev_2022_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/aircyber/aircyber-v1.5.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/aircyber/aircyber.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-architectures-si-sensibles-dr.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-genai-security-recommendations-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-guide-admin-securisee-si.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-guide-des-mecanismes-cryptographiques.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-guide-hygiene-detail.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-guide-hygiene-detail_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-guide-hygiene_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-maturite-gestion-crise-1.0.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-mon-aide-cyber.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-rec-secu-interco-si-internet.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-rec-secu-ipsec.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-rec-secu-ssh.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-rec-secu-sys-ctrl-acces-phys-videoprot.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-recommandations-configuration-systeme-gnu-linux.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-recommandations-pour-la-protection-des-sie.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-recommandations-securite-architecture-systeme-journalisation.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-recommandations-securite-relatives-TLS.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/anssi-referentiel-general-de-securite-annexe-b2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/igi-1300.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/II-901.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/II-901_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/label-ebios-risk-manager.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/mapping-secnumcloud-3.2-to-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/pdis.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/secnumcloud-3.2-annexe-2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/secnumcloud-3.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/ad/anssi_ad_framework_builder.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/ad/anssi_ad_web_scraper.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/ad/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/ad/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/.gitignore | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/anssi_MAC_build_excel_from_json.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/anssi_MAC_build_excel_from_json.py.old | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/anssi_MAC_export_referentiels_json.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/anssi_MAC_framework_builder.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/anssi/tools/mon-aide-cyber/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/apra/cps-230.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/apra/cps-234.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bio2/bio2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-app-anwendungen.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-con-konzeption-und-vorgehensweisen.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-der-detektion-und-reaktion.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-ind-industrielle-it.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-inf-infrastruktur.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-isms-sicherheitsmanagement.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-net-netze-und-kommunikation.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-ops-betrieb.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-orp-organisation-und-personal.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bs-it-gs-2023-sys-it-systeme.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/bsi-c5-2020.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/BSI-externer-Cloud-Dienste.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/bsi/it-grundschutz-kompendium-2023.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/canada/itsp.10.171.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/canada/tools/itsp.10.171_web_scraper.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccb/ccb-cff-2023-03-01.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/ccb-cff-2023-03-01_framework_NL.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccb/cyfun-small-self-assessment.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/cyfun-small-self-assessment_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/cyfun2025.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/CyFUN_ESSENTIEEL_V2023-03-01_N_update 2024.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/mapping-ccb-cff-2023-03-01-and-ccb-cyfun2025.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/mapping-ccb-cff-2023-03-01-to-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/mapping-ccb-cff-2023-03-01-to-iso27001-2022_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ccb/pdf_text_extractor_NL.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/convert_ccm.bat | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/convert_ccm.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/convert_ccm.sh | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/convert_ccm_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/ccm/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/CCPA/CCPA act.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/CCPA/CCPA_regulations.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cis/cis-benchmark-kubernetes.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cis/convert_cis.bat | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/convert_cis.sh | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/mapping-cis-controls-v8-and-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cis/prep_cis.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/prep_cis_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/prep_mapping_cis_controls_csf_2.0.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/prep_mapping_cis_controls_iso_27.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/prep_mapping_cis_controls_nist_800-53-rev5.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/cis/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/excel/cisa/cisa-cpg-2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisa/cisa-vendor-scrm.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/cisco-ccf-v3.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/cisco-ccf-v3.0_framework.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cisco/cisco-ccf-v3.0_mapping_exporter.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/cisco/Cisco-CCFv3-Public.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-bsi-c5-2020.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-esquema-nacional-de-seguridad.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-fedramp-rev5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-ncsc-caf-3.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-nist-800-171-rev2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-nist-800-171-rev3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-nist-ssdf-1.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-pcidss-4_0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-secnumcloud-3.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cisco/mappings/mapping-cisco-ccf-v3.0-and-soc2-2017-rev-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cjis/CJIS-version-5.9.5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cjis/CJIS.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cjis/mapping-cjis-policy-5.9.4-to-cjis-policy-5.9.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/clausier-sante/clausier-sante-v2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cmmc/cmmc-2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cnil/cnil-guide-securite.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/Controlli-Minimi-AGID/Controlli-minimi-AGID.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/cra/CRA-regulation-annexes.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/CROE-FOR-FMI/CROE-for-FMI.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/Cyber_essentials_requirements/Cyber_essentials.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dfs-500/dfs-500-2023-11.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/DGA/Formulaire-SDI-SecNum-2216.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dgssi/dnssi-2023-2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dgssi/Loi_05-20-Maroc.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dgssi/Mapping_Complet_DNSSI_vs_ISO_27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/dora.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/norea.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/GL-on-costs-and-losses.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/ITS-incident-reporting.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-DORA-ICT-related-incidents.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-DORA-ICT-risk-management.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-DORA-ICTservices-supporting.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-DORA-incident-reporting_official.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-on-JET.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-OVS-conduct.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/RTS-threat-led-penetration-tests.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/tools/RTS-DORA-ICT-risk-management_text_formatter.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/dora/RTS/tools/RTS-DORA-incident-reporting_text_formatter.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/e-its/convert_eits.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/e-its/e-its-2024-source.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/e-its/e-its-2024.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ecc/ecc-1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/enisa/5G Security Controls Matrix_v1.3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/enisa/convert_5g_scm.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/enisa/enisa-5g-scm-v1.3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ENS decreto/ENS-RD-311-2020-con-Refuerzos.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ESRS/ESRS-p1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ESRS/ESRS-p2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ESRS/ESRS-p3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/essential-eight/essential-eight.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/etat_beninois/pssie-benin.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/EU/cloud-sovereignty-framework.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/fadp/fadp.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/finma/finma-2023-01.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/finma/finma-2023-01_framework.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/finma/finma_rs_2023_01_20221207_de.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/finma/finma_rs_2023_01_20221207_en.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/finma/finma_rs_2023_01_20221207_fr.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/finma/finma_rs_2023_01_20221207_it.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/FNCS-v2/fncs-v2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/gdpr/gdpr-checklist.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/gdpr/GDPR.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/google/google-saif.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/google/google-saif_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/gsa/fedramp-rev5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/HDS/hds-v2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ict-minimal/2023_IKT-Minimalstandard-Assessment.Tool-1.1-2023_Revision 5_E_D_F_I.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ict-minimal/ict-minimal-convert.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/ict-minimal/ict-minimal.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/india/india-dpdpa-2023.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/asf-baseline-v2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/checklist-dossier-homologation.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/doc-pol.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/doc-pol_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/intuitem-common-catalog.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/intuitem-common-catalog_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/metrics/core_cybersecurity_metrics.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/intuitem/vendor-due-diligence.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/iso/iso22301-2019.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/iso/iso42001-2023.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/iso27001/iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/iso27001/mapping-iso27001-2013-to-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/iso27001/mapping-iso27001-2022-to-secnumcloud-3.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ITAR/ITAR-Compliance-Program-Guidelines.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/K ISMS-P/K-ISMS-P.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/lpm/lpm-oiv-2019.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/lpm/lpm-oiv-2019.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/lt-nis2-kibernetinio-saugumo-istatymas/lt-nis2-kibernetinio-saugumo-istatymas.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-3x3-mult.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-4x4-ebios-rm.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-4x4-ebios-rm_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-4x4-with-5-levels.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-5x3-demo_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-5x5-iso-27005.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-5x5-sensitive.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/matrix/risk-matrix-6x6-detailed.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/mcas/mcas-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/microsoft/mcsb-v1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/microsoft/parse_mcsb.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/mitre/d3fend.csv | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/mitre/d3fend.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/mitre/d3fend.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/mitre/measures.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/mitre/mitre-attack.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/mitre/mitre.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/mitre/techniques.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ncsc/ncsc-caf-3.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS/nis1-rules-fr.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/annex-nis2-regulation--2024-2690-with-technical-implementation-guidance-by-enisa.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/ENISA_Technical_Implementation_Guidance_Mapping_table_version_1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/mappings/mapping-annex-technical-and-methodological-requirements-nis2-and-ccb-cff-2023-03-01.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/mappings/mapping-annex-technical-and-methodological-requirements-nis2-and-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/mappings/mapping-annex-technical-and-methodological-requirements-nis2-and-nist-csf-2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/nis2-directive.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/NIS2/tools/NIS2_guidance_evidence.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/NIS2/tools/NIS2_guidance_evidence_transfer.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/NIS2/tools/NIS2_text_formatter.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/ai-rmf/nist-ai-rmf-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/csf2-tools/csf20.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/csf2-tools/csfv2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/csf2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/mapping-nist-csf-1.1-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/mapping-nist-csf-1.1-nist-csf-2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/mapping-nist-csf-2.0-to-iso27001-2022_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/nist-csf-1.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/nist-csf-2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/nist_csf_2.0_to_iso27001-2022.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/privacy/nist-privacy-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-171/nist-800-171-rev2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-171/nist-800-171-rev3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-218/nist-ssdf-1.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-53/mapping-nist-sp-800-53-rev5-to-iso27001-2022.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-53/nist-sp-800-53-rev5.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-53/nist-sp-800-53-rev5_to_iso27001-2022.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-53/sp800-53r5-to-iso-27001-mapping-2022-OLIR-2023-10-12-UPDATED.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/cprt_SP800_66_2_0_0_04-05-2024.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/mapping-nist-sp-800-66-rev2-to-nist-csf-1.1_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/mapping-nist-sp-800-66-rev2-to-nist-csf-2.0_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/mapping-nist-sp-800-66-rev2-to-nist-sp-800-53-rev5_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/nist-sp-800-66-rev2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/nist-sp-800-66.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-66/requirement_numbering.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nist/sp-800-82/nist-sp-800-82-annex-f.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nzism/nzism-3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/nzism/nzism-3.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/nzism/NZISM-Document-V3.xml | [file] | [important] | Utility scripts and maintenance tools.
- tools/excel/nzism/prep_nzism.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/OTCC/OTCC.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/owasp/mas-threats.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/owasp/owasp-asvs-4.0.3.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/owasp/owasp-asvs-5.0.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/owasp/owasp-llm-checklist.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/owasp/owasp-masvs-v2.1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/PART-IS/PART-IS.D.OR.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pci-dss/pcidss-4_0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pci-dss/tools/pcidss_framework_builder.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/pgssi-s/pgssi-s-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pqcc/PQC-Migration-Roadmap-PQCC-2.pdf | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pqcc/pqc-migration-roadmap.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pspdv/bsi_elementare_gefaherdungen.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/pspdv/bsi_elementare_gefaherdungen.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/pspf/pspf.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/PSSIE/PSSIE.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/rbi/rbi-itgrcap-2023-2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/rbi/rbi-itgrcap-2023.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/ref_audit_ssi_tunisie/Ref_Audit_SSI_TUNISIE.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/RGS/rgs-v2.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/sama/sama-crfr-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/sama/sama-crfr-1.0.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/sama/sama-csf-1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/sample/questionnaire.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/sample/sample.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-cis-controls-v8-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-india-dpdpa-2023-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-iso27001-2022-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-iso42001-2023-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-nist-csf-2.0-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-pcidss-4_0-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-scf-2025.2.2-and-swift-cscf-v2025.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/mappings/mapping-soc2-2017-rev-2022-and-scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/scf-2024-2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/scf-2025.2.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/scf/scf_framework.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_cis_csc_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_essential8_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_india_dpdpa_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_iso27001_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_iso42001_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_nist_csf_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_pci_dss_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_soc2_strm_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/create_swift_csf_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/scf/tools/extract_strm.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/sikker-digital/de-tekniske-minimumskrav.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/standards-for-safeguarding-customer-information/standards-for-safeguarding-customer-information.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/swift/swift-cscf-v2025v1.0.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/TIBER/tiber-eu-2018.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/tisax/convert_tisax.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/tisax/convert_tisax_5.1.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/tisax/ISA6_EN_6.0.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/tisax/tisax-v5.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/tisax/tisax-v6.0.2.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/tisax/VDA_ISA_5_1_EN.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/vcsa/convert_vcsa-v1.1.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/excel/vcsa/ENX_VCSA_1_1_EN.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/vcsa/vcsa-v1.1.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/excel/vcsa/vcsa-v1.1_new.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/mapping_builder/compare_models.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/example_usage.sh | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/heatmap_builder.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/heatmap_builder_notebook.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/MARIMO_README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/prepare_review.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/sbert_mapper.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/semantic_mapper.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/mapping_builder/simplify_mapping.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/bad_mapping_remover.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/check_converted_excels_against_libraries.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/convert_framework_yaml_to_excel.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/convert_library_v1.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/convert_mapping_yaml_to_excel.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/convert_v1_to_v2_tree.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/footnote_reference_prettifier.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/mapping_expander.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/mapping_expander_exceptions.json | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/mapping_extractor.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/mapping_extractor_config.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/mapping_merger.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/migrate_yaml_questions.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/prepare_mapping_v1.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/questionnaires/Cuestionario_Gestion_del_Riesgo_Cadena_de_Suministro.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/misc/questionnaires/README.txt | [doc] | [important] | Utility scripts and maintenance tools.
- tools/misc/README_v1.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/misc/remove_new_suffix_from_excels.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/misc/simple_pdf_extractor.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/prepare_framework_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/prepare_framework_v2_config.xlsx | [artifact] | [generated/artifact] | Utility scripts and maintenance tools.
- tools/prepare_framework_v2_config.yaml | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/prepare_mapping_v2.py | [code/config] | [important] | Utility scripts and maintenance tools.
- tools/README.md | [doc] | [important] | Utility scripts and maintenance tools.
- tools/requirements.txt | [doc] | [important] | Utility scripts and maintenance tools.

### translate_ar.py
- translate_ar.py | [code/config] | [important] | Supporting project file.

### translate_ar_batch.py
- translate_ar_batch.py | [code/config] | [important] | Supporting project file.

### update-ciso-assistant.sh
- update-ciso-assistant.sh | [code/config] | [important] | Configuration, sample data, or auxiliary artifact.

## Important Files
- README.md
- DEPLOYMENT.md
- TECHNICAL_REPORT.md
- backend/ciso_assistant/settings.py
- backend/ciso_assistant/urls.py
- backend/manage.py
- backend/startup.sh
- frontend/src/hooks.server.ts
- frontend/src/routes/(app)/+layout.svelte
- frontend/src/lib/utils/crud.ts
- enterprise/backend/enterprise_core/settings.py
- cli/clica.py

## Final Knowledge Base
- Complete project summary: a mature GRC platform for compliance, risk, evidence, privacy, resilience, vendor risk, and reporting.
- Architecture summary: Django API + SvelteKit UI + CLI/MCP tools + enterprise overlay + containerized deployment.
- Folder responsibilities: backend owns business logic, frontend owns UX, cli owns automation, enterprise customizes behavior, docs explain deployment and architecture.
- Technology stack: Python 3.14, Django 6, DRF, allauth, Knox, SimpleJWT, Huey, PostgreSQL, SvelteKit, Svelte 5, TypeScript, Tailwind, Caddy, Docker, Helm.
- Business workflows: assessment creation, control mapping, evidence handling, remediation, exports, notifications, and integration sync.
- Authentication workflow: Knox, JWT, SSO, MFA, PATs, and folder-scoped RBAC.
- Database workflow: ORM-backed schema with many migrations, file attachments, and folder-based tenancy.
- API workflow: router-based DRF endpoints plus custom action routes and frontend proxy/server routes.
- Critical dependencies: Django, DRF, allauth, Knox, SimpleJWT, Huey, SvelteKit, Skeleton, Tailwind, Paraglide, WeasyPrint, psycopg2, boto3.
- Known limitations: the repository is huge, migration-heavy, and relies on runtime configuration and external services that cannot be fully proven from static inspection alone.
- Questions remaining: exact production environment values, live tenant topology, and which enterprise features are enabled in the target deployment.
