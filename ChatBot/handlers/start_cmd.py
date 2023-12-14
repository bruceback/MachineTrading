from aiogram import Router, types, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from MoexML.moex_api.securities import find_on_moex, get_history, get_current_price, get_portfolio_price
from MoexML.ml_models.auto_ts import get_prediction
from MoexML.preprocessing.stock_history import prepare_history
from DataBase.controllers import add_user, get_portfolio, add_trading_record, deposit, get_user
from DataBase import get_connection

import ChatBot.config as config
from loguru import logger as log

from ChatBot.utils.states import UserMain

dp = Router()
connection = get_connection()

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
    global variables, connection

    user_id = message.from_user.id
    add_user(str(user_id), connection)

    await initialize_vars(user_id)
    await message.answer(config.GREETINGS)


@dp.message(Command(commands=['portfolio']))
async def view_portfolio(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    text = ''
    user = get_user(str(user_id), connection)
    text += 'Balance: ' + str(round(user.balance, 2)) + '\n\n'
    portfolio = get_portfolio(str(user_id), connection)

    portfolio_yield = 0
    if user.all_deposits != 0:
        portfolio_yield = round((user.balance + get_portfolio_price(portfolio) - user.all_deposits) / user.all_deposits, 2)*100

    if not portfolio:
        text += config.EMPTY_PORTFOLIO  # portfolio is empty
    else:
        for key, value in portfolio.items():
            text += str(key) + ' : ' + str(value) + '\n'

    text += '\nYield: ' + str(portfolio_yield) + '%'
    await message.answer(text)
    await state.clear()


@dp.message(Command(commands=['deposit']))
async def fill_balance(message: types.Message, state: FSMContext):
    text = 'How much would you like to deposit?'
    await message.answer(text)
    await state.set_state(UserMain.input_deposit_num)


@dp.message(UserMain.input_deposit_num)
async def buy_sell_stock(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    total = message.text

    try:
        sum = float(total)
        deposit(str(user_id), sum, connection)
        text = config.SUCCESS_MESSAGE
        await message.answer(text)
        await state.clear()
    except ValueError:
        text = 'please, input a number:'
        await message.answer(text)
        await state.set_state(UserMain.stock_buy)
        return


@dp.message(Command(commands=['trading']))
async def trade(message: types.Message, state: FSMContext):
    text = 'input a name of a company or a stock:'
    await message.answer(text)
    await state.set_state(UserMain.stock_search_trading)


@dp.message(UserMain.stock_search_trading)
async def stock_research(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    log.info(variables)

    stock = message.text
    await message.answer('Search is in progress...')

    log.info(stock)
    result = find_on_moex(stock)
    result = result[(result['engine'] == 'stock') & (result['market'] == 'shares')]
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
        await state.set_state(UserMain.stock_info_output)


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
async def stock_input(call: types.CallbackQuery, state: FSMContext):
    text = 'input a name of a company or a stock:'
    await call.message.answer(text)
    await state.set_state(UserMain.stock_search_prediction)


@dp.message(UserMain.stock_search_prediction)
async def stock_research(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    log.info(variables)

    stock = message.text
    await message.answer('Search is in progress...')

    log.info(stock)
    result = find_on_moex(stock)
    result = result[(result['engine'] == 'stock') & (result['market'] == 'shares')]

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


@dp.callback_query(UserMain.stock_info_output)
async def stock_info_output(call: types.CallbackQuery, state: FSMContext):
    global variables
    user_id = call.from_user.id

    variables[user_id]['primary_boardid'] = variables[user_id]["stocks"][int(call.data)]
    stock_name = variables[user_id]['primary_boardid']

    # get price of stock function
    stock_price = get_current_price(stock_name, 'stock', 'shares')

    text = f'The prise of {stock_name} is {stock_price}\n\nWhat to do next:'
    key = generate_markup(['buy', 'sell', 'pass'])
    await call.message.answer(text, reply_markup=key)
    await state.set_state(UserMain.stock_actions)


@dp.callback_query(F.data == '2', UserMain.stock_actions)
async def buy_sell_stock(call: types.CallbackQuery, state: FSMContext):
    global variables
    user_id = call.from_user.id

    text = 'You aborted the operation!'
    await call.message.answer(text)
    await state.clear()


@dp.callback_query(F.data == '0', UserMain.stock_actions)
async def buy_sell_stock(call: types.CallbackQuery, state: FSMContext):
    global variables
    user_id = call.from_user.id

    text = 'Input the number of shares to buy:'
    await call.message.answer(text)
    await state.set_state(UserMain.stock_buy)


@dp.callback_query(F.data == '1', UserMain.stock_actions)
async def buy_sell_stock(call: types.CallbackQuery, state: FSMContext):
    global variables
    user_id = call.from_user.id

    text = 'Input the number of shares to sell:'
    await call.message.answer(text)
    await state.set_state(UserMain.stock_sell)


@dp.message(UserMain.stock_buy)
async def buy_sell_stock(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    shares_number = message.text
    stock_name = variables[user_id]['primary_boardid']
    stock_price = get_current_price(stock_name, 'stock', 'shares')

    try:
        num = int(shares_number)
        try:
            add_trading_record(str(user_id), variables[user_id]['primary_boardid'], num, stock_price, connection)
            text = config.SUCCESS_MESSAGE
            await message.answer(text)
            await state.clear()
        except Exception as e:
            await message.answer(str(e))
            await state.clear()

    except ValueError:
        text = 'please, input a number:'
        await message.answer(text)
        await state.set_state(UserMain.stock_buy)
        return


@dp.message(UserMain.stock_sell)
async def buy_sell_stock(message: types.Message, state: FSMContext):
    global variables
    user_id = message.from_user.id
    shares_number = message.text
    stock_name = variables[user_id]['primary_boardid']
    stock_price = get_current_price(stock_name, 'stock', 'shares')

    try:
        num = int(shares_number)
        try:
            add_trading_record(str(user_id), variables[user_id]['primary_boardid'], num*(-1), stock_price, connection)
            text = config.SUCCESS_MESSAGE
            await message.answer(text)
            await state.clear()
        except Exception as e:
            await message.answer(str(e))
            await state.clear()

    except ValueError:
        text = 'please, input a number:'
        await message.answer(text)
        await state.set_state(UserMain.stock_buy)
        return
