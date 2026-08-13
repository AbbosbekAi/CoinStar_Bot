# api_handlers.py
from aiohttp import web
from sqlalchemy import select
from database.engine import SessionLocal
from database.models import User   # <-- Modelingizning nomini tekshiring!


async def handle_balance(request):
    """GET /api/balance?user_id=123"""
    user_id = request.query.get('user_id')
    if not user_id:
        return web.json_response({'success': False, 'message': 'user_id kerak'}, status=400)

    async with SessionLocal() as session:
        stmt = select(User.balance).where(User.telegram_id == int(user_id))
        result = await session.execute(stmt)
        balance = result.scalar_one_or_none()
        if balance is None:
            balance = 0
        return web.json_response({'success': True, 'balance': balance})


async def handle_click(request):
    """POST /api/click - body: { "user_id": 123, "clicks": 1 }"""
    try:
        data = await request.json()
        user_id = data.get('user_id')
        clicks = int(data.get('clicks', 1))
        if not user_id:
            return web.json_response({'success': False, 'message': 'user_id kerak'}, status=400)

        async with SessionLocal() as session:
            user = await session.get(User, int(user_id))
            if not user:
                user = User(telegram_id=int(user_id), balance=0)
                session.add(user)
            user.balance += clicks
            await session.commit()
            new_balance = user.balance

        return web.json_response({'success': True, 'new_balance': new_balance})
    except Exception as e:
        return web.json_response({'success': False, 'message': str(e)}, status=500)