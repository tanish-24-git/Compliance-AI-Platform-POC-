"""
API Router initialization.
Aggregates all route modules and registers them with correct prefixes.
"""

from fastapi import APIRouter
from app.api.routes import agent, admin, super_admin, health

api_router = APIRouter()

# Include all route modules with correct prefixes
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(agent.router, tags=["Agent"])  # No prefix - routes already have /api/
api_router.include_router(admin.router, tags=["Admin"])  # No prefix - routes already have /api/
api_router.include_router(super_admin.router, prefix="/super-admin", tags=["Super Admin"])
