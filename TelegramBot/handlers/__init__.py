from aiogram import Dispatcher

from .user import setup as user_setup


def setup(main_dp: Dispatcher):
    user_setup(main_dp)
