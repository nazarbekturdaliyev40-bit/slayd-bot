from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
import locales
import config

def get_language_selection_keyboard() -> InlineKeyboardMarkup:
    """Interfeys tilini tanlash uchun tugmalar (Start bosilganda va sozlamalarda)."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="setlang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="setlang_ru"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="setlang_en")
        ]
    ])

def get_slide_language_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Slayd qaysi tilda tayyorlanishini tanlash (O'zbek, Rus, Ingliz, Turk, Qozoq, Qirg'iz, Tojik, Nemis)."""
    cancel_text = locales.get_text("cancel_btn", lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data="slidelang_uz"),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data="slidelang_ru")
        ],
        [
            InlineKeyboardButton(text="🇬🇧 English", callback_data="slidelang_en"),
            InlineKeyboardButton(text="🇹🇷 Türkçe", callback_data="slidelang_tr")
        ],
        [
            InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="slidelang_kk"),
            InlineKeyboardButton(text="🇰🇬 Кыргызча", callback_data="slidelang_ky")
        ],
        [
            InlineKeyboardButton(text="🇹🇯 Тоҷикӣ", callback_data="slidelang_tg"),
            InlineKeyboardButton(text="🇩🇪 Deutsch", callback_data="slidelang_de")
        ],
        [
            InlineKeyboardButton(text=cancel_text, callback_data="cancel_generation")
        ]
    ])

def get_main_menu(is_admin: bool = False, lang: str = "uz") -> ReplyKeyboardMarkup:
    """Foydalanuvchi tanlagan tildagi chiroyli va qulay tartiblangan asosiy menyu."""
    buttons = [
        # 1-qator: Slayd tayyorlash va Shaxsiy profil yonma-yon
        [
            KeyboardButton(text=locales.get_text("menu_new_slide", lang)),
            KeyboardButton(text=locales.get_text("menu_profile", lang))
        ],
        # 2-qator: Mening fayllarim va Tariflar
        [
            KeyboardButton(text=locales.get_text("menu_my_files", lang)),
            KeyboardButton(text=locales.get_text("menu_tariffs", lang))
        ],
        # 3-qator: Bepul bonus limit va Tilni o'zgartirish
        [
            KeyboardButton(text=locales.get_text("menu_free_limit", lang)),
            KeyboardButton(text=locales.get_text("menu_change_lang", lang))
        ],
        # 4-qator: Bot haqida va Adminga murojaat
        [
            KeyboardButton(text=locales.get_text("menu_about", lang)),
            KeyboardButton(text=locales.get_text("menu_contact", lang))
        ]
    ]
    if is_admin:
        buttons.append([
            KeyboardButton(text=locales.get_text("menu_admin", lang)),
            KeyboardButton(text=locales.get_text("menu_stats", lang))
        ])
    
    return ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True,
        input_field_placeholder=locales.get_text("menu_placeholder", lang)
    )


def get_slide_counts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5 ta slayd", callback_data="count_5"),
            InlineKeyboardButton(text="8 ta (tavsiya)", callback_data="count_8"),
            InlineKeyboardButton(text="10 ta slayd", callback_data="count_10")
        ],
        [
            InlineKeyboardButton(text="12 ta slayd", callback_data="count_12"),
            InlineKeyboardButton(text="15 ta slayd", callback_data="count_15"),
            InlineKeyboardButton(text="20 ta slayd", callback_data="count_20")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_referral_keyboard(bot_username: str, telegram_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    import urllib.parse
    if lang == "ru":
        share_msg = "Создавайте профессиональные презентации PowerPoint за секунды с помощью искусственного интеллекта (Google Gemini)! 🎁 Попробуйте бесплатно:"
    elif lang == "en":
        share_msg = "Create professional PowerPoint presentations in seconds powered by AI (Google Gemini)! 🎁 Try for free:"
    else:
        share_msg = "Sun'iy intellekt (Google Gemini) yordamida bir necha soniyada professional PowerPoint taqdimotlar tayyorlang! 🎁 Bepul sinab ko'rish uchun bosing:"
    encoded_text = urllib.parse.quote(share_msg)
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{telegram_id}&text={encoded_text}"
    btn_text = locales.get_text("share_btn", lang)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=btn_text, url=share_url)
        ]
    ])

