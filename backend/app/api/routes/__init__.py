"""Routes package initialization"""

from app.api.routes import health, agent, admin, super_admin

__all__ = ["health", "agent", "admin", "super_admin"]
