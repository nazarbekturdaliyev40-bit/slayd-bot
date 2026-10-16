# -*- coding: utf-8 -*-
"""
Localization module for slayd_bot.
Supports bot interface in Uzbek, Russian, and English.
Supports presentation generation in 8 languages (Uzbek, Russian, English, Turkish, Kazakh, Kyrgyz, Tajik, German).
"""

# Available Bot Interface Languages
INTERFACE_LANGUAGES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English"
}

# Supported Presentation Languages (used in AI generation and PowerPoint layout)
SLIDE_LANGUAGES = {
    "uz": {
        "name": "🇺🇿 O'zbekcha",
        "prompt": "o'zbek tili (lotin alifbosidagi toza, imlo xatolarisiz akademik va tushunarli o'zbek tili)",
        "agenda": "Reja",
        "conclusion": "Xulosa",
        "thanks": "E'tiboringiz uchun rahmat!",
        "references": "Foydalanilgan adabiyotlar",
        "done_by": "Bajardi",
        "accepted_by": "Qabul qildi",
        "intro_speaker": "Hurmatli ustoz va talabalar, ushbu taqdimot mavzusi:"
    },
    "ru": {
        "name": "🇷🇺 Русский",
        "prompt": "русский язык (грамотный, академический и современный литературный русский язык)",
        "agenda": "План презентации",
        "conclusion": "Заключение",
        "thanks": "Спасибо за внимание!",
        "references": "Список использованной литературы",
        "done_by": "Выполнил(а)",
        "accepted_by": "Принял(а)",
        "intro_speaker": "Уважаемые преподаватели и студенты, тема презентации:"
    },
    "en": {
        "name": "🇬🇧 English",
        "prompt": "English language (formal, clear, academic and concise American/British English)",
        "agenda": "Agenda & Outline",
        "conclusion": "Conclusion",
        "thanks": "Thank You for Your Attention!",
        "references": "References & Bibliography",
        "done_by": "Prepared by",
        "accepted_by": "Supervised by",
        "intro_speaker": "Dear professors and students, today's presentation topic is:"
    },
    "tr": {
        "name": "🇹🇷 Türkçe",
        "prompt": "Türkçe (akademik, akıcı, zengin ve profesyonel Türkçe)",
        "agenda": "Sunum Planı / İçindekiler",
        "conclusion": "Sonuç ve Değerlendirme",
        "thanks": "Dikkatiniz için Teşekkür Ederim!",
        "references": "Kaynakça",
        "done_by": "Hazırlayan",
        "accepted_by": "Danışman",
        "intro_speaker": "Sayın hocalarım ve değerli arkadaşlar, bugünkü sunum konusu:"
    },
    "kk": {
        "name": "🇰🇿 Қазақша",
        "prompt": "Қазақ тілі (академиялық, сауатты және әдеби қазақ тілі)",
        "agenda": "Жоспар",
        "conclusion": "Қорытынды",
        "thanks": "Назарларыңызға рақмет!",
        "references": "Пайдаланылған әдебиеттер тізімі",
        "done_by": "Орындаған",
        "accepted_by": "Тексерген",
        "intro_speaker": "Құрметті ұстаздар мен студенттер, бүгінгі тақырып:"
    },
    "ky": {
        "name": "🇰🇬 Кыргызча",
        "prompt": "Кыргыз тили (академиялык, так жана адабий кыргыз тили)",
        "agenda": "План",
        "conclusion": "Корутунду",
        "thanks": "Көңүл бурганыңыздарга чоң рахмат!",
        "references": "Колдонулган адабияттар",
        "done_by": "Аткарган",
        "accepted_by": "Кабыл алган",
        "intro_speaker": "Урматтуу агай-эжейлер жана студенттер, презентациянын темасы:"
    },
    "tg": {
        "name": "🇹🇯 Тоҷикӣ",
        "prompt": "Забони тоҷикӣ (академикӣ, адабӣ ва фаҳмо)",
        "agenda": "Нақшаи презентатсия",
        "conclusion": "Хулоса",
        "thanks": "Барои таваҷҷӯҳатон ташаккур!",
        "references": "Адабиёти истифодашуда",
        "done_by": "Иҷро кард",
        "accepted_by": "Қабул кард",
        "intro_speaker": "Устодони мӯҳтарам ва донишҷӯён, мавзӯи имрӯза:"
    },
    "de": {
        "name": "🇩🇪 Deutsch",
        "prompt": "Deutsche Sprache (akademisches, professionelles Hochdeutsch)",
        "agenda": "Inhaltsverzeichnis / Agenda",
        "conclusion": "Fazit und Ausblick",
        "thanks": "Vielen Dank für Ihre Aufmerksamkeit!",
        "references": "Literaturverzeichnis",
        "done_by": "Vorgelegt von",
        "accepted_by": "Betreuer",
        "intro_speaker": "Sehr geehrte Professoren und Kommilitonen, das Thema der Präsentation lautet:"
    }
}

