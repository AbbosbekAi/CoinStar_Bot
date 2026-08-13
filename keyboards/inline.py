from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Service


def main_menu(is_admin: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="💰 Balans", callback_data="balance")],
        [InlineKeyboardButton(text="🎁 Kunlik bonus", callback_data="daily_bonus")],
        [InlineKeyboardButton(text="👥 Do'stlarni taklif qilish", callback_data="referral")],
        [InlineKeyboardButton(text="🛒 SMM Xizmatlar", callback_data="smm_services")],
        [InlineKeyboardButton(text="📤 Pul yechish", callback_data="withdraw")],
    ]
    if is_admin:
        buttons.append([InlineKeyboardButton(text="👑 Admin panel", callback_data="admin_panel")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_to_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="main_menu")]
    ])


def cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_order")]
    ])


def smm_services_kb(services: list[Service]) -> InlineKeyboardMarkup:
    buttons = []
    for s in services:
        buttons.append([
            InlineKeyboardButton(
                text=f"{s.name} - {int(s.price_per_1000)} so'm/1000",
                callback_data=f"service:{s.id}"
            )
        ])
    buttons.append([InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats")],
        [InlineKeyboardButton(text="◀️ Asosiy menyu", callback_data="main_menu")],
    ])