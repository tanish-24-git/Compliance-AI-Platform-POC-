"""
API Router initialization.
Aggregates all route modules.
"""

from fastapi import APIRouter
from app.api.routes import agent, admin, super_admin, health

api_router = APIRouter()

# Include all route modules
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(agent.router, prefix="/agent", tags=["Agent"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(super_admin.router, prefix="/super-admin", tags=["Super Admin"])
