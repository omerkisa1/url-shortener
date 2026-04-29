import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.links.models import Link
from app import redis
from app.rabbitmq import publish_click_events

def generate_short_code() -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))
    
async def create_link(session: AsyncSession, original_url: str):
    original_url = str(original_url)
    for _ in range(5):
        code = generate_short_code()
        stmt = select(Link).where(Link.short_code == code)
        result = await session.execute(stmt)
        if not result.scalars().first():
            new_link = Link(original_url=original_url, short_code=code)
            session.add(new_link)
            await session.commit()
            await session.refresh(new_link)
            return new_link
    raise Exception("Failed to generate unique short code")
        

async def get_link_by_code(session: AsyncSession, short_code: str):
    cached_url = await redis.redis_client.get(short_code)
    if cached_url:
        await publish_click_events(short_code)
        return cached_url

    stmt = select(Link).where(Link.short_code == short_code)
    result = await session.execute(stmt)
    link = result.scalars().first()

    if link:
        await redis.redis_client.set(short_code, link.original_url, ex=3600)
        await publish_click_events(short_code)
        return link.original_url

    return None

async def get_links(session: AsyncSession):
    stmt = select(Link)
    result = await session.execute(stmt)
    all_links = result.scalars().all()
    print(all_links)
    return all_links

async def get_statistics(session: AsyncSession, short_code: str):
    stmt = select(Link.click_count).where(Link.short_code == short_code)
    result = await session.execute(stmt)

    statistic = result.scalars().first()
    return statistic
