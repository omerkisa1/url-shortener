from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.links.services import create_link, get_link_by_code, get_links, get_statistics
from app.links.schemas import ShortenRequest, ShortenResponse, AllLinksResponse, StatisticsResponse

router = APIRouter()

@router.post("/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest, session: AsyncSession = Depends(get_db)):
    new_link = await create_link(session, request.original_url)
    return new_link

@router.get("/all_links", response_model=List[AllLinksResponse])
async def get_all_links(session: AsyncSession = Depends(get_db)):
    links = await get_links(session)
    return links


@router.get("/{short_code}/stats", response_model=StatisticsResponse)
async def stats(short_code: str,session: AsyncSession = Depends(get_db)):
    stat = await get_statistics(session, short_code)

    return {"click_count": stat}

@router.get("/{short_code}")
async def redirect_to_url(short_code: str, session: AsyncSession = Depends(get_db)):
    original_url = await get_link_by_code(session, short_code)
    
    if not original_url:
        raise HTTPException(status_code=404, detail="Link not found")
    
    return RedirectResponse(url=original_url, status_code=307)

