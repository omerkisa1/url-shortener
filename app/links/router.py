from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.links.services import create_link, get_link_by_code, get_links, get_statistics, delete_link
from app.links.schemas import ShortenRequest, ShortenResponse, AllLinksResponse, StatisticsResponse, DeleteLinkResponse
from app.rabbitmq import publish_click_events

import requests

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

from fastapi import Request

@router.get("/{short_code}")
async def redirect_to_url(short_code: str, request: Request, session: AsyncSession = Depends(get_db)):
    original_url = await get_link_by_code(session, short_code)

    if not original_url:
        raise HTTPException(status_code=404, detail="Link not found")

    user_agent = request.headers.get("user-agent")

    await publish_click_events(
        short_code=short_code,
        user_agent=user_agent
    )

    return RedirectResponse(url=original_url, status_code=307)

@router.delete("/{short_code}", response_model=DeleteLinkResponse)
async def delete_link_by_code(short_code: str, session: AsyncSession = Depends(get_db)):
    deleted_link = await delete_link(session, short_code)
    if not deleted_link:
        raise HTTPException(status_code=404, detail="Link not found")

    return {
        "short_code": deleted_link.short_code,
        "original_url": deleted_link.original_url,
        "deleted_at": deleted_link.deleted_at,
    }