def get_no_limit_keyboard(bot_username: str, telegram_id: int, lang: str = "uz") -> InlineKeyboardMarkup:
    import urllib.parse
    if lang == "ru":
        share_msg = "Создавайте профессиональные презентации PowerPoint за секунды с помощью искусственного интеллекта (Google Gemini)! 🎁 Попробуйте бесплатно:"
    elif lang == "en":
        share_msg = "Create professional PowerPoint presentations in seconds powered by AI (Google Gemini)! 🎁 Try for free:"
    else:
        share_msg = "Sun'iy intellekt (Google Gemini) yordamida bir necha soniyada professional PowerPoint taqdimotlar tayyorlang! 🎁 Bepul sinab ko'rish uchun bosing:"
    encoded_text = urllib.parse.quote(share_msg)
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{telegram_id}&text={encoded_text}"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("bonus_limit", lang), url=share_url)
        ],
        [
            InlineKeyboardButton(text=locales.get_text("pay_card_btn", lang), callback_data="pay_card"),
            InlineKeyboardButton(text=locales.get_text("send_receipt_btn", lang), callback_data="send_receipt")
        ],
        [
            InlineKeyboardButton(text=locales.get_text("back_main_menu", lang), callback_data="cancel_generation")
        ]
    ])

def get_payment_keyboard(admin_username: str = "", lang: str = "uz") -> InlineKeyboardMarkup:
    admin_title = locales.get_text("contact_admin_btn", lang)
    admin_btn = (
        InlineKeyboardButton(text=admin_title, url=f"https://t.me/{admin_username.lstrip('@')}")
        if admin_username
        else InlineKeyboardButton(text=admin_title, callback_data="contact_admin")
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("pay_card_btn", lang), callback_data="pay_card"),
            InlineKeyboardButton(text=locales.get_text("send_receipt_btn", lang), callback_data="send_receipt")
        ],
        [
            admin_btn,
            InlineKeyboardButton(text=locales.get_text("back_main_menu", lang), callback_data="cancel_generation")
        ]
    ])

def get_receipt_cancel_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("cancel_btn", lang), callback_data="cancel_receipt")
        ]
    ])

def get_admin_receipt_keyboard(user_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ 1 ta limit (3 000)", callback_data=f"adm_pay_limit_1_{user_id}"),
            InlineKeyboardButton(text="➕ 3 ta limit (8 000)", callback_data=f"adm_pay_limit_3_{user_id}")
        ],
        [
            InlineKeyboardButton(text="👑 1 oylik obuna (40 000)", callback_data=f"adm_pay_sub_{user_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"adm_pay_reject_{user_id}")
        ]
    ])

def get_admin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📈 Bot statistikasi", callback_data="admin_stats")
        ]
    ])

def get_about_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("contact_admin_btn", lang), callback_data="contact_admin")
        ]
    ])

def get_contact_admin_keyboard(admin_username: str = "", admin_id: int = 0, lang: str = "uz") -> InlineKeyboardMarkup:
    target_id = admin_id or 8597458619
    admin_url = (
        f"https://t.me/{admin_username.lstrip('@')}"
        if admin_username
        else f"tg://user?id={target_id}"
    )
    if admin_username:
        pm_title = f"{locales.get_text('write_to_pm_btn', lang)} (@{admin_username.lstrip('@')})"
    else:
        pm_title = locales.get_text("write_to_pm_btn", lang)

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=pm_title, url=admin_url)
        ],
        [
            InlineKeyboardButton(text=locales.get_text("cancel_btn", lang), callback_data="cancel_contact")
        ]
    ])

def get_skip_author_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("skip_btn", lang), callback_data="skip_author_info"),
            InlineKeyboardButton(text=locales.get_text("cancel_btn", lang), callback_data="cancel_generation")
        ]
    ])

