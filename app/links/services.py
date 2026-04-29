import string
import random
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.links.models import Link
from app import redis
from app.rabbitmq import publish_click_events

def generate_short_code() -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))
    
async def create_link(session: AsyncSession, original_url: str):
    original_url = str(original_url)

    cache_key = f"url:{original_url}"
    existing_code = await redis.redis_client.get(cache_key)

    if existing_code:
        stmt = select(Link).where(Link.short_code == existing_code)
        result = await session.execute(stmt)
        return result.scalars().first()

    for _ in range(5):
        code = generate_short_code()

        try:
            new_link = Link(original_url=original_url, short_code=code)
            session.add(new_link)
            await session.commit()
            await session.refresh(new_link)

            await redis.redis_client.set(cache_key, code, ex=3600)
            await redis.redis_client.set(f"code:{code}", original_url, ex=3600)

            return new_link

        except IntegrityError:
            await session.rollback()
            continue

    raise Exception("Failed to generate unique short code")
        

async def delete_link(session: AsyncSession, short_code: str):
    short_code = str(short_code)

    stmt = select(Link).where(Link.short_code == short_code,Link.deleted_at.is_(None))
    result = await session.execute(stmt)
    link = result.scalars().first()

    if not link:
        return None

    link.deleted_at = datetime.utcnow()
    await session.commit()

    await redis.redis_client.delete(f"code:{short_code}")
    await redis.redis_client.delete(f"url:{link.original_url}")

    return link

async def get_link_by_code(session: AsyncSession, short_code: str):
    cached_url = await redis.redis_client.get(short_code)
    if cached_url:
        await publish_click_events(short_code)
        return cached_url

    stmt = select(Link).where(Link.short_code == short_code).where(Link.deleted_at.is_(None))
    result = await session.execute(stmt)
    link = result.scalars().first()

    if link:
        await redis.redis_client.set(short_code, link.original_url, ex=3600)
        await publish_click_events(short_code)
        return link.original_url

    return None

async def get_links(session: AsyncSession):
    stmt = select(Link).where(Link.deleted_at.is_(None))
    result = await session.execute(stmt)
    all_links = result.scalars().all()
    print(all_links)
    return all_links

async def get_statistics(session: AsyncSession, short_code: str):
    stmt = select(Link.click_count).where(Link.short_code == short_code).where(Link.deleted_at.is_(None))
    result = await session.execute(stmt)

    statistic = result.scalars().first()
    return statistic
