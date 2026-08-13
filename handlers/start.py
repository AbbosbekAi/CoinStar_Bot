from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from database.engine import SessionLocal
from database import crud
from config import ADMIN_IDS
from keyboards.inline import main_menu

router = Router()


@router.message(Command("start"))
async def start_cmd(message: Message):
    # Referral havolani tekshirish: /start ref_123456
    referrer_id = None
    parts = message.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            referrer_id = int(parts[1][4:])
        except ValueError:
            referrer_id = None

    async with SessionLocal() as session:
        user, is_new = await crud.get_or_create_user(
            session,
            user_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            referrer_id=referrer_id,
        )
        await session.commit()

        if is_new:
            text = (
                "👋 Xush kelibsiz!\n\n"
                "Sizga 0 Coin taqdim etildi. Kunlik bonus olishni unutmang!\n"
                "Asosiy menyudan kerakli bo'limni tanlang."
            )
        else:
            text = "👋 Yana salom! Asosiy menyu:"

    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(text, reply_markup=main_menu(is_admin=is_admin))