def get_theme_selection_keyboard() -> InlineKeyboardMarkup:
    """Fanlar bo'yicha kategoriyalangan PowerPoint 2016 shablonlarini tanlash oynasi va Mini Ilova tugmasi."""
    webapp_url = getattr(config, "THEMES_WEBAPP_URL", "https://slayd-bot.onrender.com/themes")
    rows = [
        # 1-qator: Telegram Mini Ilova tugmasi (Oyna ochilishi uchun)
        [
            InlineKeyboardButton(
                text="📱 Fanlar bo'yicha fon tanlash (Mini ilova)",
                web_app=WebAppInfo(url=webapp_url)
            )
        ],
        # 2-qator: Universal Dinamik Mix
        [
            InlineKeyboardButton(text="🔀 Barcha fanlar uchun (Dinamik Mix)", callback_data="theme_mix")
        ],
        # Fanlar bo'yicha juftliklar
        [
            InlineKeyboardButton(text="💻 IT & Kiber (Circuit)", callback_data="theme_circuit"),
            InlineKeyboardButton(text="🩺 Tibbiyot (Droplet)", callback_data="theme_droplet")
        ],
        [
            InlineKeyboardButton(text="💼 Biznes & Moliya (Office)", callback_data="theme_office"),
            InlineKeyboardButton(text="📐 Fizika & Texnika (Integral)", callback_data="theme_integral")
        ],
        [
            InlineKeyboardButton(text="🌿 Biologiya & Eko (Facet)", callback_data="theme_facet"),
            InlineKeyboardButton(text="🏛 Tarix & Meros (Retrospect)", callback_data="theme_retrospect")
        ],
        [
            InlineKeyboardButton(text="📚 Adabiyot & Til (Savon)", callback_data="theme_savon"),
            InlineKeyboardButton(text="🔴 Ta'lim & Psixologiya (Ion)", callback_data="theme_ion")
        ],
        [
            InlineKeyboardButton(text="🔷 IT Startaplar (Slice)", callback_data="theme_slice"),
            InlineKeyboardButton(text="🌌 Koinot & Astronomiya (Celestial)", callback_data="theme_celestial")
        ],
        [
            InlineKeyboardButton(text="🌸 San'at & Ijod (Pastel)", callback_data="theme_canva_pastel"),
            InlineKeyboardButton(text="🖤 Hashamatli Dark (Dark Gold)", callback_data="theme_dark")
        ],
        [
            InlineKeyboardButton(text="⚪️ Minimal Oq Galereya", callback_data="theme_white"),
            InlineKeyboardButton(text="📜 Antik Pergament", callback_data="theme_vintage")
        ],
        [
            InlineKeyboardButton(text="🖼 Oʻz fon rasmingizni yuklash", callback_data="theme_custom_bg")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_theme_reply_keyboard() -> ReplyKeyboardMarkup:
    """Telegram pastki panelida Mini ilovani ochish tugmasi."""
    webapp_url = getattr(config, "THEMES_WEBAPP_URL", "https://slayd-bot.onrender.com/themes")
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Fanlar bo'yicha fon tanlash (Mini ilova)", web_app=WebAppInfo(url=webapp_url))],
            [KeyboardButton(text="❌ Bekor qilish")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def get_custom_bg_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_to_theme_selection"),
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_confirm_generation_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Taqdimot tayyorlashdan oldin barcha ma'lumotlarni ko'rib tasdiqlash tugmalari."""
    change_theme_txt = "🎨 Fonni o'zgartirish" if lang == "uz" else ("🎨 Сменить фон" if lang == "ru" else "🎨 Change theme")
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("confirm_btn", lang), callback_data="confirm_slide_generation")
        ],
        [
            InlineKeyboardButton(text=change_theme_txt, callback_data="change_theme_btn"),
            InlineKeyboardButton(text=locales.get_text("cancel_btn", lang), callback_data="cancel_generation")
        ]
    ])

def get_slide_action_keyboard(share_url: str = "", gamma_url: str = "", lang: str = "uz") -> InlineKeyboardMarkup:
    btns = []
    if gamma_url:
        btns.append([
            InlineKeyboardButton(text="🌐 Gamma.app da ochish va tahrirlash", url=gamma_url)
        ])
    else:
        ppt_btn_text = locales.get_text("edit_in_powerpoint", lang)
        btns.append([
            InlineKeyboardButton(text=ppt_btn_text, url="https://powerpoint.cloud.microsoft/")
        ])
    pdf_btn_text = locales.get_text("get_pdf", lang)
    speech_btn_text = locales.get_text("speech_notes", lang)
    btns.append([
        InlineKeyboardButton(text=pdf_btn_text, callback_data="get_latest_pdf"),
        InlineKeyboardButton(text=speech_btn_text, callback_data="get_latest_speech")
    ])
    if share_url:
        bonus_btn_text = locales.get_text("bonus_limit", lang)
        btns.append([
            InlineKeyboardButton(text=bonus_btn_text, url=share_url)
        ])
    return InlineKeyboardMarkup(inline_keyboard=btns)

def get_cancel_pptx_to_pdf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_pptx_to_pdf")
        ]
    ])

def get_cancel_image_to_pdf_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_image_to_pdf")
        ]
    ])

def get_media_choice_keyboard(is_doc: bool = False, lang: str = "uz") -> InlineKeyboardMarkup:
    cancel_text = locales.get_text("cancel_btn", lang)
    if is_doc:
        first_btn = InlineKeyboardButton(text=locales.get_text("doc_to_slides_btn", lang), callback_data="media_to_slides")
    else:
        first_btn = InlineKeyboardButton(text=locales.get_text("photo_to_slides_btn", lang), callback_data="media_to_slides")
    return InlineKeyboardMarkup(inline_keyboard=[
        [first_btn],
        [InlineKeyboardButton(text=cancel_text, callback_data="cancel_generation")]
    ])


