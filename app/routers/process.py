import logging

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from app.services.photoroom import process_image, ProcessingTimings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/process",
    response_class=Response,
    responses={
        200: {
            "content": {"image/png": {}},
            "description": "Processed PNG — car composited onto chosen background",
        },
        400: {"description": "Bad request (empty file, unknown background)"},
        502: {"description": "Photoroom API error"},
    },
)
async def process(
    image: UploadFile = File(..., description="Car photo — JPEG or PNG"),
    background_id: str = Form(..., description="Background ID from /backgrounds"),
) -> Response:
    """
    Accept a car photo and a background ID.
    Resize, send to Photoroom /v2/edit, return PNG composite.
    """
    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="image file is empty")

    logger.info(
        "POST /process — file=%s size=%d bg=%s",
        image.filename,
        len(image_bytes),
        background_id,
    )

    try:
        result_png, timings = await process_image(image_bytes, background_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except TimeoutError as exc:
        logger.error("Photoroom timeout: %s", exc)
        raise HTTPException(status_code=504, detail=str(exc))
    except RuntimeError as exc:
        logger.error("Photoroom error: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc))

    return Response(
        content=result_png,
        media_type="image/png",
        headers={
            "X-Background-Id": background_id,
            "X-Processing-Time-Ms": str(timings.total_ms),
            "X-Resize-Time-Ms": str(timings.resize_ms),
            "X-Photoroom-Time-Ms": str(timings.photoroom_ms),
        },
    )
