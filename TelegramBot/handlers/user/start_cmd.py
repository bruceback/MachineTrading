import asyncio
import datetime
import os

from aiogram import Router, types, F
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.filters import Command, ContentTypesFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
import config
import loader
from loader import log

from utils.states import UserMain

dp = Router()


def generate_markup(data) -> types.InlineKeyboardMarkup:
    key = InlineKeyboardBuilder()
    i = 0
    for item in data:
        key.button(text=item, callback_data=f'{i}')
        i += 1
    key.adjust(1)
    return key.as_markup()


async def portfolio_output(text, message):
    buttons = loader.stocks
    key = generate_markup(buttons)
    await message.answer(text, reply_markup=key)


@dp.message(Command(commands='start'), state='*')
async def start_cmd(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    await message.answer(config.GREETINGS)


@dp.message(commands=['portfolio', 'prediction', 'trading'])
async def view_portfolio(message: types.Message, state: FSMContext):
    text = 'here is your portfolio!'
    if message.text == '/trading':
        text += ' Choose a stock to trade'
    elif message.text == '/prediction':
        text += ' Choose a stock to predict'
    await portfolio_output(text, message)
    await state.set_state(UserMain.stock_output)


@dp.callback_query(F.data, UserMain.stock_output)
async def driving_fine_choice(call: types.CallbackQuery, state: FSMContext):
    text = 'Chosen stock: ' + loader.stocks[int(call.data)] + '\nStock info:\n' + config.STOCK_INFO + '\n' + config.PREDICTION + '\n'+ config.POSITIVE_ADVICE
    buttons = loader.actions
    key = generate_markup(buttons)
    await call.message.answer(text, reply_markup=key)
    await state.set_state(UserMain.stock_action)


@dp.callback_query(F.data == '0', UserMain.stock_action)
async def fine_cancel_another_reason(call: types.CallbackQuery, state: FSMContext):
    text = 'Stock is sold!'
    await call.message.answer(text)
    await state.clear()


@dp.callback_query(F.data == '1', UserMain.stock_action)
async def fine_cancel_call_cancel(call: types.CallbackQuery, state: FSMContext):
    text = 'Stock is bought!'
    await call.message.answer(text)
    await state.clear()


@dp.callback_query(F.data == '2', UserMain.stock_action)
async def fine_cancel_call_cancel(call: types.CallbackQuery, state: FSMContext):
    text = 'Operation was not approved'
    await call.message.answer(text)
    await state.clear()
