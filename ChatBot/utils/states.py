from aiogram.fsm.state import StatesGroup, State


class UserMain(StatesGroup):
    portfolio_output = State()
    stock_output = State()
    stock_action = State()
    stock_search = State()
    stock_history = State()
    start_prediction = State()
