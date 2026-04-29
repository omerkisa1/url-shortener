from fastapi import FastAPI, Depends
from app.config import settings
from contextlib import asynccontextmanager
from app.database import get_db
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.links.router import router as LinkRouter
from app.redis import init_redis, close_redis
from app.rabbitmq import init_rabbitmq, close_rabbitmq

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_redis()
    await init_rabbitmq()
    yield 
    await close_redis()
    close_rabbitmq()


app = FastAPI(lifespan=lifespan)
app.include_router(LinkRouter, prefix="/link")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check(session: AsyncSession = Depends(get_db)):
    try:
        await session.execute(text("SELECT 1"))
        return{"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "message": "Database connection failed"}
