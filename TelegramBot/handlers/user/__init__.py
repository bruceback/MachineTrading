from aiogram import Dispatcher

from .start_cmd import dp as start_dp


def setup(main_dp: Dispatcher):
    main_dp.include_router(start_dp)
