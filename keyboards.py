from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import locales

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
        # Asosiy katta harakat tugmasi:
        [KeyboardButton(text=locales.get_text("menu_new_slide", lang))],
        # 1-qator: Shaxsiy profil va Tariflar
        [
            KeyboardButton(text=locales.get_text("menu_profile", lang)),
            KeyboardButton(text=locales.get_text("menu_tariffs", lang))
        ],
        # 2-qator: Bepul bonus limit va PPTX -> PDF konverter
        [
            KeyboardButton(text=locales.get_text("menu_free_limit", lang)),
            KeyboardButton(text=locales.get_text("menu_pptx_to_pdf", lang))
        ],
        # 3-qator: Tilni o'zgartirish va Yordam / Bot haqida
        [
            KeyboardButton(text=locales.get_text("menu_change_lang", lang)),
            KeyboardButton(text=locales.get_text("menu_about", lang))
        ]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text=locales.get_text("menu_admin", lang))])
    
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
            admin_btn
        ],
        [
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
            InlineKeyboardButton(text="➕ 1 ta limit (5 000)", callback_data=f"adm_pay_limit_1_{user_id}"),
            InlineKeyboardButton(text="➕ 3 ta limit (12 000)", callback_data=f"adm_pay_limit_3_{user_id}")
        ],
        [
            InlineKeyboardButton(text="👑 1 oylik obuna (20 000)", callback_data=f"adm_pay_sub_{user_id}")
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

def get_skip_author_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=locales.get_text("skip_btn", lang), callback_data="skip_author_info")
        ],
        [
            InlineKeyboardButton(text=locales.get_text("cancel_btn", lang), callback_data="cancel_generation")
        ]
    ])

def get_theme_selection_keyboard() -> InlineKeyboardMarkup:
    import gamma_service
    rows = []
    if gamma_service.is_gamma_available():
        rows.append([
            InlineKeyboardButton(text="🪄 Gamma AI (gamma.app taqdimot)", callback_data="theme_gamma")
        ])
    else:
        rows.append([
            InlineKeyboardButton(text="✨ PowerPoint AI (Avtomatik eng yaxshi dizayn)", callback_data="theme_auto")
        ])

    rows.extend([
        [
            InlineKeyboardButton(text="⚪️ Oq fon (Minimal)", callback_data="theme_white"),
            InlineKeyboardButton(text="⚫️ Qora fon (Premium Dark)", callback_data="theme_dark")
        ],
        [
            InlineKeyboardButton(text="🔵 Toʻq koʻk fon (Navy)", callback_data="theme_navy"),
            InlineKeyboardButton(text="🔷 Moviy fon (Havorang)", callback_data="theme_blue")
        ],
        [
            InlineKeyboardButton(text="🟢 Zumrad yashil fon", callback_data="theme_green"),
            InlineKeyboardButton(text="🟣 Binafsha fon (Kosmik)", callback_data="theme_purple")
        ],
        [
            InlineKeyboardButton(text="🌸 Canva Pastel fon", callback_data="theme_canva_pastel"),
            InlineKeyboardButton(text="📜 Klassik pergament fon", callback_data="theme_vintage")
        ]
    ])
    if gamma_service.is_gamma_available():
        rows.append([
            InlineKeyboardButton(text="🤖 AI Avtomatik (Mavzuga mos fon)", callback_data="theme_auto")
        ])
    rows.extend([
        [
            InlineKeyboardButton(text="🖼 Oʻz fon rasmingizni yuklash", callback_data="theme_custom_bg")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def get_custom_bg_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Fon ranglariga qaytish", callback_data="back_to_theme_selection")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
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
        second_btn = InlineKeyboardButton(text=locales.get_text("doc_to_pdf_btn", lang), callback_data="media_to_pdf")
        return InlineKeyboardMarkup(inline_keyboard=[
            [first_btn],
            [second_btn],
            [InlineKeyboardButton(text=cancel_text, callback_data="cancel_generation")]
        ])
    else:
        first_btn = InlineKeyboardButton(text=locales.get_text("photo_to_slides_btn", lang), callback_data="media_to_slides")
        return InlineKeyboardMarkup(inline_keyboard=[
            [first_btn],
            [InlineKeyboardButton(text=cancel_text, callback_data="cancel_generation")]
        ])


