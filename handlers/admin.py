from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, func

from database.engine import SessionLocal
from database.models import WithdrawalRequest, Service
from database import crud
from config import ADMIN_IDS
from keyboards.inline import back_to_main, admin_menu_kb

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


@router.callback_query(F.data == "admin_panel")
async def admin_panel_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    await callback.message.edit_text(
        "👑 Admin panel\n\n"
        "Buyruqlar:\n"
        "/stats - statistika\n"
        "/add_coins user_id amount - coin qo'shish/ayirish\n"
        "/set_smm_api url key - SMM API sozlash\n"
        "/set_margin percent - marja foizi\n"
        "/add_service code name price_per_1000 - xizmat qo'shish",
        reply_markup=admin_menu_kb()
    )


@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("Ruxsat yo'q", show_alert=True)
        return

    async with SessionLocal() as session:
        users = await crud.get_user_count(session)
        orders = await crud.get_order_count(session)
        total_coins = await crud.get_total_coins(session)
        result = await session.execute(
            select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status == "pending")
        )
        pending = result.scalar_one()

    text = (
        f"📊 Statistika\n\n"
        f"Foydalanuvchilar: {users}\n"
        f"Buyurtmalar: {orders}\n"
        f"Jami Coin: {total_coins}\n"
        f"Kutilayotgan yechish: {pending}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main())


@router.message(Command("stats"))
async def stats_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with SessionLocal() as session:
        users = await crud.get_user_count(session)
        orders = await crud.get_order_count(session)
        total_coins = await crud.get_total_coins(session)
        result = await session.execute(
            select(func.count()).select_from(WithdrawalRequest).where(WithdrawalRequest.status == "pending")
        )
        pending = result.scalar_one()

    await message.answer(
        f"Foydalanuvchilar: {users}\n"
        f"Buyurtmalar: {orders}\n"
        f"Jami Coin: {total_coins}\n"
        f"Kutilayotgan yechish: {pending}"
    )


@router.message(Command("add_coins"))
async def add_coins_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Format: /add_coins user_id amount")
        return

    try:
        user_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("Noto'g'ri format. user_id va amount butun son bo'lishi kerak")
        return

    async with SessionLocal() as session:
        user = await crud.add_coins(session, user_id, amount, description=f"Admin {message.from_user.id}")
        await session.commit()

        if user:
            await message.answer(
                f"✅ {user_id} foydalanuvchiga {amount} Coin qo'shildi. Yangi balans: {user.coins}"
            )
        else:
            await message.answer("Foydalanuvchi topilmadi")


@router.message(Command("set_smm_api"))
async def set_smm_api_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=2)
    if len(parts) != 3:
        await message.answer("Format: /set_smm_api url key")
        return

    url, key = parts[1], parts[2]

    async with SessionLocal() as session:
        await crud.set_setting(session, "smm_api_url", url)
        await crud.set_setting(session, "smm_api_key", key)
        await session.commit()

    await message.answer("✅ SMM API sozlandi")


@router.message(Command("set_margin"))
async def set_margin_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Format: /set_margin percent")
        return

    try:
        margin = float(parts[1])
    except ValueError:
        await message.answer("Foizni raqamda kiriting")
        return

    async with SessionLocal() as session:
        await crud.set_setting(session, "smm_margin", str(margin))
        await session.commit()

    await message.answer(f"✅ Marja {margin}% qilib o'rnatildi")


@router.message(Command("add_service"))
async def add_service_cmd(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split(maxsplit=3)
    if len(parts) != 4:
        await message.answer("Format: /add_service code name price_per_1000")
        return

    code, name, price_str = parts[1], parts[2], parts[3]
    try:
        price = float(price_str)
    except ValueError:
        await message.answer("Narxni raqamda kiriting")
        return

    async with SessionLocal() as session:
        result = await session.execute(select(Service).where(Service.service_code == code))
        existing = result.scalar_one_or_none()
        if existing:
            await message.answer("Bu kod mavjud")
            return

        service = Service(service_code=code, name=name, price_per_1000=price, category="Boshqa")
        session.add(service)
        await session.commit()

    await message.answer("✅ Xizmat qo'shildi")