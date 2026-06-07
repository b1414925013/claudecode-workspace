from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import httpx

router = APIRouter()

@router.get("/{song_id}")
async def download(song_id: str, platform: str, quality: str = "standard"):
    return {"message": "download endpoint"}