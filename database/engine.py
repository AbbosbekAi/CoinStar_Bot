from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from config import DATABASE_URL

# Async engine yaratamiz
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Sessiya fabrikasi
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Baza uchun asosiy model klassi
class Base(DeclarativeBase):
    pass