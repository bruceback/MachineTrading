from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from MoexML.moex_api.securities import find_on_moex, get_history
from MoexML.ml_models.auto_ts import get_prediction
from MoexML.preprocessing.stock_history import prepare_history
import ChatBot.config as config
from loguru import logger as log

from ChatBot.utils.states import UserMain

dp = Router()

global variables
variables = {}


def generate_markup(data) -> types.InlineKeyboardMarkup:
    key = InlineKeyboardBuilder()
    i = 0
    for item in data:
        key.button(text=item, callback_data=f'{i}')
        i += 1
    key.adjust(1)
    return key.as_markup()


async def initialize_vars(user_id):
    variables[user_id] = {"stocks": []}


@dp.message(Command(commands=["start"]))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    global variables

    user_id = message.from_user.id
    await initialize_vars(user_id)
    await message.answer(config.GREETINGS)


@dp.message(Command(commands=['prediction']))
async def view_portfolio(message: types.Message, state: FSMContext):
    global variables

    user_id = message.from_user.id
    if user_id not in variables:
        await initialize_vars(user_id)

    text = config.POLICY_AGREEMENT
    key = generate_markup(config.POLICY_AGREEMENT_BTN)
    await message.answer(text, reply_markup=key)
    await state.set_state(UserMain.start_prediction)


@dp.callback_query(F.data, UserMain.start_prediction)
async def view_portfolio(call: types.CallbackQuery, state: FSMContext):
    text = 'input a name of a company or a stock:'
    await call.message.answer(text)
    await state.set_state(UserMain.stock_search)


@dp.message(UserMain.stock_search)
async def stock_research(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    log.info(variables)

    stock = message.text
    await message.answer('Search is in progress...')

    log.info(stock)
    result = find_on_moex(stock)
    log.info(result)
    if result is None:
        text = config.SEARCH_ERROR
        await message.answer(text)
        await state.clear()
    else:
        variables[user_id]["stocks"] = list(result['secid'][:7])
        key = generate_markup(variables[user_id]["stocks"])
        text = config.SEARCH_RESULT
        await message.answer(text, reply_markup=key)
        await state.set_state(UserMain.stock_history)


@dp.callback_query(UserMain.stock_history)
async def stock_prediction(call: types.CallbackQuery, state: FSMContext):
    global variables
    user_id = call.from_user.id

    text = 'Retrieving the history of stock...'
    await call.message.answer(text)
    text = 'It can take some time. We kindly ask you to wait a few minutes)'
    await call.message.answer(text)
    stock_history = get_history(variables[user_id]["stocks"][int(call.data)], "stock", "shares")
    try:
        log.info(stock_history[:5])
    except Exception as e:
        await call.message.answer(config.HISTORY_ERROR)

    text = 'Preparing the data for the analysis...'
    await call.message.answer(text)
    dataset = prepare_history(stock_history)

    text = 'Analyzing the data...'
    await call.message.answer(text)

    text = 'It can take up to 5 mins'
    await call.message.answer(text)

    try:
        prediction = get_prediction(dataset, "TRADEDATE", "WAPRICE")
        text = str(prediction.forecast)
        await call.message.answer('Here\'s the prediction of the stock:\n' + text)
        await call.message.answer('Call /prediction to get another forecast')
    except Exception as e:
        await call.message.answer(config.DATA_ERROR)

    await state.clear()

