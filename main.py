import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

import config
import database
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

async def main():
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! .env faylini tekshiring.")
        return
    if not config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY kiritilmagan! Slayd generatsiyasi ishlamasligi mumkin.")

    # Init SQLite DB
    await database.init_db()
    logger.info("Ma'lumotlar bazasi tayyorlandi.")

    # Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
