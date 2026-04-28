from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.links.services import create_link, get_link_by_code, get_links
from app.links.schemas import ShortenRequest, ShortenResponse

router = APIRouter()

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, session: AsyncSession = Depends(get_db)):
    new_link = await create_link(session, request.original_url)
    return new_link

@router.get("/{short_code}")
async def redirect_to_url(short_code: str, session: AsyncSession = Depends(get_db)):
    original_url = await get_link_by_code(session, short_code)
    
    if not original_url:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return RedirectResponse(url=original_url, status_code=307)

@router.get("/all_links")
async def get_all_links(session: AsyncSession = Depends(get_db)):
    links = await get_links(session)

    return links