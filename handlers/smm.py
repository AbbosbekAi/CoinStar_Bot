from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
import math

from database.engine import SessionLocal
from database.models import Service, Order
from database import crud
from services.smm_api import send_order
from keyboards.inline import smm_services_kb, back_to_main, cancel_kb
from states import OrderState

router = Router()


@router.callback_query(F.data == "smm_services")
async def list_services(callback: CallbackQuery):
    async with SessionLocal() as session:
        result = await session.execute(
            select(Service).where(Service.is_active == True).order_by(Service.category, Service.id)
        )
        services = result.scalars().all()

        if not services:
            await callback.message.edit_text(
                "Hozircha xizmatlar mavjud emas.",
                reply_markup=back_to_main()
            )
            return

        await callback.message.edit_text(
            "🛒 Xizmatni tanlang:",
            reply_markup=smm_services_kb(services)
        )


@router.callback_query(F.data.startswith("service:"))
async def service_selected(callback: CallbackQuery, state: FSMContext):
    try:
        service_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Xatolik", show_alert=True)
        return

    async with SessionLocal() as session:
        service = await session.get(Service, service_id)

    if not service:
        await callback.answer("Xizmat topilmadi", show_alert=True)
        return

    await state.update_data(
        service_id=service.id,
        service_name=service.name,
        price_per_1000=service.price_per_1000,
    )

    await callback.message.answer(
        f"Tanlangan: {service.name}\n\nHavolani yuboring (http/https):",
        reply_markup=cancel_kb()
    )
    await state.set_state(OrderState.link)
    await callback.answer()


@router.message(OrderState.link)
async def order_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("http://") or link.startswith("https://")):
        await message.answer("Iltimos to'g'ri URL yuboring (http/https)", reply_markup=cancel_kb())
        return

    await state.update_data(link=link)
    await message.answer("Soni (quantity) kiriting:", reply_markup=cancel_kb())
    await state.set_state(OrderState.quantity)


@router.message(OrderState.quantity)
async def order_quantity(message: Message, state: FSMContext):
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer("Iltimos butun son kiriting", reply_markup=cancel_kb())
        return

    if quantity <= 0:
        await message.answer("Soni musbat bo'lishi kerak", reply_markup=cancel_kb())
        return

    data = await state.get_data()
    service_id = data.get("service_id")
    link = data.get("link")

    async with SessionLocal() as session:
        service = await session.get(Service, service_id)
        if not service:
            await message.answer("Xizmat topilmadi", reply_markup=back_to_main())
            await state.clear()
            return

        if quantity < service.min_quantity or quantity > service.max_quantity:
            await message.answer(
                f"Soni {service.min_quantity}-{service.max_quantity} oralig'ida bo'lishi kerak",
                reply_markup=cancel_kb()
            )
            return

        # Narxni hisoblash: panel narxi + marja
        base_price = (quantity / 1000) * service.price_per_1000
        api_url, api_key, margin_percent = await crud.get_smm_settings(session)
        total_price = int(math.ceil(base_price * (1 + margin_percent / 100)))

        user = await crud.get_user(session, message.from_user.id)
        if not user:
            await message.answer("Foydalanuvchi topilmadi", reply_markup=back_to_main())
            await state.clear()
            return

        if user.coins < total_price:
            await message.answer(
                f"Balans yetarli emas.\nNarx: {total_price} Coin\nBalansingiz: {user.coins} Coin",
                reply_markup=back_to_main()
            )
            await state.clear()
            return

        # Coin yechib olish va buyurtma yaratish
        user.coins -= total_price
        order = Order(
            user_id=user.id,
            service_id=service.id,
            link=link,
            quantity=quantity,
            price=total_price,
            status="pending",
        )
        session.add(order)
        await session.flush()

        # SMM panelga yuborish
        result, error = await send_order(
            service.service_code,
            link,
            quantity,
            api_url=api_url,
            api_key=api_key,
        )

        if error or not result or (isinstance(result, dict) and result.get("error")):
            # Xatolik bo'lsa, mablag'ni qaytarish
            user.coins += total_price
            order.status = "error"
            await session.commit()

            error_text = error or (result.get("error") if isinstance(result, dict) else "Noma'lum xato")
            await message.answer(
                f"❌ Buyurtma xatosi: {error_text}\nMablag' qaytarildi.",
                reply_markup=back_to_main()
            )
            await state.clear()
            return

        # Muvaffaqiyatli buyurtma
        order.status = "processing"
        if isinstance(result, dict):
            order.api_order_id = str(result.get("order", ""))
        await session.commit()

        await message.answer(
            f"✅ Buyurtma qabul qilindi!\n\n"
            f"Xizmat: {service.name}\n"
            f"Havola: {link}\n"
            f"Soni: {quantity}\n"
            f"Narx: {total_price} Coin\n"
            f"API buyurtma ID: {order.api_order_id}",
            reply_markup=back_to_main()
        )
        await state.clear()


@router.callback_query(F.data == "cancel_order")
async def cancel_order_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Bekor qilindi", reply_markup=back_to_main())