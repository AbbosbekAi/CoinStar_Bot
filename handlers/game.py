# handlers/game.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

router = Router()

@router.message(Command("game"))
async def cmd_game(message: types.Message):
    # Bu URL – sizning index.html joylashgan manzil (Vercel/Netlify)
    WEBAPP_URL = "https://sizning-mini-app-manzilingiz.vercel.app"
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="🎮 O‘yinni ochish",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )]
        ]
    )
    await message.answer(
        "💰 Coin Clicker o‘yiniga xush kelibsiz!\n"
        "Tugmani bosing va coin yig‘ing. Har bir bosish uchun 1 coin qo‘shiladi.",
        reply_markup=keyboard
    )