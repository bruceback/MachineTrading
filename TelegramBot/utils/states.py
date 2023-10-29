from aiogram.dispatcher.fsm.state import State, StatesGroup


class UserMain(StatesGroup):
    portfolio_output = State()
    stock_output = State()
    stock_action = State()
    fine_cancel_msg = State()
    date_fine = State()
    date_decree = State()
    number_fine = State()
    datetime_decree = State()
    content = State()
    name = State()
    address = State()
    phone_number = State()
    email = State()
