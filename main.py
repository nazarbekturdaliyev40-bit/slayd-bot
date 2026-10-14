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

from aiohttp import web
import os

async def start_web_server():
    port = int(os.getenv("PORT", "10000"))
    app = web.Application()
    async def handle_ping(request):
        return web.Response(text="Bot is running 24/7!")
    app.router.add_get("/", handle_ping)
    app.router.add_get("/health", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logger.info(f"Healthcheck veb-server 0.0.0.0:{port} da ishga tushdi.")

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
    # 1. Render uchun veb-serverni eng birinchi navbatda ishga tushiramiz
    try:
        await start_web_server()
    except Exception as e:
        logger.error(f"Veb-serverni ishga tushirishda xatolik: {e}")

    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN aniqlanmadi! .env faylini tekshiring.")
        return
    if not config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY kiritilmagan! Slayd generatsiyasi ishlamasligi mumkin.")

    # Init SQLite DB
    try:
        await database.init_db()
        logger.info("Ma'lumotlar bazasi tayyorlandi.")
    except Exception as e:
        logger.error(f"Baza xatoligi: {e}")

    # Bot & Dispatcher
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(router)

    try:
        await setup_bot_commands(bot)
    except Exception as e:
        logger.warning(f"Menu o'rnatish xatoligi: {e}")

    logger.info("Bot muvaffaqiyatli ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
