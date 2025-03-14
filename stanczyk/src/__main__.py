from asyncio import run
import logging
import sys

from aiogram import Bot, Dispatcher

from . import load_token
from .handlers import router


async def main():
    dp = Dispatcher()
    bot = Bot(token=load_token())
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    run(main())
