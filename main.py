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

import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Bot is running 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        # Don't clutter logs with pings
        pass

def start_health_server():
    port = int(os.environ.get("PORT", 10000))
    try:
        server = HTTPServer(("0.0.0.0", port), HealthHandler)
        logger.info(f"Healthcheck veb-server 0.0.0.0:{port} da bir zumda ishga tushdi.")
        server.serve_forever()
    except Exception as e:
        logger.error(f"Health server xatosi: {e}")

# Python ishga tushishi bilanoq fonda portni darhol ochamiz
threading.Thread(target=start_health_server, daemon=True).start()

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
        logger.error("DIQQAT: BOT_TOKEN aniqlanmadi! Render Environment Variables bo'limiga BOT_TOKEN qo'shing.")
        while True:
            await asyncio.sleep(3600)

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

    logger.info("Bot polling ishga tushmoqda...")
    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            logger.error(f"Telegram polling to'xtadi yoki xatolik: {e}. 5 soniyada qayta ulanadi...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
