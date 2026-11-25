"""Release-only overlay. Does not change the existing repository settings file."""
from .settings import *  # noqa: F403

# These are Python booleans/tuples, not truthy environment-variable strings.
SICO_ENGAGEMENT_COMMITS_ENABLED = False
SICO_AI_EXECUTION_STAGE_ALLOWLIST = ()
FORCE_CREATE_ADMIN = False

# SICO case-only execution. Disabled unless explicitly enabled.
# General AI engagement commits retain their separate disabled policy.
SICO_CASE_SETUP_COMMITS_ENABLED = (
    __import__("os").environ.get(
        "SICO_CASE_SETUP_COMMITS_ENABLED", ""
    ).strip().lower() == "true"
)
