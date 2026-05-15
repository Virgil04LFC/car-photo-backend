"""
Background library.

Each entry defines how to set the background in the Photoroom /v2/edit call.
Two modes are supported:
  - color: passes `background.color` (hex, no #) — used for solid/studio colours
  - image_path: passes `background.imageFile` (PNG on disk) — used for textured scenes

To add a new background:
  1. Add an entry here.
  2. If image-based, drop the PNG in the `backgrounds/` directory at the repo root
     and set `image_path` to the relative path from the repo root.
"""

from pathlib import Path

from app.models import Background

# Absolute path to the backgrounds/ asset directory (repo root / backgrounds)
_BACKGROUNDS_DIR = Path(__file__).parent.parent.parent / "backgrounds"

# Colour-only backgrounds use `color` (hex, no #).
# Image backgrounds use `image_path` (relative to backgrounds/ dir) plus placement metadata:
#   floor_y_from_bottom  — measured floor-wall boundary as fraction from bottom (documentation)
#   placement_pad_bottom — paddingBottom value passed to Photoroom; places wheel contact point
#                          within the floor zone. See BACKGROUND_SPEC.md for the spec.
BACKGROUND_LIBRARY: dict[str, dict] = {
    # ── Solid colour backdrops ──────────────────────────────────────────────
    "showroom-light": {
        "name": "Light Showroom",
        "description": "Clean light grey studio with subtle floor reflection",
        "preview_color": "#EBEBEB",
        "color": "EBEBEB",
    },
    "showroom-dark": {
        "name": "Dark Showroom",
        "description": "Clean dark charcoal studio with subtle floor reflection",
        "preview_color": "#2A2A2A",
        "color": "2A2A2A",
    },
    "studio-white": {
        "name": "Studio White",
        "description": "Pure white studio backdrop",
        "preview_color": "#FFFFFF",
        "color": "FFFFFF",
    },
    "studio-black": {
        "name": "Studio Black",
        "description": "Deep black studio backdrop",
        "preview_color": "#111111",
        "color": "111111",
    },
    "midnight-blue": {
        "name": "Midnight Blue",
        "description": "Rich deep navy backdrop",
        "preview_color": "#0D1B2A",
        "color": "0D1B2A",
    },
    "slate-grey": {
        "name": "Slate Grey",
        "description": "Neutral slate grey backdrop",
        "preview_color": "#708090",
        "color": "708090",
    },
    "outdoor-sky": {
        "name": "Open Sky",
        "description": "Clear blue sky outdoor backdrop",
        "preview_color": "#87CEEB",
        "color": "87CEEB",
    },
    # ── Image-based backgrounds ─────────────────────────────────────────────
    # floor_y_from_bottom: PIL-measured floor-wall boundary (see BACKGROUND_SPEC.md)
    # placement_pad_bottom: paddingBottom passed to Photoroom for wheel alignment
    "concrete-warm": {
        "name": "Concrete Warm",
        "description": "Warm cream sweep with soft LED floor-wall glow — clean studio backdrop, no perspective lines",
        "preview_color": "#C8B99A",
        "image_path": "concrete-warm.jpg",
        "floor_y_from_bottom": 0.26,   # LED strip junction at 23.8%, wall-floor boundary ~26%
        "placement_pad_bottom": 0.10,  # wheels 10% from bottom, mid-floor zone
        "scene_type": "interior",
    },
}


def get_background(background_id: str) -> dict | None:
    return BACKGROUND_LIBRARY.get(background_id)


def list_backgrounds() -> list[Background]:
    return [
        Background(
            id=bg_id,
            name=bg["name"],
            description=bg["description"],
            preview_color=bg["preview_color"],
        )
        for bg_id, bg in BACKGROUND_LIBRARY.items()
    ]


def backgrounds_dir() -> Path:
    return _BACKGROUNDS_DIR
