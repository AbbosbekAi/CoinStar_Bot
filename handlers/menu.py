from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from database.engine import SessionLocal
from database import crud
from database.models import WithdrawalRequest
from config import ADMIN_IDS, BOT_USERNAME, DAILY_BONUS_AMOUNT, REFERRAL_BONUS_AMOUNT, MIN_WITHDRAW
from keyboards.inline import main_menu, back_to_main
from states import WithdrawState

router = Router()


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    is_admin = callback.from_user.id in ADMIN_IDS
    await callback.message.edit_text("Asosiy menyu:", reply_markup=main_menu(is_admin=is_admin))


@router.callback_query(F.data == "balance")
async def balance_callback(callback: CallbackQuery):
    async with SessionLocal() as session:
        user = await crud.get_user(session, callback.from_user.id)
        if user:
            await callback.message.edit_text(
                f"💰 Balansingiz: {user.coins} Coin",
                reply_markup=back_to_main()
            )
        else:
            await callback.answer("Foydalanuvchi topilmadi", show_alert=True)


@router.callback_query(F.data == "daily_bonus")
async def daily_bonus_callback(callback: CallbackQuery):
    async with SessionLocal() as session:
        success = await crud.claim_daily_bonus(session, callback.from_user.id)
        await session.commit()

    if success:
        await callback.answer(f"{DAILY_BONUS_AMOUNT} Coin qo'shildi!", show_alert=True)
    else:
        await callback.answer("Bugun bonus allaqachon olingan", show_alert=True)


@router.callback_query(F.data == "referral")
async def referral_callback(callback: CallbackQuery):
    bot_username = BOT_USERNAME or (await callback.bot.me()).username
    link = f"https://t.me/{bot_username}?start=ref_{callback.from_user.id}"

    async with SessionLocal() as session:
        user = await crud.get_user(session, callback.from_user.id)
        count = user.referred_count if user else 0

    text = (
        f"👥 Do'stlarni taklif qiling!\n\n"
        f"Havola: {link}\n\n"
        f"Har bir do'st uchun {REFERRAL_BONUS_AMOUNT} Coin olasiz.\n"
        f"Siz taklif qilgan do'stlar: {count}"
    )
    await callback.message.edit_text(text, reply_markup=back_to_main())


@router.callback_query(F.data == "withdraw")
async def withdraw_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Yechib olish miqdorini kiriting (Coin):")
    await state.set_state(WithdrawState.amount)
    await callback.answer()


@router.message(WithdrawState.amount)
async def withdraw_amount(message: Message, state: FSMContext):
    try:
        amount = int(message.text)
    except ValueError:
        await message.answer("Iltimos butun son kiriting")
        return

    if amount < MIN_WITHDRAW:
        await message.answer(f"Minimal yechish miqdori: {MIN_WITHDRAW} Coin")
        return

    async with SessionLocal() as session:
        user = await crud.get_user(session, message.from_user.id)
        if not user:
            await message.answer("Foydalanuvchi topilmadi")
            await state.clear()
            return

        if user.coins < amount:
            await message.answer("Balans yetarli emas")
            await state.clear()
            return

        user.coins -= amount
        session.add(WithdrawalRequest(user_id=user.id, amount=amount))
        await session.commit()

        # Adminlarga xabar berish
        for admin_id in ADMIN_IDS:
            try:
                await message.bot.send_message(
                    admin_id,
                    f"📤 Yechish so'rovi: {message.from_user.full_name} ({message.from_user.id}) - {amount} Coin"
                )
            except Exception:
                pass

    await message.answer(
        "So'rovingiz qabul qilindi. Admin tasdiqlashini kuting.",
        reply_markup=back_to_main()
    )
    await state.clear()