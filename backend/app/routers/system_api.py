from fastapi import (
    APIRouter,
    HTTPException,
)

from app.models.health import Health
from app.models.version import Version
from app.repositories.system_repo import SystemRepository

router = APIRouter()


@router.get(
    "/health",
    responses={
        200: {"model": Health, "description": "OK"},
    },
    summary="Liveness / readiness probe",
    response_model_by_alias=True,
)
async def get_health() -> Health:
    try:
        return await SystemRepository().get_health()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/version",
    responses={
        200: {"model": Version, "description": "Version info"},
    },
    summary="API and build/version info",
    response_model_by_alias=True,
)
async def get_version() -> Version:
    try:
        return await SystemRepository().get_version()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
