from aiogram.dispatcher.fsm.state import State, StatesGroup


class UserMain(StatesGroup):
    portfolio_output = State()
    stock_output = State()
    stock_action = State()
    stock_search = State()
    stock_history = State()
    start_prediction = State()
