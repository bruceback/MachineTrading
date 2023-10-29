from loguru import logger as log
from aiogram import Bot

from config import BOT_TOKEN

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

stocks = ['MSFT (Microsoft)',
          'AFLT (Аэрофлот)',
          'YNDX (Яндекс)',
          'TM (Toyota)',
          'IMOEX (Индекс МосБиржи)']

actions = ['sell',
           'buy',
           'skip']
