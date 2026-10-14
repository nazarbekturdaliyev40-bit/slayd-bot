from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu(is_admin: bool = False) -> ReplyKeyboardMarkup:
    buttons = [
        [KeyboardButton(text="📊 Yangi slayd tayyorlash")],
        [KeyboardButton(text="📄 PPTX ni PDF ga aylantirish"), KeyboardButton(text="🖼 Rasmni PDF ga aylantirish")],
        [KeyboardButton(text="👤 Mening profilim"), KeyboardButton(text="🎁 Bepul limit olish")],
        [KeyboardButton(text="💳 Limit va Obuna")],
        [KeyboardButton(text="ℹ️ Bot haqida"), KeyboardButton(text="👨‍💻 Adminga murojaat")]
    ]
    if is_admin:
        buttons.append([KeyboardButton(text="⚙️ Admin panel")])
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)


def get_slide_counts_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="5 ta slayd", callback_data="count_5"),
            InlineKeyboardButton(text="8 ta slayd (tavsiya)", callback_data="count_8"),
            InlineKeyboardButton(text="10 ta slayd", callback_data="count_10")
        ],
        [
            InlineKeyboardButton(text="15 ta slayd", callback_data="count_15"),
            InlineKeyboardButton(text="20 ta slayd (katta)", callback_data="count_20")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_referral_keyboard(bot_username: str, telegram_id: int) -> InlineKeyboardMarkup:
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{telegram_id}&text=Sun'iy%20intellekt%20(Google%20Gemini)%20yordamida%20bir%20necha%20soniyada%20professional%20PowerPoint%20taqdimotlar%20tayyorlang!%20%F0%9F%8E%81%20Bepul%20sinab%20ko'rish%20uchun%20bosing:"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="↗️ Do'stlarga ulashish", url=share_url)
        ]
    ])

def get_no_limit_keyboard(bot_username: str, telegram_id: int) -> InlineKeyboardMarkup:
    share_url = f"https://t.me/share/url?url=https://t.me/{bot_username}?start=ref_{telegram_id}&text=Sun'iy%20intellekt%20(Google%20Gemini)%20yordamida%20bir%20necha%20soniyada%20professional%20PowerPoint%20taqdimotlar%20tayyorlang!%20%F0%9F%8E%81%20Bepul%20sinab%20ko'rish%20uchun%20bosing:"
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎁 Do'stlarni taklif qilish (+1 limit)", url=share_url)
        ],
        [
            InlineKeyboardButton(text="💳 Tariflar va To'lov", callback_data="pay_card"),
            InlineKeyboardButton(text="🧾 Chek yuborish", callback_data="send_receipt")
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="cancel_generation")
        ]
    ])

def get_payment_keyboard(admin_username: str = "") -> InlineKeyboardMarkup:
    admin_btn = (
        InlineKeyboardButton(text="👨‍💻 Adminga murojaat", url=f"https://t.me/{admin_username.lstrip('@')}")
        if admin_username
        else InlineKeyboardButton(text="👨‍💻 Adminga murojaat", callback_data="contact_admin")
    )
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="💳 Karta raqami", callback_data="pay_card"),
            InlineKeyboardButton(text="🧾 To'lov chekini yuborish", callback_data="send_receipt")
        ],
        [
            admin_btn
        ],
        [
            InlineKeyboardButton(text="🔙 Asosiy menyu", callback_data="cancel_generation")
        ]
    ])

def get_receipt_cancel_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_receipt")
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

def get_skip_author_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="⏩ O'tkazib yuborish (Standart)", callback_data="skip_author_info")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_theme_selection_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
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
        ],
        [
            InlineKeyboardButton(text="🤖 AI Avtomatik (Mavzuga mos fon)", callback_data="theme_auto")
        ],
        [
            InlineKeyboardButton(text="🖼 Oʻz fon rasmingizni yuklash", callback_data="theme_custom_bg")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_custom_bg_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔙 Fon ranglariga qaytish", callback_data="back_to_theme_selection")
        ],
        [
            InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")
        ]
    ])

def get_slide_action_keyboard(share_url: str = "") -> InlineKeyboardMarkup:
    btns = [
        [
            InlineKeyboardButton(text="📄 PDF formatida olish", callback_data="get_latest_pdf"),
            InlineKeyboardButton(text="🎤 Himoya nutq matni", callback_data="get_latest_speech")
        ]
    ]
    if share_url:
        btns.append([
            InlineKeyboardButton(text="🎁 Bepul limit olish (+1)", url=share_url)
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

def get_media_choice_keyboard(is_doc: bool = False) -> InlineKeyboardMarkup:
    if is_doc:
        first_btn = InlineKeyboardButton(text="📊 Ushbu hujjatdan taqdimot yasash", callback_data="media_to_slides")
        second_btn = InlineKeyboardButton(text="📄 PPTX boʻlsa PDF ga aylantirish", callback_data="media_to_pdf")
    else:
        first_btn = InlineKeyboardButton(text="📊 Shu rasmdan taqdimot yasash", callback_data="media_to_slides")
        second_btn = InlineKeyboardButton(text="🖼 Rasmni PDF ga aylantirish", callback_data="media_to_pdf")
        
    return InlineKeyboardMarkup(inline_keyboard=[
        [first_btn],
        [second_btn],
        [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_generation")]
    ])


