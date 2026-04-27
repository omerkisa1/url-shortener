import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.links.models import Link

def generate_short_code() -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choices(chars, k=6))
    
async def create_link(session: AsyncSession, original_url: str):
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
    stmt = select(Link).where(Link.short_code == short_code)
    result = await session.execute(stmt)
    link = result.scalars().first()
    
    if link:
        link.click_count += 1
        await session.commit()
        await session.refresh(link)
        
    return link