# UI Translation dictionary
TEXTS = {
    "uz": {
        "choose_lang_title": "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>",
        "lang_changed": "✅ <b>Interfeys tili O'zbekchaga o'zgartirildi!</b>",
        "menu_new_slide": "📊 Slayd tayyorlash",
        "menu_pptx_to_pdf": "📄 PPTX ➡️ PDF",
        "menu_profile": "👤 Mening profilim",
        "menu_free_limit": "🎁 Bepul limit",
        "menu_tariffs": "💳 Tariflar",
        "menu_about": "ℹ️ Bot haqida",
        "menu_contact": "👨‍💻 Adminga murojaat",
        "menu_change_lang": "🌐 Tilni o'zgartirish",
        "menu_admin": "⚙️ Admin panel",
        "menu_stats": "📈 Statistika",
        "menu_placeholder": "Mavzu yozing yoki menyudan tanlang...",
        "photo_to_slides_btn": "📊 Shu rasmdan taqdimot yasash",
        "doc_to_slides_btn": "📊 Hujjatdan taqdimot yasash",
        "doc_to_pdf_btn": "📄 PPTX boʻlsa PDF ga aylantirish",
        "welcome": (
            "Assalomu alaykum, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — sun'iy intellekt (Google Gemini) yordamida professional taqdimotlar (<b>PowerPoint .pptx</b>) tayyorlovchi bot.\n\n"
            "✨ <b>Imkoniyatlar:</b>\n"
            "• 🌐 <b>Ko'p tilli slaydlar:</b> O'zbek, Rus, Ingliz va boshqa tillarda\n"
            "• 🎙 <b>Ovozli xabar:</b> Mavzuni audio tarzda aytsangiz, bot o'zi tushunib slayd tuzadi\n"
            "• 📚 <b>Konspekt va kitob:</b> Kitob beti yoki konspekt rasmini yuboring, bot slayd chiqarib beradi\n"
            "• 📄 <b>PPTX ➡️ PDF:</b> Taqdimot faylini sifatli PDF ga o'girish\n\n"
            "🎁 Sizda <b>{free_limit} ta bepul taqdimot</b> limiti mavjud!\n"
            "👥 Do'stlaringizni taklif qilib (har 2 ta do'st uchun <b>+1 ta limit</b>) bepul limit olishingiz mumkin.\n\n"
            "👇 Boshlash uchun <b>«📊 Slayd tayyorlash»</b> tugmasini bosing yoki toʻgʻridan-toʻgʻri ovoz/fayl yuboring:"
        ),
        "choose_slide_lang": "🌐 <b>Taqdimot qaysi tilda tayyorlansin?</b>\n\nQuyidagi kerakli tillardan birini tanlang: 👇",
        "prompt_topic": "✍️ <b>Taqdimot mavzusini yozib yuboring:</b>\n\n<i>Masalan: Sun'iy intellektning tibbiyotdagi o'rni va kelajagi</i>",
        "prompt_count": (
            "📌 Mavzu: <b>{topic}</b>\n"
            "🌐 Slayd tili: <b>{slide_lang}</b>\n\n"
            "📊 <b>Nechta slayd tayyorlansin?</b>\n"
            "Quyidagi tugmalardan birini tanlang yoki <b>oʻzingiz xohlagan sonni (5 dan 30 gacha)</b> yozib yuboring:\n"
            "<i>💡 Masalan: 7, 10, 12 yoki 15</i>"
        ),
        "prompt_author": (
            "✅ <b>{count} ta slayd</b> tanlandi!\n\n"
            "🎓 <b>1-slayd: Titul varaqasi uchun ma'lumotlar</b>\n"
            "<i>(OTM, fakultet, yoʻnalish, guruh, talaba va ilmiy rahbar)</i>\n\n"
            "Maʼlumotlarni tagma-tag yoki bir qatorda yozib yuborishingiz mumkin:\n"
            "💡 <i>Masalan:</i>\n"
            "OTM: TATU\n"
            "Fakultet: Dasturiy injiniring\n"
            "Guruh: 210-21\n"
            "Talaba: Nazarbek Turdaliyev\n"
            "O'qituvchi: Eshpolatov Ozodbek\n\n"
            "⏩ Agar maʼlumot kiritishni xohlamasangiz, <b>«O'tkazib yuborish»</b> tugmasini bosing:"
        ),
        "prompt_theme": (
            "🎨 <b>Slaydning orqa fonini (dizaynini) tanlang:</b>\n\n"
            "Oʻzingizga yoqqan orqa fon rangini tanlang yoki <b>oʻz fon rasmingizni</b> yuboring.\n"
            "Taqdimot aynan siz tanlagan fon asosida tayyorlanadi: 👇"
        ),
        "no_limit": (
            "⚠️ <b>Kechirasiz, sizda limitlar tugagan!</b>\n\n"
            "Siz yangi taqdimot yaratish uchun:\n"
            "1️⃣ <b>Limit yoki Oylik obuna xarid qilishingiz mumkin</b> (1 ta taqdimot — 5 000 so'm, oylik cheksiz — 20 000 so'm);\n"
            "2️⃣ <b>Do'stlaringizni taklif qiling</b> — har 2 ta yangi do'st uchun <b>+1 ta bepul limit</b> oling!"
        ),
        "cancel_btn": "❌ Bekor qilish",
        "cancelled": "❌ Amal bekor qilindi.",
        "skip_btn": "⏩ O'tkazib yuborish (Standart)",
        "share_btn": "↗️ Do'stlarga ulashish",
        "pptx_to_pdf_prompt": "📄 <b>PPTX faylingizni yuboring:</b>\n\nBot uni bir necha soniyada yuqori sifatli PDF formatga aylantirib beradi.",
        "image_to_pdf_prompt": "🖼 <b>PDF ga aylantirmoqchi boʻlgan rasmlarni yuboring:</b>\n\nBir yoki bir nechta rasm yuborishingiz mumkin.",
        "edit_in_powerpoint": "📊 PowerPoint-da tahrirlash (Online)",
        "get_pdf": "📄 PDF formatida olish",
        "speech_notes": "🎤 Himoya nutq matni",
        "bonus_limit": "🎁 Bepul limit olish (+1)",
        "profile_title": "👤 <b>Foydalanuvchi ma'lumotlari:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Tarif:</b>",
        "profile_limit": "✨ <b>Mavjud limit:</b>",
        "profile_total": "📊 <b>Jami yaratilgan slaydlar:</b>",
        "profile_invited": "👥 <b>Taklif qilgan do'stlaringiz:</b>",
        "back_main_menu": "🔙 Asosiy menyu",
        "pay_card_btn": "💳 Karta raqami",
        "send_receipt_btn": "🧾 To'lov chekini yuborish",
        "contact_admin_btn": "👨‍💻 Adminga murojaat",
        "referral_text": (
            "🎁 **Do'stlarni taklif qiling va bepul limit oling!**\n\n"
            "Har **2 ta do'stingiz** ushbu havola orqali botga kirsa, sizga **+1 ta yangi taqdimot yaratish limiti** sovg'a qilinadi!\n\n"
            "📊 **Sizning referal statistikangiz:**\n"
            "👥 Taklif qilingan do'stlar: **{invited_count} nafar**\n"
            "🎁 Olingan bonus limitlar: **{earned_limits} ta**\n"
            "⏳ Keyingi limit uchun kerak: **{needed_for_next} ta do'st**\n\n"
            "🔗 **Sizning shaxsiy referal havolangiz:**\n"
            "`{ref_link}`\n\n"
            "👇 *Quyidagi tugmani bosing va havolani do'stlaringizga yoki guruhlarga yuboring:*"
        ),
        "tariffs_vip": (
            "👑 **Sizning hisobingizda VIP (Cheksiz) ta'rif faol!**\n\n"
            "Sizga to'lov qilish yoki limit sotib olish talab etilmaydi. "
            "Hisobingizda doimiy **cheksiz taqdimotlar yaratish** imkoniyati yoqilgan.\n\n"
            "Marhamat, istalgancha slayd tayyorlashingiz mumkin."
        ),
        "tariffs_text": (
            "💳 **Tariflar va To'lov:**\n\n"
            "🎁 **2 ta bepul taqdimot** — har bir yangi foydalanuvchiga taqdim etiladi!\n\n"
            "2 ta bepul limitdan so'ng:\n"
            "1️⃣ **1 ta taqdimot** — **5 000 so'm**\n"
            "2️⃣ **3 ta taqdimot** — **12 000 so'm** (chegirma bilan)\n"
            "👑 **Oylik obuna (1 oy)** — **20 000 so'm** (1 oy davomida mutlaqo CHEKSIZ taqdimotlar yaratish! 🚀)\n\n"
            "📌 **To'lov qilish tartibi:**\n"
            "1. Quyidagi kartaga kerakli summani o'tkazing:\n"
            "💳 Karta raqami: `{card_number}`\n"
            "👤 Egasi: **{card_holder}**\n\n"
            "2. Pul o'tkazgach, pastdagi **'🧾 To'lov chekini yuborish'** tugmasini bosing va to'lov chekining rasmini (skrinshotini) botga yuboring.\n"
            "3. 5 daqiqa ichida admin chekni tasdiqlaydi va limitingiz avtomatik qo'shiladi!"
        ),
        "about_text": (
            "ℹ️ **Talabalar uchun Slayd & PDF Generator Bot haqida:**\n\n"
            "🎓 **OTM talablari boʻyicha taqdimotlar:**\n"
            "• Titul varaqasi (Universitet, fakultet, talaba va oʻqituvchi maʼlumotlari)\n"
            "• Taqdimot rejasi (Mundarija) va mazmuniy slaydlar\n"
            "• Xulosa va **Foydalanilgan adabiyotlar (manbalar)**\n"
            "• **Himoya nutq matni (doklad / shpargalka)** — darsda nima deb gapirishni toʻliq koʻrsatadi!\n\n"
            "🔹 **Formatlar:** Tahrirlash mumkin boʻlgan zamonaviy **PowerPoint (.pptx)** hamda **PDF**.\n"
            "🔹 **Ko'p tilli slaydlar:** O'zbek, Rus, Ingliz, Turk, Qozoq, Qirg'iz, Tojik, Nemis tillarida!\n"
            "🔹 **Rasmni PDF ga aylantirish:** Istalgan rasm(lar)ni bir zumda PDF qilib beradi.\n"
            "🔹 **Tariflar:** 2 ta bepul taqdimot, so'ngra 1 ta taqdimot — 5 000 so'm, oylik cheksiz — 20 000 so'm.\n"
            "🔹 **Referal:** Har 2 ta do'st taklif qilsangiz, +1 ta bepul limit beriladi!\n\n"
            "Savol va takliflar uchun quyidagi tugma orqali adminga murojaat qilishingiz mumkin."
        ),
        "status_start": "🚀 Slayd tayyorlash boshlandi...",
        "status_plan": "🧠 1/4: Sun'iy intellekt akademik rejani tuzmoqda...",
        "status_images": "🖼 2/4: Mavzuga mos sifatli rasmlar tanlanmoqda...",
        "status_layout": "🎨 3/4: Slaydlar dizayni va infografikalar chizilmoqda...",
        "status_save": "💾 4/4: PowerPoint (.pptx) fayli saqlanmoqda..."
    },
    "ru": {
        "choose_lang_title": "🌐 <b>Выберите язык / Tilni tanlang / Choose language:</b>",
        "lang_changed": "✅ <b>Язык интерфейса изменен на Русский!</b>",
        "menu_new_slide": "📊 Создать слайды",
        "menu_pptx_to_pdf": "📄 PPTX ➡️ PDF",
        "menu_profile": "👤 Мой профиль",
        "menu_free_limit": "🎁 Бесплатные лимиты",
        "menu_tariffs": "💳 Тарифы",
        "menu_about": "ℹ️ О боте",
        "menu_contact": "👨‍💻 Связаться с админом",
        "menu_change_lang": "🌐 Сменить язык",
        "menu_admin": "⚙️ Админ панель",
        "menu_stats": "📈 Статистика",
        "menu_placeholder": "Введите тему или выберите действие...",
        "photo_to_slides_btn": "📊 Создать презентацию по фото",
        "doc_to_slides_btn": "📊 Создать презентацию из документа",
        "doc_to_pdf_btn": "📄 Конвертировать PPTX в PDF",
        "welcome": (
            "Здравствуйте, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — создание профессиональных презентаций (<b>PowerPoint .pptx</b>) на базе искусственного интеллекта (Google Gemini).\n\n"
            "✨ <b>Возможности:</b>\n"
            "• 🌐 <b>Многоязычность:</b> Презентации на русском, узбекском, английском и еще 9+ языках\n"
            "• 🎙 <b>Голосовые сообщения:</b> Назовите тему голосом, и бот составит презентацию\n"
            "• 📚 <b>По фото книги / конспекта:</b> Отправьте фото материала, и бот структурирует слайды\n"
            "• 📄 <b>PPTX в PDF:</b> Быстрая конвертация презентаций в формат PDF\n\n"
            "🎁 У вас есть <b>{free_limit} бесплатных презентаций</b>!\n"
            "👥 Приглашайте друзей (за каждые 2 друга — <b>+1 бесплатный лимит</b>).\n\n"
            "👇 Нажмите <b>«📊 Создать слайды»</b> ниже или отправьте голосовое сообщение:"
        ),
        "choose_slide_lang": "🌐 <b>На каком языке подготовить презентацию?</b>\n\nВыберите нужный язык из списка ниже: 👇",
        "prompt_topic": "✍️ <b>Отправьте тему презентации:</b>\n\n<i>Например: Роль искусственного интеллекта в современной медицине</i>",
        "prompt_count": (
            "📌 Тема: <b>{topic}</b>\n"
            "🌐 Язык слайдов: <b>{slide_lang}</b>\n\n"
            "📊 <b>Сколько слайдов подготовить?</b>\n"
            "Выберите вариант ниже или отправьте число (от 5 до 30):\n"
            "<i>💡 Например: 7, 10, 12 или 15</i>"
        ),
        "prompt_author": (
            "✅ Выбрано: <b>{count} слайдов</b>!\n\n"
            "🎓 <b>1-й слайд: Данные титульного листа</b>\n"
            "<i>(ВУЗ, факультет, направление, группа, студент и преподаватель)</i>\n\n"
            "Вы можете отправить данные одной строкой или списком:\n"
            "💡 <i>Например:</i>\n"
            "ВУЗ: МГУ\n"
            "Факультет: ВМК\n"
            "Группа: 201\n"
            "Студент: Иван Иванов\n"
            "Преподаватель: Петров П.С.\n\n"
            "⏩ Если титульный лист не нужен, нажмите <b>«Пропустить»</b>:"
        ),
        "prompt_theme": (
            "🎨 <b>Выберите стиль / фон презентации:</b>\n\n"
            "Выберите цвет фона из предложенных или отправьте **свое фоновое изображение**: 👇"
        ),
        "no_limit": (
            "⚠️ <b>К сожалению, ваши лимиты закончились!</b>\n\n"
            "Чтобы создать новую презентацию:\n"
            "1️⃣ <b>Приобретите лимиты или подписку</b> (1 презентация — 5 000 сум, безлимит на месяц — 20 000 сум);\n"
            "2️⃣ <b>Пригласите друзей</b> — получайте <b>+1 лимит</b> за каждые 2 приглашенных друга!"
        ),
        "cancel_btn": "❌ Отмена",
        "cancelled": "❌ Действие отменено.",
        "skip_btn": "⏩ Пропустить (Стандарт)",
        "share_btn": "↗️ Поделиться с друзьями",
        "pptx_to_pdf_prompt": "📄 <b>Отправьте PPTX файл:</b>\n\nБот мгновенно конвертирует его в качественный PDF документ.",
        "image_to_pdf_prompt": "🖼 <b>Отправьте фотографии для конвертации в PDF:</b>\n\nВы можете отправить одно или несколько фото.",
        "edit_in_powerpoint": "📊 Редактировать в PowerPoint (Online)",
        "get_pdf": "📄 Скачать в PDF",
        "speech_notes": "🎤 Текст речи для защиты",
        "bonus_limit": "🎁 Получить бесплатный лимит (+1)",
        "profile_title": "👤 <b>Информация профиля:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Тариф:</b>",
        "profile_limit": "✨ <b>Доступный лимит:</b>",
        "profile_total": "📊 <b>Всего создано слайдов:</b>",
        "profile_invited": "👥 <b>Приглашено друзей:</b>",
        "back_main_menu": "🔙 Главное меню",
        "pay_card_btn": "💳 Номер карты",
        "send_receipt_btn": "🧾 Отправить чек оплаты",
        "contact_admin_btn": "👨‍💻 Связаться с админом",
        "referral_text": (
            "🎁 **Приглашайте друзей и получайте бесплатные лимиты!**\n\n"
            "Каждые **2 друга**, которые перейдут по вашей ссылке и запустят бота, принесут вам **+1 бесплатный лимит на создание презентации**!\n\n"
            "📊 **Ваша реферальная статистика:**\n"
            "👥 Приглашено друзей: **{invited_count} чел.**\n"
            "🎁 Получено бонусных лимитов: **{earned_limits} шт.**\n"
            "⏳ Нужно до следующего бонуса: **{needed_for_next} чел.**\n\n"
            "🔗 **Ваша персональная реферальная ссылка:**\n"
            "`{ref_link}`\n\n"
            "👇 *Нажмите кнопку ниже, чтобы переслать ссылку друзьям или в группы:*"
        ),
        "tariffs_vip": (
            "👑 **Для вашего аккаунта активен тариф VIP (Безлимит)!**\n\n"
            "Вам не требуется покупать лимиты или подписку. "
            "На вашем аккаунте включен постоянный **безлимитный доступ** к созданию презентаций.\n\n"
            "Вы можете создавать неограниченное количество слайдов."
        ),
        "tariffs_text": (
            "💳 **Тарифы и Оплата:**\n\n"
            "🎁 **2 бесплатные презентации** — даются каждому пользователю при старте!\n\n"
            "После расходования 2 бесплатных лимитов:\n"
            "1️⃣ **1 презентация** — **5 000 сум**\n"
            "2️⃣ **3 презентации** — **12 000 сум** (со скидкой)\n"
            "👑 **Месячная подписка** — **20 000 сум** (1 месяц полных БЕЗЛИМИТНЫХ презентаций! 🚀)\n\n"
            "📌 **Как оплатить:**\n"
            "1. Переведите нужную сумму на карту:\n"
            "💳 Номер карты: `{card_number}`\n"
            "👤 Получатель: **{card_holder}**\n\n"
            "2. После перевода нажмите кнопку **'🧾 Отправить чек оплаты'** ниже и отправьте скриншот чека.\n"
            "3. Администратор подтвердит чек в течение 5 минут, и лимиты будут начислены автоматически!"
        ),
        "about_text": (
            "ℹ️ **О боте Slide & PDF Generator для студентов:**\n\n"
            "🎓 **Создание презентаций по академическим стандартам:**\n"
            "• Титульный лист (ВУЗ, факультет, группа, студент и преподаватель)\n"
            "• План презентации (содержание) и структурированные слайды\n"
            "• Заключение и **список литературы (источников)**\n"
            "• **Речь для защиты (доклад / шпаргалка)** — готовый текст того, что говорить во время защиты!\n\n"
            "🔹 **Форматы:** Редактируемый **PowerPoint (.pptx)** и документ **PDF**.\n"
            "🔹 **Многоязычность:** Русский, Узбекский, Английский, Турецкий, Казахский, Кыргызский, Таджикский, Немецкий.\n"
            "🔹 **Конвертер:** Быстрое преобразование фото или PPTX в качественный PDF.\n"
            "🔹 **Тарифы:** 2 бесплатные презентации при старте, затем 1 презентация — 5 000 сум, безлимит на месяц — 20 000 сум.\n"
            "🔹 **Рефералы:** За каждые 2 приглашенных друга — **+1 бесплатный лимит**!\n\n"
            "По всем вопросам и предложениям обращайтесь к администратору."
        ),
        "status_start": "🚀 Начинаем подготовку презентации...",
        "status_plan": "🧠 1/4: ИИ составляет академический план и структуру...",
        "status_images": "🖼 2/4: Подбираются качественные тематические изображения...",
        "status_layout": "🎨 3/4: Оформляется дизайн, инфографика и карточки...",
        "status_save": "💾 4/4: Сохраняется файл PowerPoint (.pptx)..."
    },
    "en": {
        "choose_lang_title": "🌐 <b>Choose language / Tilni tanlang / Выберите язык:</b>",
        "lang_changed": "✅ <b>Interface language changed to English!</b>",
        "menu_new_slide": "📊 Create Slides",
        "menu_pptx_to_pdf": "📄 PPTX ➡️ PDF",
        "menu_profile": "👤 My Profile",
        "menu_free_limit": "🎁 Free Limits",
        "menu_tariffs": "💳 Plans & Pricing",
        "menu_about": "ℹ️ About Bot",
        "menu_contact": "👨‍💻 Contact Admin",
        "menu_change_lang": "🌐 Change Language",
        "menu_admin": "⚙️ Admin Panel",
        "menu_stats": "📈 Statistics",
        "menu_placeholder": "Type topic or choose from menu...",
        "photo_to_slides_btn": "📊 Create Presentation from Photo",
        "doc_to_slides_btn": "📊 Create Presentation from Document",
        "doc_to_pdf_btn": "📄 Convert PPTX to PDF",
        "welcome": (
            "Hello, <b>{name}</b>! 👋\n\n"
            "🤖 <b>Slide AI</b> — professional presentation (<b>PowerPoint .pptx</b>) generator powered by Artificial Intelligence (Google Gemini).\n\n"
            "✨ <b>Features:</b>\n"
            "• 🌐 <b>Multi-language:</b> Generate slides in English, Russian, Uzbek and other languages\n"
            "• 🎙 <b>Voice Input:</b> Speak your topic in an audio note, and AI creates the slides\n"
            "• 📚 <b>From Notes & Books:</b> Send photos of study materials to extract presentations\n"
            "• 📄 <b>PPTX to PDF:</b> Instant high-quality presentation converter\n\n"
            "🎁 You have <b>{free_limit} free presentations</b>!\n"
            "👥 Invite friends (get <b>+1 free presentation</b> for every 2 friends).\n\n"
            "👇 Tap <b>«📊 Create Slides»</b> below or send an audio note to get started:"
        ),
        "choose_slide_lang": "🌐 <b>What language should the presentation be in?</b>\n\nPlease select the desired language below: 👇",
        "prompt_topic": "✍️ <b>Send your presentation topic:</b>\n\n<i>Example: The Role and Future of Artificial Intelligence in Medicine</i>",
        "prompt_count": (
            "📌 Topic: <b>{topic}</b>\n"
            "🌐 Slide Language: <b>{slide_lang}</b>\n\n"
            "📊 <b>How many slides should be generated?</b>\n"
            "Select an option below or type a custom number (5 to 30):\n"
            "<i>💡 Example: 7, 10, 12 or 15</i>"
        ),
        "prompt_author": (
            "✅ <b>{count} slides</b> selected!\n\n"
            "🎓 <b>Slide 1: Title Card Details</b>\n"
            "<i>(University, faculty, department, student name, and professor)</i>\n\n"
            "You can send the details line by line:\n"
            "💡 <i>Example:</i>\n"
            "University: Oxford\n"
            "Faculty: Computer Science\n"
            "Student: John Doe\n"
            "Professor: Dr. Smith\n\n"
            "⏩ If you don't need title details, click <b>«Skip»</b>:"
        ),
        "prompt_theme": (
            "🎨 <b>Choose presentation theme & background:</b>\n\n"
            "Select your preferred color scheme or send **your custom background image**: 👇"
        ),
        "no_limit": (
            "⚠️ <b>Sorry, you have run out of presentation limits!</b>\n\n"
            "To generate new presentations:\n"
            "1️⃣ <b>Purchase limits or monthly subscription</b> (1 presentation — 5,000 UZS, unlimited month — 20,000 UZS);\n"
            "2️⃣ <b>Invite friends</b> — get <b>+1 free limit</b> for every 2 friends who join!"
        ),
        "cancel_btn": "❌ Cancel",
        "cancelled": "❌ Action cancelled.",
        "skip_btn": "⏩ Skip (Default)",
        "share_btn": "↗️ Share with friends",
        "pptx_to_pdf_prompt": "📄 <b>Send your PPTX file:</b>\n\nThe bot will quickly convert it to a high-quality PDF document.",
        "image_to_pdf_prompt": "🖼 <b>Send photos to convert to PDF:</b>\n\nYou can send one or multiple pictures.",
        "edit_in_powerpoint": "📊 Edit in PowerPoint (Online)",
        "get_pdf": "📄 Download as PDF",
        "speech_notes": "🎤 Speaker Defence Script",
        "bonus_limit": "🎁 Get free limit (+1)",
        "profile_title": "👤 <b>Profile Details:</b>",
        "profile_id": "🆔 ID:",
        "profile_tariff": "👑 <b>Plan:</b>",
        "profile_limit": "✨ <b>Available limit:</b>",
        "profile_total": "📊 <b>Total slides created:</b>",
        "profile_invited": "👥 <b>Invited friends:</b>",
        "back_main_menu": "🔙 Main Menu",
        "pay_card_btn": "💳 Card Number",
        "send_receipt_btn": "🧾 Submit Receipt",
        "contact_admin_btn": "👨‍💻 Contact Admin",
        "referral_text": (
            "🎁 **Invite friends and get free presentations!**\n\n"
            "Every **2 friends** who start the bot via your referral link will reward you with **+1 free presentation limit**!\n\n"
            "📊 **Your Referral Statistics:**\n"
            "👥 Invited friends: **{invited_count}**\n"
            "🎁 Earned bonus limits: **{earned_limits}**\n"
            "⏳ Needed for next bonus: **{needed_for_next} friends**\n\n"
            "🔗 **Your personal referral link:**\n"
            "`{ref_link}`\n\n"
            "👇 *Click the button below to share your link with friends or group chats:*"
        ),
        "tariffs_vip": (
            "👑 **VIP (Unlimited) Plan is active on your account!**\n\n"
            "No payments or limit purchases are required. "
            "Permanent **unlimited presentation creation** is enabled for you.\n\n"
            "Feel free to create as many presentations as you need."
        ),
        "tariffs_text": (
            "💳 **Plans & Payment:**\n\n"
            "🎁 **2 free presentations** for every new user!\n\n"
            "After your free limits:\n"
            "1️⃣ **1 presentation** — **5,000 UZS**\n"
            "2️⃣ **3 presentations** — **12,000 UZS** (discounted)\n"
            "👑 **Monthly Unlimited** — **20,000 UZS** (unlimited presentations for 30 days! 🚀)\n\n"
            "📌 **How to pay:**\n"
            "1. Transfer the amount to the card:\n"
            "💳 Card Number: `{card_number}`\n"
            "👤 Recipient: **{card_holder}**\n\n"
            "2. After payment, click **'🧾 Submit Receipt'** below and send a screenshot of the receipt.\n"
            "3. The admin will verify within 5 minutes and limits will be activated automatically!"
        ),
        "about_text": (
            "ℹ️ **About Slide & PDF Generator Bot:**\n\n"
            "🎓 **Academic presentations compliant with university standards:**\n"
            "• Title slide (University, faculty, student name, and supervisor)\n"
            "• Agenda outline and informative content slides\n"
            "• Conclusion and **academic references/bibliography**\n"
            "• **Speaker Defence Script** — full script of what to say while presenting!\n\n"
            "🔹 **Formats:** Editable **PowerPoint (.pptx)** and high quality **PDF**.\n"
            "🔹 **Multi-language:** English, Russian, Uzbek, Turkish, Kazakh, Kyrgyz, Tajik, German.\n"
            "🔹 **Converters:** Convert documents or images to PDF in seconds.\n"
            "🔹 **Plans:** 2 free presentations, then 1 slide — 5,000 UZS, unlimited monthly — 20,000 UZS.\n"
            "🔹 **Referral:** Invite friends (+1 free limit for every 2 friends)!\n\n"
            "For inquiries and support, feel free to contact the administrator."
        ),
        "status_start": "🚀 Starting presentation preparation...",
        "status_plan": "🧠 1/4: AI is composing academic structure and agenda...",
        "status_images": "🖼 2/4: Selecting matching high-resolution imagery...",
        "status_layout": "🎨 3/4: Rendering infographic cards and layout...",
        "status_save": "💾 4/4: Saving PowerPoint (.pptx) presentation..."
    }
}

def get_text(key: str, lang: str = "uz", **kwargs) -> str:
    """Returns localized string, falling back to Uzbek if not found."""
    if lang not in TEXTS:
        lang = "uz"
    template = TEXTS[lang].get(key, TEXTS["uz"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template

def get_slide_lang_info(lang_code: str) -> dict:
    """Returns presentation language settings, falling back to Uzbek."""
    return SLIDE_LANGUAGES.get(lang_code, SLIDE_LANGUAGES["uz"])
