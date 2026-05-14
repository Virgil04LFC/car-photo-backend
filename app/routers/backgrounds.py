from fastapi import APIRouter

from app.models import BackgroundListResponse
from app.services.backgrounds import list_backgrounds

router = APIRouter()


@router.get("/backgrounds", response_model=BackgroundListResponse)
async def get_backgrounds() -> BackgroundListResponse:
    """Return the list of available backgrounds the app can choose from."""
    return BackgroundListResponse(backgrounds=list_backgrounds())
