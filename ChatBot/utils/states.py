from aiogram.fsm.state import StatesGroup, State


class UserMain(StatesGroup):
    portfolio_output = State()
    stock_output = State()
    stock_search_prediction = State()
    stock_search_trading = State()
    stock_history = State()
    start_prediction = State()
    stock_info_output = State()
    stock_actions = State()
    stock_buy = State()
    stock_sell = State()
    input_deposit_num = State()