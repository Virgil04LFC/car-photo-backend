from pydantic import BaseModel


class Background(BaseModel):
    id: str
    name: str
    description: str
    preview_color: str  # hex colour for app-side UI preview tile


class BackgroundListResponse(BaseModel):
    backgrounds: list[Background]
