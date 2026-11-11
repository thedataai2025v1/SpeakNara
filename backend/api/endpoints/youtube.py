"""YouTube evaluation endpoint."""

from fastapi import APIRouter, HTTPException

from services.youtube_transcript import fetch_youtube_transcript

router = APIRouter()


@router.post("/evaluate")
async def evaluate_youtube(body: dict):
    """Accept a YouTube URL, transcribe it, and return analysis.

    Request body: {"url": "https://youtube.com/watch?v=..."}
    Returns transcript and word count (analysis happens via /upload pipeline).
    """
    url = body.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="YouTube URL is required")

    try:
        result = await fetch_youtube_transcript(url)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return result
