import asyncio
import logging
import sys
import aiohttp
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.exceptions import TelegramNetworkError

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

THEMES_HTML = """<!DOCTYPE html>
<html lang="uz">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>PowerPoint 2016 Shablonlari</title>
  <script src="https://telegram.org/js/telegram-web-app.js"></script>
  <style>
    :root {
      --bg: #0f172a;
      --card-bg: #1e293b;
      --text: #f8fafc;
      --accent: #38bdf8;
    }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: var(--bg);
      color: var(--text);
      margin: 0;
      padding: 16px;
    }
    h1 {
      font-size: 20px;
      text-align: center;
      margin-bottom: 6px;
    }
    p.subtitle {
      font-size: 13px;
      color: #94a3b8;
      text-align: center;
      margin-top: 0;
      margin-bottom: 18px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 12px;
    }
    .theme-card {
      background: var(--card-bg);
      border: 2px solid #334155;
      border-radius: 12px;
      padding: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
    }
    .theme-card:hover, .theme-card:active {
      border-color: var(--accent);
      transform: translateY(-2px);
    }
    .color-preview {
      width: 100%;
      height: 52px;
      border-radius: 8px;
      margin-bottom: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 22px;
      box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .theme-name {
      font-size: 14px;
      font-weight: 600;
      margin-bottom: 4px;
    }
    .theme-desc {
      font-size: 11px;
      color: #94a3b8;
    }
  </style>
</head>
<body>
  <h1>PowerPoint 2016 Shablonlari</h1>
  <p class="subtitle">Oʻzingizga maʼqul shablon ustiga bosing:</p>
  <div class="grid" id="themesGrid"></div>

  <script>
    const tg = window.Telegram?.WebApp;
    if (tg) {
      tg.ready();
      tg.expand();
    }
    const themes = [
      { id: "mix", name: "PPT 2016 Mix", desc: "Xar xil aralash shablon", icon: "🔀", bg: "linear-gradient(135deg, #1f4e79, #104b3c, #721c34)" },
      { id: "facet", name: "Facet 2016", desc: "Zumrad geometrik", icon: "🟢", bg: "linear-gradient(135deg, #104b3c, #10b981)" },
      { id: "ion", name: "Ion 2016", desc: "Bordo sharob tusli", icon: "🔴", bg: "linear-gradient(135deg, #721c34, #f97316)" },
      { id: "slice", name: "Slice 2016", desc: "Kesimli neo kiber", icon: "🔷", bg: "linear-gradient(135deg, #1e293b, #06b6d4)" },
      { id: "celestial", name: "Celestial 2016", desc: "Tungi koinot moviy", icon: "🌌", bg: "linear-gradient(135deg, #0a193c, #eab308)" },
      { id: "integral", name: "Integral 2016", desc: "Muhandislik terrakota", icon: "📐", bg: "linear-gradient(135deg, #21405f, #eb5e3c)" },
      { id: "retrospect", name: "Retrospect 2016", desc: "Retro oltin qum", icon: "🏺", bg: "linear-gradient(135deg, #582f17, #d97706)" },
      { id: "droplet", name: "Droplet 2016", desc: "Yumshoq tomchi akva", icon: "💧", bg: "linear-gradient(135deg, #0d5c63, #14b8a6)" },
      { id: "savon", name: "Savon 2016", desc: "Aristokrat shampan", icon: "📜", bg: "linear-gradient(135deg, #44403c, #d97706)" },
      { id: "circuit", name: "Circuit 2016", desc: "Kiber texno qora", icon: "⚡️", bg: "linear-gradient(135deg, #0f172a, #06b6d4)" },
      { id: "office", name: "Office 2016", desc: "Klassik moviy oq", icon: "🏢", bg: "linear-gradient(135deg, #1f4e79, #2f75b5)" },
      { id: "white", name: "Minimal Oq", desc: "Toza oq & moviy", icon: "⚪️", bg: "#f8fafc" },
      { id: "dark", name: "Premium Dark", desc: "Qora & oltin jilo", icon: "🖤", bg: "#18181b" },
      { id: "canva_pastel", name: "Canva Pastel", desc: "Nafis pushti binafsha", icon: "🌸", bg: "linear-gradient(135deg, #4f46e5, #ec4899)" },
      { id: "vintage", name: "Pergament", desc: "Antikvar pergament", icon: "📜", bg: "linear-gradient(135deg, #432818, #c2892c)" }
    ];

    const container = document.getElementById("themesGrid");
    themes.forEach(t => {
      const card = document.createElement("div");
      card.className = "theme-card";
      card.innerHTML = `
        <div class="color-preview" style="background: ${t.bg}">${t.icon}</div>
        <div class="theme-name">${t.name}</div>
        <div class="theme-desc">${t.desc}</div>
      `;
      card.onclick = () => {
        if (tg) {
          tg.sendData(t.id);
        } else {
          alert("Tanlandi: " + t.name);
        }
      };
      container.appendChild(card);
    });
  </script>
</body>
</html>
"""

class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/themes"):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(THEMES_HTML.encode("utf-8"))
            return

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
        BotCommand(command="start", description="🚀 Qayta ishga tushirish / Start"),
        BotCommand(command="slayd", description="📊 Slayd tayyorlash / Create slides"),
        BotCommand(command="lang", description="🌐 Tilni o'zgartirish / Language"),
        BotCommand(command="profil", description="👤 Profil / Profile"),
        BotCommand(command="fayllarim", description="📁 Mening fayllarim / My files"),
        BotCommand(command="tariffs", description="💳 Tariflar / Plans"),
        BotCommand(command="haqida", description="ℹ️ Bot haqida / About"),
        BotCommand(command="murojaat", description="👨‍💻 Adminga murojaat / Contact"),
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
        while True:
            try:
                try:
                    await setup_bot_commands(bot)
                except Exception as e:
                    logger.warning(f"Menu o'rnatish xatoligi: {e}")

                logger.info("Bot polling ishga tushmoqda...")
                await dp.start_polling(bot)
                break
            except (TelegramNetworkError, aiohttp.ClientError, asyncio.TimeoutError) as net_err:
                logger.warning(f"Tarmoqqa ulanishda xatolik ({net_err}). 5 soniyadan so'ng qayta urinib ko'riladi...")
                await asyncio.sleep(5)
            except (KeyboardInterrupt, SystemExit):
                break
            except Exception as e:
                logger.error(f"Kutilmagan xatolik yuz berdi: {e}")
                await asyncio.sleep(5)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot to'xtatildi.")
