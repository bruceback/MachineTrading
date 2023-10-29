import asyncio

from aiogram import Dispatcher
import nest_asyncio

from loader import bot, log
import handlers


nest_asyncio.apply()


@log.catch()
async def main():
    main_dp = Dispatcher()
    handlers.setup(main_dp)
    log.info('Бот запущен')
    await bot.delete_webhook(drop_pending_updates=True)
    await main_dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
