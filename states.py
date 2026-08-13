from aiogram.fsm.state import State, StatesGroup

class OrderState(StatesGroup):
    link = State()
    quantity = State()

class WithdrawState(StatesGroup):
    amount = State()