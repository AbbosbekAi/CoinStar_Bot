from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, Transaction, Service, Order, WithdrawalRequest, Setting
from config import DAILY_BONUS_AMOUNT, REFERRAL_BONUS_AMOUNT, SMM_API_URL, SMM_API_KEY, SMM_MARGIN_PERCENT


async def get_user(session: AsyncSession, user_id: int):
    return await session.get(User, user_id)


async def get_or_create_user(
    session: AsyncSession,
    user_id: int,
    username: str | None = None,
    full_name: str | None = None,
    referrer_id: int | None = None
):
    """Foydalanuvchini qaytaradi yoki yangi yaratadi. Referral bonus ham hisobga olinadi."""
    user = await session.get(User, user_id)
    if user:
        return user, False

    user = User(id=user_id, username=username, full_name=full_name or "")
    session.add(user)
    await session.flush()

    if referrer_id and referrer_id != user_id:
        referrer = await session.get(User, referrer_id)
        if referrer:
            referrer.coins += REFERRAL_BONUS_AMOUNT
            referrer.referred_count += 1
            session.add(Transaction(
                user_id=referrer_id,
                amount=REFERRAL_BONUS_AMOUNT,
                description="Referral bonus"
            ))
            user.referrer_id = referrer_id
            await session.flush()

    return user, True


async def add_coins(session: AsyncSession, user_id: int, amount: int, description: str = ""):
    """Foydalanuvchi balansiga coin qo'shadi yoki ayiradi (manfiy amount)."""
    user = await session.get(User, user_id)
    if not user:
        return None
    user.coins += amount
    session.add(Transaction(user_id=user_id, amount=amount, description=description))
    await session.flush()
    return user


async def claim_daily_bonus(session: AsyncSession, user_id: int) -> bool:
    """Kunlik bonusni beradi. Agar bugun olingan bo'lsa False qaytaradi."""
    user = await session.get(User, user_id)
    if not user:
        return False

    today = datetime.utcnow().date()
    if user.last_daily_bonus and user.last_daily_bonus.date() == today:
        return False

    user.last_daily_bonus = datetime.utcnow()
    user.coins += DAILY_BONUS_AMOUNT
    session.add(Transaction(user_id=user_id, amount=DAILY_BONUS_AMOUNT, description="Kunlik bonus"))
    await session.flush()
    return True


async def get_setting(session: AsyncSession, key: str):
    return await session.get(Setting, key)


async def set_setting(session: AsyncSession, key: str, value: str):
    setting = await session.get(Setting, key)
    if setting:
        setting.value = value
    else:
        setting = Setting(key=key, value=value)
        session.add(setting)
    await session.flush()
    return setting


async def get_smm_settings(session: AsyncSession):
    """SMM panel sozlamalarini qaytaradi: (url, key, margin%)."""
    url = await get_setting(session, "smm_api_url")
    key = await get_setting(session, "smm_api_key")
    margin = await get_setting(session, "smm_margin")

    return (
        url.value if url else SMM_API_URL,
        key.value if key else SMM_API_KEY,
        float(margin.value) if margin else SMM_MARGIN_PERCENT,
    )


async def get_user_count(session: AsyncSession):
    result = await session.execute(select(func.count()).select_from(User))
    return result.scalar_one()


async def get_order_count(session: AsyncSession):
    result = await session.execute(select(func.count()).select_from(Order))
    return result.scalar_one()


async def get_total_coins(session: AsyncSession):
    result = await session.execute(select(func.coalesce(func.sum(User.coins), 0)))
    return result.scalar_one()