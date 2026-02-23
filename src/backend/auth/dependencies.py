"""
Auth dependencies - re-exports for compatibility
"""
from auth.security import require_permission, get_current_user, get_current_active_user

__all__ = ["require_permission", "get_current_user", "get_current_active_user"]
