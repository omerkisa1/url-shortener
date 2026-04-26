from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from datetime import datetime

from app.database import Base

class Link(Base):
    __tablename__ = "links"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True)
    original_url: Mapped[str]  = mapped_column(String)
    short_code: Mapped[str]  = mapped_column(String, unique=True, index=True)
    click_count: Mapped[int]  = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(default=func.now())

