import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from aiogram.types import BotCommand, BotCommandScopeDefault

import config
import database
from handlers import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

async def setup_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🚀 Botni ishga tushirish"),
        BotCommand(command="yangi_slayd", description="📊 Yangi slayd tayyorlash"),
        BotCommand(command="profil", description="👤 Mening profilim"),
        BotCommand(command="limit", description="💳 Limit va Obuna"),
        BotCommand(command="murojaat", description="👨‍💻 Adminga murojaat"),
        BotCommand(command="haqida", description="ℹ️ Bot haqida"),
    ]
    try:
        await bot.set_my_commands(commands, scope=BotCommandScopeDefault())
        logger.info("Bot buyruqlari (Menu) muvaffaqiyatli o'rnatildi.")
    except Exception as e:
        logger.warning(f"Bot buyruqlarini o'rnatishda xatolik: {e}")

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

    await setup_bot_commands(bot)

    logger.info("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
