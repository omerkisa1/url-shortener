from fastapi import FastAPI, Depends
from app.config import settings
from app.database import get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.links.router import router as LinkRouter


app = FastAPI()
app.include_router(LinkRouter, prefix="/link")

@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text("SELECT 1"))
        return{"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": "Database connection failed"}
