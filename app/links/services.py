import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.links.models import Link
from app.redis import redis_client

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
    cached_url = await redis_client.get(short_code)
    if cached_url:
        stmt = select(Link).where(Link.short_code == short_code)
        result = await session.execute(stmt)
        link = result.scalars().first()

        if link:
            link.click_count += 1
            await session.commit()
        return {"original_url": cached_url}
    
    stmt = select(Link).where(Link.short_code == short_code)
    result = await session.execute(stmt)
    link = result.scalars().first()
    
    if link:
        await redis_client.set(short_code, link.original_url, ex=3600)
        link.click_count += 1
        await session.commit()
        await session.refresh(link)
        
    return link