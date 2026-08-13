from sqlalchemy import select
from database.models import Service

# Boshlang'ich xizmatlar ro'yxati (panel kodlari o'z panelingizga moslab o'zgartiriladi)
DEFAULT_SERVICES = [
    {
        "service_code": "ig_followers",
        "name": "Instagram Obunachilar",
        "category": "Instagram",
        "price_per_1000": 5000,
        "min_quantity": 10,
        "max_quantity": 100000,
    },
    {
        "service_code": "ig_views",
        "name": "Instagram Ko'rishlar",
        "category": "Instagram",
        "price_per_1000": 2000,
        "min_quantity": 50,
        "max_quantity": 1000000,
    },
    {
        "service_code": "tg_members",
        "name": "Telegram Obunachilar",
        "category": "Telegram",
        "price_per_1000": 7000,
        "min_quantity": 10,
        "max_quantity": 100000,
    },
    {
        "service_code": "tg_views",
        "name": "Telegram Ko'rishlar",
        "category": "Telegram",
        "price_per_1000": 1500,
        "min_quantity": 50,
        "max_quantity": 1000000,
    },
]


async def seed_services(session):
    """Agar xizmatlar jadvali bo'sh bo'lsa, boshlang'ich xizmatlarni qo'shadi."""
    result = await session.execute(select(Service).limit(1))
    if result.scalar_one_or_none() is None:
        for item in DEFAULT_SERVICES:
            session.add(Service(**item))