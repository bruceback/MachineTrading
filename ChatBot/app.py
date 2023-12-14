import asyncio

from aiogram import Dispatcher
from aiogram.fsm.strategy import FSMStrategy
import nest_asyncio
from loguru import logger as log

from ChatBot.loader import bot
from ChatBot.handlers import start_cmd

nest_asyncio.apply()

global connection


@log.catch()
async def main():
    global connection

    main_dp = Dispatcher(fsm_strategy=FSMStrategy.USER_IN_CHAT)
    main_dp.include_router(start_cmd.dp)
    # connection.close()

    log.info('Бот запущен')
    await bot.delete_webhook(drop_pending_updates=True)
    await main_dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
