"""Audio upload endpoint."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from api.deps import get_current_user
from services.audio_upload import AudioUploadError, validate_audio

router = APIRouter()


class UploadResponse(BaseModel):
    """Audio upload response."""

    file_id: str
    filename: str
    duration: float


@router.post("/upload", responses={422: {"model": dict}})
async def upload_audio(
    file: UploadFile,
    user_info = Depends(get_current_user),
):
    """Upload and validate an audio file for speech evaluation."""
    try:
        content = await file.read()
        validate_audio(content, file.filename or "unknown.wav", file.content_type or "")

        file_id = str(uuid.uuid4())
        return UploadResponse(
            file_id=file_id,
            filename=file.filename or "unknown",
            duration=0.0,
        )

    except AudioUploadError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
