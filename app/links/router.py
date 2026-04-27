from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.links.services import create_link, get_link_by_code
from app.links.schemas import ShortenRequest, ShortenResponse

router = APIRouter()

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, session: AsyncSession = Depends(get_db)):
    new_link = await create_link(session, request.original_url)
    return new_link

@router.get("/{short_code}")
async def redirect_to_url(short_code: str, session: AsyncSession = Depends(get_db)):
    link = await get_link_by_code(session, short_code)
    
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
        
    return RedirectResponse(url=link.original_url)