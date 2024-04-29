from fastapi import APIRouter

from dns_system.apps.domains.views.api import router as domain_router


core_router = APIRouter()

core_router.include_router(domain_router, prefix="/domains", tags=["Domains"])
