# Slayd Yasovchi Telegram Bot (AI PowerPoint & PDF Generator)

Sun'iy intellekt (Google Gemini) yordamida rasmlar va ma'lumotlar bilan boyitilgan professional taqdimotlar (`.pptx`) hamda tayyor (`.pdf`) fayllar tayyorlovchi Telegram bot.

## Imkoniyatlar:
- 🎁 **2 ta bepul limit**: Har bir yangi foydalanuvchiga 2 ta bepul taqdimot beriladi.
- 💳 **Tariflar**: 2 ta bepul limitdan keyin: 1 ta taqdimot — **5 000 so'm**, oylik cheksiz obuna — **20 000 so'm**.
- 🖼 **Rasmni PDF ga aylantirish**: Botga rasm yoki bir nechta rasmlar tashlansa, darhol sifatli PDF qilib beradi.
- 📊 **PowerPoint (.pptx)**: 16:9 formatdagi, tahrirlash uchun qulay taqdimot fayli.
- 📑 **PDF (.pdf)**: Barcha slaydlar, rasmlar va ma'lumotlar bilan tayyor PDF taqdimot fayli.
- 🖼 **Mavzuga mos rasmlar**: Har bir slaydga va muqovaga avtomatik tarzda mavzuga oid sifatli rasmlar joylashtiriladi.
- 🎙 **Spiker nutqi (Speaker notes)**: Har bir slayd ostida taqdimotchi nima deb gapirishi kerakligi yozilgan bo'ladi.
- 👥 **Referal tizimi**: Do'stlarni taklif qilish orqali bepul limitlar olish imkoniyati.
- ⚙️ **Admin boshqaruvi**: Adminga statistika (`/stats`), limit qo'shish (`/add_limit <id> <soni>`) va oylik obuna faollashtirish (`/add_sub <id> [kun]`).

## O'rnatish va Ishga tushirish:

1. `.env` faylini oching va ma'lumotlarni kiriting:
   - `BOT_TOKEN`: @BotFather dan olingan token
   - `GEMINI_API_KEY`: Google AI Studio dan olingan kalit
   - `ADMIN_ID`: O'zingizning Telegram ID raqamingiz
   - `CARD_NUMBER`: To'lov qabul qiladigan karta raqami

2. Botni ishga tushirish:
   ```bash
   ./run.sh
   ```
   yoki:
   ```bash
   source venv/bin/activate
   python main.py
   ```
