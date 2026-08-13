import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiohttp import web  # YANGI

from config import BOT_TOKEN
from database.engine import Base, engine, SessionLocal
from handlers import start, menu, smm, admin
from handlers.game import router as game_router  # YANGI
from services.seed import seed_services
from handlers.api_handlers import handle_balance, handle_click  # YANGI


async def main():
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN sozlanmagan! .env faylini to'ldiring.")

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    # Routerlarni ulash (eski + yangi)
    dp.include_router(start.router)
    dp.include_router(menu.router)
    dp.include_router(smm.router)
    dp.include_router(admin.router)
    dp.include_router(game_router)   # <-- /game buyrug'i uchun

    # Jadvallarni yaratish
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Boshlang'ich xizmatlarni kiritish
    async with SessionLocal() as session:
        await seed_services(session)
        await session.commit()

    # ---------- HTTP API serverini ishga tushirish ----------
    app = web.Application()
    app.router.add_get('/api/balance', handle_balance)
    app.router.add_post('/api/click', handle_click)

    # Portni sozlash (Railway/Render uchun muhim)
    port = int(os.getenv('PORT', 8080))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logging.info(f"HTTP API http://0.0.0.0:{port} da ishga tushdi")

    # ---------- Bot pollingni boshlash ----------
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())