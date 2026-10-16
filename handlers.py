import os
import json
import tempfile
import logging
import shutil
import asyncio
import html
import re
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import database
import keyboards
import generator
import gamma_service
import locales

logger = logging.getLogger(__name__)
router = Router()

class SlideCreation(StatesGroup):
    waiting_for_slide_language = State()
    waiting_for_topic = State()
    waiting_for_count = State()
    waiting_for_author = State()
    waiting_for_theme = State()
    waiting_for_custom_bg = State()

class PptxToPdfState(StatesGroup):
    waiting_for_pptx = State()

class ImageToPdfState(StatesGroup):
    waiting_for_image = State()

class PaymentReceiptState(StatesGroup):
    waiting_for_receipt = State()

class AdminContactState(StatesGroup):
    waiting_for_message = State()

class AdminSendReplyState(StatesGroup):
    waiting_for_reply_text = State()

class MediaChoiceState(StatesGroup):
    waiting_for_action = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject = None):
    await state.clear()
    
    existing_user = await database.get_user(message.from_user.id)
    can_be_referred = (existing_user is None)

    # Extract referrer if provided
    referrer_id = None
    args_str = ""
    if command and command.args:
        args_str = command.args.strip()
    elif message.text and len(message.text.split()) > 1:
        args_str = message.text.split()[1].strip()

    if args_str:
        if args_str.startswith("ref_"):
            try:
                referrer_id = int(args_str.replace("ref_", ""))
            except ValueError:
                pass
        elif args_str.isdigit():
            referrer_id = int(args_str)

    logger.info(f"/start from user {message.from_user.id} ({message.from_user.full_name}), referrer_id: {referrer_id}, can_be_referred: {can_be_referred}")

    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or ""
    )
    is_admin = config.is_admin(message.from_user.id)

    # Process referral reward
    if can_be_referred and referrer_id and referrer_id != message.from_user.id:
        ref_res = await database.process_referral(message.from_user.id, referrer_id)
        if ref_res["success"]:
            invited_cnt = ref_res["new_invited_count"]
            friend_name = message.from_user.full_name or "Yangi foydalanuvchi"
            logger.info(f"Referral successful: {message.from_user.id} invited by {referrer_id}. Total: {invited_cnt}, rewarded: {ref_res['reward_given']}")
            safe_friend = html.escape(friend_name)
            if ref_res["reward_given"]:
                try:
                    await message.bot.send_message(
                        referrer_id,
                        f"🎉 <b>Ajoyib yangilik!</b> Siz taklif qilgan do'stingiz ({safe_friend}) botga qo'shildi!\n\n"
                        f"🎁 <b>2 ta do'st taklif qilganingiz uchun sizga +1 ta taqdimot limiti berildi!</b> 🥳\n"
                        f"👥 Jami taklif qilgan do'stlaringiz: <b>{invited_cnt} nafar</b>.",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning(f"Referrerga xabar yuborishda xatolik: {e}")
            else:
                try:
                    await message.bot.send_message(
                        referrer_id,
                        f"👤 <b>Yangi do'st qo'shildi!</b> Siz taklif qilgan do'stingiz ({safe_friend}) botga kirdi.\n\n"
                        f"💡 Yana <b>1 ta do'stingiz</b> qo'shilsa, hisobingizga <b>+1 ta bepul taqdimot limiti</b> sovg'a qilinadi! (Hozircha: {invited_cnt} ta)",
                        parse_mode="HTML"
                    )
                except Exception as e:
                    logger.warning(f"Referrerga xabar yuborishda xatolik: {e}")

    # Prompt language selection on /start
    lang_prompt = (
        "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>\n\n"
        "Iltimos, botdan foydalanish uchun qulay tilni tanlang:\n"
        "Пожалуйста, выберите удобный язык интерфейса:\n"
        "Please select your preferred interface language:"
    )
    await message.answer(
        lang_prompt,
        reply_markup=keyboards.get_language_selection_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("setlang_"))
async def process_language_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    chosen_lang = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await database.set_user_language(user_id, chosen_lang)
    user = await database.get_user(user_id) or {}
    is_admin = config.is_admin(user_id)

    name = html.escape(callback.from_user.first_name or "Foydalanuvchi")
    free_limit = user.get("free_limit", 2)
    welcome_text = locales.get_text("welcome", chosen_lang, name=name, free_limit=free_limit)

    try:
        await callback.message.delete()
    except Exception:
        pass

    await callback.message.answer(
        welcome_text,
        reply_markup=keyboards.get_main_menu(is_admin=is_admin, lang=chosen_lang),
        parse_mode="HTML"
    )

@router.message(Command("lang"))
@router.message(F.text.in_({"🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language", "🌐 Change language"}))
async def prompt_change_language(message: Message):
    lang_prompt = (
        "🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>\n\n"
        "Iltimos, botdan foydalanish uchun qulay tilni tanlang:\n"
        "Пожалуйста, выберите удобный язык интерфейса:\n"
        "Please select your preferred interface language:"
    )
    await message.answer(
        lang_prompt,
        reply_markup=keyboards.get_language_selection_keyboard(),
        parse_mode="HTML"
    )

@router.message(F.text.in_({"🎁 Bepul limit", "🎁 Bepul limit olish", "🎁 Бесплатные лимиты", "🎁 Получить бесплатный лимит", "🎁 Free Limits", "🎁 Get free limits"}))
async def show_referral_program(message: Message):
    user_lang = await database.get_user_language(message.from_user.id)
    bot_user = await message.bot.get_me()
    stats = await database.get_referral_stats(message.from_user.id)
    ref_link = f"https://t.me/{bot_user.username}?start=ref_{message.from_user.id}"
    
    text = locales.get_text(
        "referral_text",
        user_lang,
        invited_count=stats['invited_count'],
        earned_limits=stats['earned_limits'],
        needed_for_next=stats['needed_for_next'],
        ref_link=ref_link
    )
    await message.answer(
        text,
        reply_markup=keyboards.get_referral_keyboard(bot_user.username, message.from_user.id, lang=user_lang),
        parse_mode="Markdown"
    )

@router.message(F.text.in_({"👤 Mening profilim", "👤 Profilim", "👤 Мой профиль", "👤 My Profile"}))
@router.message(Command("profil"))
@router.message(Command("profile"))
async def show_profile(message: Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        user = await database.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or ""
        )
    
    user_lang = user.get("language") or "uz"
    stats = await database.get_referral_stats(message.from_user.id)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id)
    is_sub = database.is_subscription_active(user)
    total_remaining = user["free_limit"] + user["paid_balance"]
    
    if is_unlimited:
        if user_lang == "ru":
            text = (
                f"👤 **Информация профиля:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Тариф:** 👑 VIP / Безлимит (Владелец)\n"
                f"✨ **Доступный лимит:** ♾ **Без ограничений**\n"
                f"📊 **Всего создано слайдов:** **{user['total_generated']} шт.**\n"
                f"👥 **Приглашено друзей:** **{stats['invited_count']} чел.**\n\n"
                f"✅ Для вашего аккаунта активирован постоянный безлимитный доступ."
            )
        elif user_lang == "en":
            text = (
                f"👤 **User Profile:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Plan:** 👑 VIP / Unlimited (Owner)\n"
                f"✨ **Available limit:** ♾ **Unlimited**\n"
                f"📊 **Total slides created:** **{user['total_generated']}**\n"
                f"👥 **Invited friends:** **{stats['invited_count']}**\n\n"
                f"✅ Unlimited access is permanently enabled for your account."
            )
        else:
            text = (
                f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Tarif:** 👑 VIP / Cheksiz (Bot Egasi)\n"
                f"✨ **Mavjud limit:** ♾ **Cheksiz**\n"
                f"📊 **Jami yaratilgan slaydlar:** **{user['total_generated']} ta**\n"
                f"👥 **Taklif qilgan do'stlaringiz:** **{stats['invited_count']} nafar**\n\n"
                f"✅ Barcha xizmatlar hisobingiz uchun to'liq bepul va cheksiz sozlangan."
            )
    elif is_sub:
        sub_until = user.get("subscription_until", "")
        if user_lang == "ru":
            text = (
                f"👤 **Информация профиля:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Тариф:** ⭐️ **Месячная подписка**\n"
                f"⏳ **Действует до:** `{sub_until}`\n"
                f"✨ **Доступный лимит:** ♾ **Без ограничений**\n"
                f"📊 **Всего создано слайдов:** **{user['total_generated']} шт.**\n"
                f"👥 **Приглашено друзей:** **{stats['invited_count']} чел.**\n\n"
                f"✅ Вы можете создавать презентации без ограничений."
            )
        elif user_lang == "en":
            text = (
                f"👤 **User Profile:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Plan:** ⭐️ **Monthly Unlimited**\n"
                f"⏳ **Valid until:** `{sub_until}`\n"
                f"✨ **Available limit:** ♾ **Unlimited**\n"
                f"📊 **Total slides created:** **{user['total_generated']}**\n"
                f"👥 **Invited friends:** **{stats['invited_count']}**\n\n"
                f"✅ You can create presentations without restrictions."
            )
        else:
            text = (
                f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"👑 **Tarif:** ⭐️ **Oylik cheksiz obuna**\n"
                f"⏳ **Amal qilish muddati:** `{sub_until}` gacha\n"
                f"✨ **Mavjud limit:** ♾ **Obuna davrida cheksiz**\n"
                f"📊 **Jami yaratilgan slaydlar:** **{user['total_generated']} ta**\n"
                f"👥 **Taklif qilgan do'stlaringiz:** **{stats['invited_count']} nafar**\n\n"
                f"✅ Ushbu muddat davomida bemalol yangi slaydlar yaratishingiz mumkin."
            )
    else:
        if user_lang == "ru":
            text = (
                f"👤 **Информация профиля:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"🎁 Стартовый лимит: **{user['free_limit']} шт.**\n"
                f"💳 Оплаченный баланс: **{user['paid_balance']} шт.**\n"
                f"✨ Всего доступно: **{total_remaining} шт.**\n"
                f"📊 Всего создано: **{user['total_generated']} шт.**\n"
                f"👥 Приглашено друзей: **{stats['invited_count']} чел.** (бонус: {stats['earned_limits']} лимитов)\n\n"
            )
            if total_remaining == 0:
                text += (
                    "⚠️ **Ваши лимиты исчерпаны.**\n\n"
                    "💡 Чтобы продолжить, выберите подходящий тариф в меню «💳 Тарифы» или пригласите друзей и получите бесплатные лимиты."
                )
            else:
                text += "✅ Вы можете создать презентацию прямо сейчас."
        elif user_lang == "en":
            text = (
                f"👤 **User Profile:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"🎁 Initial free limit: **{user['free_limit']}**\n"
                f"💳 Paid balance: **{user['paid_balance']}**\n"
                f"✨ Total available: **{total_remaining}**\n"
                f"📊 Total created: **{user['total_generated']}**\n"
                f"👥 Friends invited: **{stats['invited_count']}** (bonus: {stats['earned_limits']} limits)\n\n"
            )
            if total_remaining == 0:
                text += (
                    "⚠️ **You have no remaining limits.**\n\n"
                    "💡 To create presentations, select a plan in «💳 Plans & Pricing» or invite friends for free bonus limits."
                )
            else:
                text += "✅ You are ready to create a new presentation."
        else:
            text = (
                f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
                f"🆔 ID: `{user['telegram_id']}`\n"
                f"🎁 Boshlang'ich limit: **{user['free_limit']} ta**\n"
                f"💳 Pulli balans: **{user['paid_balance']} ta**\n"
                f"✨ Jami mavjud limit: **{total_remaining} ta**\n"
                f"📊 Jami tayyorlangan: **{user['total_generated']} ta**\n"
                f"👥 Taklif qilgan do'stlaringiz: **{stats['invited_count']} nafar** (bonus: {stats['earned_limits']} ta)\n\n"
            )
            if total_remaining == 0:
                text += (
                    "⚠️ **Sizning limitingiz tugagan.**\n\n"
                    "💡 Yangi taqdimot yaratish uchun «💳 Tariflar» menyusi orqali limit xarid qilishingiz yoki do'stlaringizni taklif qilib bepul limit olishingiz mumkin."
                )
            else:
                text += "✅ Siz bemalol yangi slayd yaratishingiz mumkin."

    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.in_({"💳 Tariflar", "💳 Limit sotib olish", "💳 Limit va Obuna", "💳 Тарифы", "💳 Лимиты и Подписка", "💳 Plans & Pricing", "💳 Limits & Subscription"}))
@router.message(Command("limit"))
@router.message(Command("obuna"))
@router.message(Command("tariffs"))
async def buy_limits(message: Message):
    user = await database.get_user(message.from_user.id)
    user_lang = (user.get("language") if user else "uz") or "uz"
    is_unlimited = (user and bool(user.get("is_unlimited"))) or config.is_unlimited(message.from_user.id)
    if is_unlimited:
        await message.answer(
            locales.get_text("tariffs_vip", user_lang),
            parse_mode="Markdown"
        )
        return

    text = locales.get_text(
        "tariffs_text",
        user_lang,
        card_number=config.CARD_NUMBER,
        card_holder=config.CARD_HOLDER
    )
    await message.answer(text, reply_markup=keyboards.get_payment_keyboard(config.ADMIN_USERNAME, lang=user_lang), parse_mode="Markdown")

@router.callback_query(F.data == "pay_card")
async def pay_card_callback(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        f"💳 **To'lov rekvizitlari:**\n\n"
        f"💳 Karta raqami: `{config.CARD_NUMBER}`\n"
        f"👤 Egasi: **{config.CARD_HOLDER}**\n\n"
        f"Pulni o'tkazgach, pastdagi **'🧾 To'lov chekini yuborish'** tugmasini bosing va skrinshotni yuboring.",
        reply_markup=keyboards.get_payment_keyboard(config.ADMIN_USERNAME),
        parse_mode="Markdown"
    )

# ----------------- CHEK YUBORISH JARAYONI -----------------
@router.callback_query(F.data == "send_receipt")
async def send_receipt_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(PaymentReceiptState.waiting_for_receipt)
    await callback.message.answer(
        "📸 **To'lov chekini yuborish:**\n\n"
        "Iltimos, kartaga pul o'tkazganingiz haqidagi **chek rasmini (skrinshotini)** shu yerga yuboring.\n\n"
        "Admin chekni ko'rib chiqib, 5 daqiqa ichida hisobingizga limit yoki obunani faollashtirib beradi! ⏳",
        reply_markup=keyboards.get_receipt_cancel_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "cancel_receipt")
async def cancel_receipt_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Chek yuborish bekor qilindi.")
    await callback.message.answer(
        "❌ Chek yuborish bekor qilindi.",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id))
    )

@router.message(PaymentReceiptState.waiting_for_receipt, F.photo)
async def process_receipt_photo(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Foydalanuvchi"
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    photo_id = message.photo[-1].file_id

    # Foydalanuvchiga tasdiq xabari
    await message.answer(
        "✅ <b>To'lov chekingiz adminga yuborildi!</b>\n\n"
        "Admin to'lovni tekshirib tasdiqlagach, bot sizga avtomatik xabar beradi va limitingiz qo'shiladi. ⏳",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(user_id)),
        parse_mode="HTML"
    )

    safe_name = html.escape(user_name)
    safe_username = html.escape(username)
    admin_caption = (
        f"🧾 <b>YANGI TO'LOV CHEKI!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {safe_name} ({safe_username})\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
        f"Tasdiqlash uchun quyidagi tugmalardan birini bosing:"
    )
    admin_kb = keyboards.get_admin_receipt_keyboard(user_id)

    admin_targets = set(getattr(config, "ADMIN_USERS", [config.ADMIN_ID]))
    for adm_id in admin_targets:
        try:
            await message.bot.send_photo(
                chat_id=adm_id,
                photo=photo_id,
                caption=admin_caption,
                reply_markup=admin_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"HTML send failed for admin {adm_id}: {e}")
            try:
                # Plain text fallback
                plain_caption = f"🧾 YANGI TO'LOV CHEKI!\n\n👤 Foydalanuvchi: {user_name} ({username})\n🆔 Telegram ID: {user_id}\n\nTasdiqlash uchun tugmalardan birini bosing:"
                await message.bot.send_photo(
                    chat_id=adm_id,
                    photo=photo_id,
                    caption=plain_caption,
                    reply_markup=admin_kb
                )
            except Exception as e2:
                logger.error(f"Fallback plain text send failed for admin {adm_id}: {e2}")

@router.message(PaymentReceiptState.waiting_for_receipt, F.document)
async def process_receipt_document(message: Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Foydalanuvchi"
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"

    await message.answer(
        "✅ <b>To'lov chekingiz adminga yuborildi!</b>\n\n"
        "Admin to'lovni tekshirib tasdiqlagach, bot sizga avtomatik xabar beradi va limitingiz qo'shiladi. ⏳",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(user_id)),
        parse_mode="HTML"
    )

    safe_name = html.escape(user_name)
    safe_username = html.escape(username)
    admin_caption = (
        f"🧾 <b>YANGI TO'LOV CHEKI (Hujjat)!</b>\n\n"
        f"👤 <b>Foydalanuvchi:</b> {safe_name} ({safe_username})\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
        f"Tasdiqlash uchun quyidagi tugmalardan birini bosing:"
    )
    admin_kb = keyboards.get_admin_receipt_keyboard(user_id)

    admin_targets = set(getattr(config, "ADMIN_USERS", [config.ADMIN_ID]))
    for adm_id in admin_targets:
        try:
            await message.bot.send_document(
                chat_id=adm_id,
                document=message.document.file_id,
                caption=admin_caption,
                reply_markup=admin_kb,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"HTML doc send failed for admin {adm_id}: {e}")
            try:
                plain_caption = f"🧾 YANGI TO'LOV CHEKI (Hujjat)!\n\n👤 Foydalanuvchi: {user_name} ({username})\n🆔 Telegram ID: {user_id}\n\nTasdiqlash uchun tugmalardan birini bosing:"
                await message.bot.send_document(
                    chat_id=adm_id,
                    document=message.document.file_id,
                    caption=plain_caption,
                    reply_markup=admin_kb
                )
            except Exception as e2:
                logger.error(f"Fallback plain doc send failed for admin {adm_id}: {e2}")

@router.message(PaymentReceiptState.waiting_for_receipt, F.text)
async def process_receipt_text_invalid(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    await message.answer(
        "⚠️ Iltimos, to'lov chekining <b>rasmini (skrinshotini)</b> yuboring.\n"
        "Agar bekor qilmoqchi bo'lsangiz, '❌ Bekor qilish' tugmasini bosing.",
        reply_markup=keyboards.get_receipt_cancel_keyboard(),
        parse_mode="HTML"
    )

# ----------------- ADMIN TOMONIDAN CHEKNI TASDIQLASH -----------------
@router.callback_query(F.data.startswith("adm_pay_limit_"))
async def adm_approve_limit(callback: CallbackQuery):
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    # Data: adm_pay_limit_<amount>_<user_id>
    parts = callback.data.split("_")
    amount = int(parts[3])
    target_id = int(parts[4])

    success = await database.add_paid_limit(target_id, amount)
    await callback.answer(f"{amount} ta limit qo'shildi!")

    if success:
        try:
            await callback.bot.send_message(
                chat_id=target_id,
                text=(
                    f"🎉 <b>To'lovingiz muvaffaqiyatli tasdiqlandi!</b>\n\n"
                    f"Hisobingizga <b>+{amount} ta</b> yangi taqdimot limiti qo'shildi! 🚀\n"
                    f"Marhamat, taqdimot yaratish uchun <b>'📊 Yangi slayd tayyorlash'</b> tugmasini bosing!"
                ),
                reply_markup=keyboards.get_main_menu(),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {target_id}: {e}")

    old_caption = callback.message.caption or ""
    adm_name = html.escape(callback.from_user.full_name or "Admin")
    new_caption = f"{old_caption}\n\n✅ <b>TASDIQLANDI:</b> +{amount} ta limit berildi! (Admin: {adm_name})"
    try:
        await callback.message.edit_caption(caption=new_caption, reply_markup=None, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.edit_caption(caption=f"{old_caption}\n\n✅ TASDIQLANDI: +{amount} ta limit berildi!", reply_markup=None)
        except Exception:
            await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("adm_pay_sub_"))
async def adm_approve_sub(callback: CallbackQuery):
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    # Data: adm_pay_sub_<user_id>
    parts = callback.data.split("_")
    target_id = int(parts[3])

    res = await database.activate_subscription(target_id, days=30)
    await callback.answer("1 oylik obuna faollashtirildi!")

    if res["success"]:
        exp = res["expires_at"]
        try:
            await callback.bot.send_message(
                chat_id=target_id,
                text=(
                    f"🎉 <b>To'lovingiz muvaffaqiyatli tasdiqlandi!</b>\n\n"
                    f"👑 Sizga <b>1 oylik (30 kunlik) CHEKSIZ OBUNA</b> faollashtirildi!\n"
                    f"⏳ Amal qilish muddati: <code>{exp}</code> gacha.\n\n"
                    f"Ushbu muddat davomida bemalol istalgancha yangi taqdimotlar yaratishingiz mumkin! 🚀"
                ),
                reply_markup=keyboards.get_main_menu(),
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Failed to notify user {target_id}: {e}")

    old_caption = callback.message.caption or ""
    adm_name = html.escape(callback.from_user.full_name or "Admin")
    new_caption = f"{old_caption}\n\n👑 <b>TASDIQLANDI:</b> 1 oylik obuna faollashtirildi! (Admin: {adm_name})"
    try:
        await callback.message.edit_caption(caption=new_caption, reply_markup=None, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.edit_caption(caption=f"{old_caption}\n\n👑 TASDIQLANDI: 1 oylik obuna!", reply_markup=None)
        except Exception:
            await callback.message.edit_reply_markup(reply_markup=None)

@router.callback_query(F.data.startswith("adm_pay_reject_"))
async def adm_reject_payment(callback: CallbackQuery):
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Siz admin emassiz!", show_alert=True)
        return

    # Data: adm_pay_reject_<user_id>
    parts = callback.data.split("_")
    target_id = int(parts[3])

    await callback.answer("Chek rad etildi.")
    try:
        await callback.bot.send_message(
            chat_id=target_id,
            text=(
                "❌ <b>To'lov chekingiz tasdiqlanmadi.</b>\n\n"
                "Sababi: to'lov summasi to'liq kelib tushmagan yoki chek noto'g'ri bo'lishi mumkin. "
                "Iltimos, qayta tekshirib ko'ring yoki adminga murojaat qiling."
            ),
            reply_markup=keyboards.get_main_menu(),
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Failed to notify user {target_id}: {e}")

    old_caption = callback.message.caption or ""
    adm_name = html.escape(callback.from_user.full_name or "Admin")
    new_caption = f"{old_caption}\n\n❌ <b>RAD ETILDI</b> (Admin: {adm_name})"
    try:
        await callback.message.edit_caption(caption=new_caption, reply_markup=None, parse_mode="HTML")
    except Exception:
        try:
            await callback.message.edit_caption(caption=f"{old_caption}\n\n❌ RAD ETILDI", reply_markup=None)
        except Exception:
            await callback.message.edit_reply_markup(reply_markup=None)

# ----------------- ADMINGA MUROJAAT QILISH -----------------
@router.message(F.text.in_({"👨‍💻 Adminga murojaat", "Adminga murojaat", "Admin bilan bog'lanish", "Murojaat", "Admin", "👨‍💻 Связаться с админом", "👨‍💻 Contact Admin"}))
@router.message(Command("murojaat"))
@router.message(Command("admin"))
@router.message(Command("boglanish"))
@router.message(Command("contact"))
@router.message(Command("support"))
async def contact_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    user_lang = await database.get_user_language(message.from_user.id)
    buttons = []
    if config.ADMIN_USERNAME:
        buttons.append([
            InlineKeyboardButton(text=f"✈️ Admin profili (@{config.ADMIN_USERNAME.lstrip('@')})", url=f"https://t.me/{config.ADMIN_USERNAME.lstrip('@')}")
        ])
    buttons.append([
        InlineKeyboardButton(text=locales.get_text("cancel_btn", user_lang), callback_data="cancel_contact")
    ])

    await state.set_state(AdminContactState.waiting_for_message)
    if user_lang == "ru":
        contact_text = (
            "👨‍💻 <b>Связаться с администратором:</b>\n\n"
            "Напишите ваш вопрос, предложение или сообщение о проблеме.\n"
            "<i>(Также вы можете прикрепить скриншот, фото или голосовое сообщение)</i>\n\n"
            "Администратор рассмотрит ваше сообщение и ответит в ближайшее время."
        )
    elif user_lang == "en":
        contact_text = (
            "👨‍💻 <b>Contact Administrator:</b>\n\n"
            "Please send your question, feedback, or describe any issue you encountered.\n"
            "<i>(You can also attach a screenshot, photo, document or voice message)</i>\n\n"
            "The administrator will review your message and reply promptly."
        )
    else:
        contact_text = (
            "👨‍💻 <b>Adminga murojaat qilish:</b>\n\n"
            "Savollaringiz, takliflaringiz yoki biron-bir muammo bo'lsa, xabaringizni yozib yuboring.\n"
            "<i>(Xabar bilan birga skrinshot / rasm, fayl yoki ovozli xabar ham yuborishingiz mumkin)</i>\n\n"
            "Admin xabaringizni ko'rib chiqib, tez orada sizga javob qaytaradi."
        )
    await message.answer(
        contact_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "contact_admin")
async def contact_admin_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    buttons = []
    if config.ADMIN_USERNAME:
        buttons.append([
            InlineKeyboardButton(text=f"✈️ Admin profili (@{config.ADMIN_USERNAME.lstrip('@')})", url=f"https://t.me/{config.ADMIN_USERNAME.lstrip('@')}")
        ])
    buttons.append([
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_contact")
    ])

    await state.set_state(AdminContactState.waiting_for_message)
    await callback.message.answer(
        "👨‍💻 <b>Adminga murojaat qilish:</b>\n\n"
        "Savollaringiz, takliflaringiz yoki biron-bir muammo bo'lsa, xabaringizni yozib yuboring.\n"
        "<i>(Xabar bilan birga skrinshot / rasm, fayl yoki ovozli xabar ham yuborishingiz mumkin)</i>\n\n"
        "Admin xabaringizni ko'rib chiqib, tez orada sizga javob qaytaradi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "cancel_contact")
async def cancel_contact_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Murojaat bekor qilindi.")
    await callback.message.answer("❌ Adminga murojaat bekor qilindi.", reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id)))

async def check_menu_navigation(message: Message, state: FSMContext) -> bool:
    """Agar foydalanuvchi menyu tugmasini bosgan yoki buyruq bergan bo'lsa, holatdan chiqib menyuni ochadi."""
    if not message.text:
        return False
    text = message.text.strip()
    menu_items = {
        # Uzbek
        "📊 Slayd tayyorlash", "📊 Yangi slayd tayyorlash", "📄 PPTX ni PDF ga aylantirish",
        "👤 Mening profilim", "🎁 Bepul limit", "🎁 Bepul limit olish", "💳 Tariflar",
        "💳 Limit va Obuna", "💳 Limit sotib olish",
        "ℹ️ Bot haqida", "👨‍💻 Adminga murojaat", "Adminga murojaat", "⚙️ Admin panel", "🌐 Tilni o'zgartirish",
        # Russian
        "📊 Создать слайды", "📊 Создать слайд", "📄 PPTX в PDF", "📄 Конвертировать PPTX в PDF",
        "👤 Мой профиль", "🎁 Бесплатные лимиты", "🎁 Получить бесплатный лимит", "💳 Тарифы", "💳 Лимиты и Подписка",
        "ℹ️ О боте", "👨‍💻 Связаться с админом", "⚙️ Админ панель", "🌐 Сменить язык",
        # English
        "📊 Create Slides", "📊 Create slide", "📄 PPTX to PDF", "📄 Convert PPTX to PDF",
        "👤 My Profile", "🎁 Free Limits", "🎁 Get free limits", "💳 Plans & Pricing", "💳 Limits & Subscription",
        "ℹ️ About Bot", "👨‍💻 Contact Admin", "⚙️ Admin Panel", "🌐 Change Language", "🌐 Change language"
    }
    if text.startswith("/") or text in menu_items:
        await state.clear()
        if text.startswith("/start"):
            await cmd_start(message, state)
        elif text in ("📊 Slayd tayyorlash", "📊 Yangi slayd tayyorlash", "📊 Создать слайды", "📊 Создать слайд", "📊 Create Slides", "📊 Create slide", "/yangi_slayd", "/new_slide", "/slayd"):
            await start_new_slide(message, state)
        elif text in ("📄 PPTX ni PDF ga aylantirish", "📄 PPTX в PDF", "📄 Конвертировать PPTX в PDF", "📄 PPTX to PDF", "📄 Convert PPTX to PDF"):
            await prompt_pptx_to_pdf(message, state)
        elif text in ("👤 Mening profilim", "👤 Мой профиль", "👤 My Profile", "/profil", "/profile"):
            await show_profile(message)
        elif text in ("🎁 Bepul limit", "🎁 Bepul limit olish", "🎁 Бесплатные лимиты", "🎁 Получить бесплатный лимит", "🎁 Free Limits", "🎁 Get free limits"):
            await show_referral_program(message)
        elif text in ("💳 Tariflar", "💳 Limit va Obuna", "💳 Лимиты и Подписка", "💳 Тарифы", "💳 Plans & Pricing", "💳 Limits & Subscription", "💳 Limit sotib olish", "/limit", "/obuna", "/tariffs"):
            await buy_limits(message)
        elif text in ("ℹ️ Bot haqida", "ℹ️ О боте", "ℹ️ About Bot", "/haqida", "/help", "/about"):
            await about_bot(message)
        elif text in ("🌐 Tilni o'zgartirish", "🌐 Сменить язык", "🌐 Change Language", "🌐 Change language", "/lang"):
            await prompt_change_language(message)
        elif text in ("⚙️ Admin panel", "⚙️ Админ панель", "⚙️ Admin Panel") and config.is_admin(message.from_user.id):
            await admin_panel(message)
        elif text in ("👨‍💻 Adminga murojaat", "👨‍💻 Связаться с админом", "👨‍💻 Contact Admin", "Adminga murojaat", "/murojaat", "/admin"):
            await contact_admin_menu(message, state)
        return True
    return False

@router.message(AdminContactState.waiting_for_message)
async def process_admin_contact(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return

    await state.clear()
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Foydalanuvchi"
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"

    await message.answer(
        "✅ <b>Xabaringiz adminga yetkazildi!</b>\n\nAdmin tez orada xabaringizni ko'rib chiqib, javob beradi.",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(user_id)),
        parse_mode="HTML"
    )

    safe_name = html.escape(user_name)
    safe_username = html.escape(username)
    admin_targets = set(getattr(config, "ADMIN_USERS", [config.ADMIN_ID]))

    reply_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Javob yozish", callback_data=f"admin_reply_btn_{user_id}")]
    ])

    if message.photo:
        photo = message.photo[-1]
        caption = message.caption or "(Matnsiz rasm)"
        safe_caption = html.escape(caption)
        admin_caption = (
            f"📩 <b>YANGI MUROJAAT (Rasm / Skrinshot):</b>\n\n"
            f"👤 <b>Yuboruvchi:</b> {safe_name} ({safe_username})\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
            f"💬 <b>Tavsif:</b> {safe_caption}\n\n"
            f"✍️ <i>Javob berish:</i> Ushbu xabarga <b>Reply</b> qiling yoki pastdagi tugmani bosing."
        )
        for adm_id in admin_targets:
            try:
                await message.bot.send_photo(
                    chat_id=adm_id,
                    photo=photo.file_id,
                    caption=admin_caption,
                    reply_markup=reply_kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Photo forward failed for admin {adm_id}: {e}")
    elif message.voice:
        admin_caption = (
            f"📩 <b>YANGI MUROJAAT (Ovozli xabar):</b>\n\n"
            f"👤 <b>Yuboruvchi:</b> {safe_name} ({safe_username})\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
            f"✍️ <i>Javob berish:</i> Ushbu xabarga <b>Reply</b> qiling yoki pastdagi tugmani bosing."
        )
        for adm_id in admin_targets:
            try:
                await message.bot.send_voice(
                    chat_id=adm_id,
                    voice=message.voice.file_id,
                    caption=admin_caption,
                    reply_markup=reply_kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Voice forward failed for admin {adm_id}: {e}")
    elif message.document:
        caption = message.caption or ""
        safe_caption = html.escape(caption)
        admin_caption = (
            f"📩 <b>YANGI MUROJAAT (Hujjat / Fayl):</b>\n\n"
            f"👤 <b>Yuboruvchi:</b> {safe_name} ({safe_username})\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
            + (f"\n💬 <b>Tavsif:</b> {safe_caption}\n" if safe_caption else "") +
            f"\n✍️ <i>Javob berish:</i> Ushbu xabarga <b>Reply</b> qiling yoki pastdagi tugmani bosing."
        )
        for adm_id in admin_targets:
            try:
                await message.bot.send_document(
                    chat_id=adm_id,
                    document=message.document.file_id,
                    caption=admin_caption,
                    reply_markup=reply_kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Document forward failed for admin {adm_id}: {e}")
    else:
        user_text = message.text or ""
        safe_text = html.escape(user_text)
        admin_msg = (
            f"📩 <b>YANGI MUROJAAT (Adminga xabar):</b>\n\n"
            f"👤 <b>Yuboruvchi:</b> {safe_name} ({safe_username})\n"
            f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
            f"💬 <b>Xabar matni:</b>\n{safe_text}\n\n"
            f"✍️ <i>Javob berish:</i>\n"
            f"• Ushbu xabarga to'g'ridan-to'g'ri <b>Reply</b> qiling\n"
            f"• Pastdagi <b>'✉️ Javob yozish'</b> tugmasini bosing\n"
            f"• Yoki buyruq: <code>/reply {user_id} Javob matni</code>"
        )
        for adm_id in admin_targets:
            try:
                await message.bot.send_message(
                    chat_id=adm_id,
                    text=admin_msg,
                    reply_markup=reply_kb,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"HTML forward failed for admin {adm_id}: {e}")
                try:
                    plain_msg = f"📩 YANGI MUROJAAT:\n\n👤 {user_name} ({username})\n🆔 ID: {user_id}\n\n💬 Xabar:\n{user_text}\n\nJavob: /reply {user_id} matn"
                    await message.bot.send_message(chat_id=adm_id, text=plain_msg)
                except Exception as e2:
                    logger.error(f"Plain forward failed for admin {adm_id}: {e2}")

@router.callback_query(F.data.startswith("admin_reply_btn_"))
async def admin_reply_btn_callback(callback: CallbackQuery, state: FSMContext):
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    await callback.answer()
    target_id = int(callback.data.replace("admin_reply_btn_", ""))
    await state.set_state(AdminSendReplyState.waiting_for_reply_text)
    await state.update_data(target_user_id=target_id)
    await callback.message.answer(
        f"✍️ Foydalanuvchi (<code>{target_id}</code>) ga yuboriladigan javob matnini yozing:\n\n"
        f"<i>(Bekor qilish uchun /cancel deb yozing)</i>",
        parse_mode="HTML"
    )

@router.message(AdminSendReplyState.waiting_for_reply_text)
async def process_admin_reply_text(message: Message, state: FSMContext):
    if message.text in ("/cancel", "Bekor qilish", "❌ Bekor qilish"):
        await state.clear()
        await message.answer("❌ Javob yuborish bekor qilindi.")
        return
    data = await state.get_data()
    target_id = data.get("target_user_id")
    await state.clear()
    if not target_id:
        await message.answer("❌ Foydalanuvchi ID topilmadi.")
        return

    reply_text = message.text or message.caption or ""
    safe_reply = html.escape(reply_text)

    try:
        if message.photo:
            await message.bot.send_photo(
                chat_id=target_id,
                photo=message.photo[-1].file_id,
                caption=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}" if safe_reply else "👨‍💻 <b>Admindan javob</b>",
                parse_mode="HTML"
            )
        elif message.document:
            await message.bot.send_document(
                chat_id=target_id,
                document=message.document.file_id,
                caption=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}" if safe_reply else "👨‍💻 <b>Admindan javob</b>",
                parse_mode="HTML"
            )
        elif message.voice:
            await message.bot.send_voice(
                chat_id=target_id,
                voice=message.voice.file_id,
                caption="👨‍💻 <b>Admindan javob (ovozli)</b>",
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                chat_id=target_id,
                text=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}",
                parse_mode="HTML"
            )
        await message.answer(f"✅ Javob foydalanuvchi <code>{target_id}</code> ga muvaffaqiyatli yetkazildi!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xatolik: foydalanuvchiga yuborib bo'lmadi ({e})")

@router.message(F.reply_to_message)
async def admin_direct_reply(message: Message):
    if not config.is_admin(message.from_user.id):
        return
    if message.text and message.text.startswith("/"):
        return

    orig = message.reply_to_message.text or message.reply_to_message.caption or ""
    import re
    match = re.search(r"Telegram ID:.*?(\d{6,15})", orig) or re.search(r"ID:.*?(\d{6,15})", orig)
    if not match:
        return

    target_id = int(match.group(1))
    reply_text = message.text or message.caption or ""
    safe_reply = html.escape(reply_text)

    try:
        if message.photo:
            await message.bot.send_photo(
                chat_id=target_id,
                photo=message.photo[-1].file_id,
                caption=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}" if safe_reply else "👨‍💻 <b>Admindan javob</b>",
                parse_mode="HTML"
            )
        elif message.document:
            await message.bot.send_document(
                chat_id=target_id,
                document=message.document.file_id,
                caption=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}" if safe_reply else "👨‍💻 <b>Admindan javob</b>",
                parse_mode="HTML"
            )
        elif message.voice:
            await message.bot.send_voice(
                chat_id=target_id,
                voice=message.voice.file_id,
                caption="👨‍💻 <b>Admindan javob (ovozli)</b>",
                parse_mode="HTML"
            )
        else:
            await message.bot.send_message(
                chat_id=target_id,
                text=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}",
                parse_mode="HTML"
            )
        await message.answer(f"✅ Javobingiz foydalanuvchi <code>{target_id}</code> ga yetkazildi!", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Javob yuborishda xatolik: {e}")

@router.message(F.text.in_({"ℹ️ Bot haqida", "ℹ️ О боте", "ℹ️ About Bot"}))
@router.message(Command("haqida"))
@router.message(Command("help"))
@router.message(Command("about"))
@router.message(Command("yordam"))
async def about_bot(message: Message):
    user_lang = await database.get_user_language(message.from_user.id)
    text = locales.get_text("about_text", user_lang)
    await message.answer(text, reply_markup=keyboards.get_about_keyboard(lang=user_lang), parse_mode="Markdown")


# ================= RASMNI PDF GA AYLANTIRISH =================
MEDIA_GROUP_CACHE = {}

async def _process_media_group(group_id: str, bot, state: FSMContext = None):
    await asyncio.sleep(1.5)
    data = MEDIA_GROUP_CACHE.pop(group_id, None)
    if not data:
        return
    messages = data.get("messages", [])
    if not messages:
        return

    last_msg = messages[-1]
    status_msg = await last_msg.answer("⏳ Rasmlar to'plami PDF ga aylantirilmoqda...")
    tmp_dir = tempfile.mkdtemp(prefix="album2pdf_")
    try:
        downloaded = []
        for idx, m in enumerate(messages, 1):
            if m.photo:
                photo = m.photo[-1]
                path = os.path.join(tmp_dir, f"page_{idx:03d}.jpg")
                await bot.download(photo.file_id, destination=path)
                if os.path.exists(path):
                    downloaded.append(path)

        if not downloaded:
            await status_msg.edit_text("❌ Rasmlarni yuklab olishda xatolik yuz berdi.")
            return

        pdf_path = os.path.join(tmp_dir, "rasmlar_to'plami.pdf")
        await asyncio.to_thread(generator.convert_images_to_pdf, downloaded, pdf_path)

        pdf_doc = FSInputFile(pdf_path, filename="rasmlar_to'plami.pdf")
        await last_msg.reply_document(
            document=pdf_doc,
            caption=(
                f"✅ **Rasmlar muvaffaqiyatli PDF ga aylantirildi!**\n\n"
                f"📄 Jami sahifalar: **{len(downloaded)} ta**\n"
                f"✨ Barcha rasmlar bitta tartibli PDF hujjatga birlashtirildi."
            ),
            parse_mode="Markdown"
        )
        await status_msg.delete()
        if state:
            await state.clear()
    except Exception as e:
        logger.error(f"Album PDF error: {e}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

# ================= PPTX NI PDF GA AYLANTIRISH =================
@router.message(F.text.in_({"📄 PPTX ni PDF ga aylantirish", "📄 Конвертировать PPTX в PDF", "📄 Convert PPTX to PDF"}))
async def prompt_pptx_to_pdf(message: Message, state: FSMContext):
    user_lang = await database.get_user_language(message.from_user.id)
    await state.set_state(PptxToPdfState.waiting_for_pptx)
    await message.answer(
        locales.get_text("pptx_to_pdf_prompt", user_lang),
        reply_markup=keyboards.get_cancel_pptx_to_pdf_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "cancel_pptx_to_pdf")
async def cancel_pptx_to_pdf_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Bekor qilindi")
    user_lang = await database.get_user_language(callback.from_user.id)
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id), lang=user_lang)
    )

@router.message(F.text.in_({"🖼 Rasmni PDF ga aylantirish", "🖼 Конвертировать фото в PDF", "🖼 Convert Image to PDF"}))
async def prompt_image_to_pdf(message: Message, state: FSMContext):
    user_lang = await database.get_user_language(message.from_user.id)
    await state.set_state(ImageToPdfState.waiting_for_image)
    await message.answer(
        locales.get_text("image_to_pdf_prompt", user_lang),
        reply_markup=keyboards.get_cancel_image_to_pdf_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "cancel_image_to_pdf")
async def cancel_image_to_pdf_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Bekor qilindi")
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id))
    )

@router.message(ImageToPdfState.waiting_for_image, F.photo)
async def handle_photo_to_pdf(message: Message, state: FSMContext):
    if message.media_group_id:
        group_id = message.media_group_id
        if group_id not in MEDIA_GROUP_CACHE:
            MEDIA_GROUP_CACHE[group_id] = {
                "messages": [message],
                "task": asyncio.create_task(_process_media_group(group_id, message.bot, state))
            }
        else:
            MEDIA_GROUP_CACHE[group_id]["messages"].append(message)
        return

    # Yagona rasm
    status_msg = await message.answer("⏳ Rasm PDF ga aylantirilmoqda...")
    tmp_dir = tempfile.mkdtemp(prefix="single2pdf_")
    try:
        photo = message.photo[-1]
        img_path = os.path.join(tmp_dir, "photo.jpg")
        await message.bot.download(photo.file_id, destination=img_path)
        pdf_path = os.path.join(tmp_dir, "rasm.pdf")
        await asyncio.to_thread(generator.convert_images_to_pdf, [img_path], pdf_path)

        pdf_doc = FSInputFile(pdf_path, filename="rasm.pdf")
        await message.reply_document(
            document=pdf_doc,
            caption="✅ **Rasmingiz sifatli PDF hujjatga aylantirildi!** 📄",
            parse_mode="Markdown"
        )
        await status_msg.delete()
        await state.clear()
    except Exception as e:
        logger.error(f"Single photo PDF error: {e}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

@router.message(ImageToPdfState.waiting_for_image, F.text)
async def handle_image_to_pdf_text(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    await message.answer(
        "⚠️ Iltimos, PDF ga aylantirish uchun rasm yuboring yoki '❌ Bekor qilish' tugmasini bosing:",
        reply_markup=keyboards.get_cancel_image_to_pdf_keyboard()
    )

@router.message(PptxToPdfState.waiting_for_pptx, F.text)
async def handle_pptx_to_pdf_text(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    await message.answer(
        "⚠️ Iltimos, PowerPoint (.pptx) taqdimot faylini yuboring yoki '❌ Bekor qilish' tugmasini bosing:",
        reply_markup=keyboards.get_cancel_pptx_to_pdf_keyboard()
    )

@router.message(F.document)
async def handle_document_to_pdf(message: Message, state: FSMContext = None):
    cur_state = await state.get_state() if state else None
    if cur_state in (SlideCreation.waiting_for_custom_bg, SlideCreation.waiting_for_theme):
        return  # Slide creation custom background handlers will process it

    doc = message.document
    mime = (doc.mime_type or "").lower()
    fname = (doc.file_name or "").lower()
    
    is_presentation = any(fname.endswith(ext) for ext in [".pptx", ".ppt"]) or "presentation" in mime or "powerpoint" in mime
    is_image = mime.startswith("image/") or any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"])

    if is_presentation:
        if state:
            await state.clear()
        status_msg = await message.answer("⏳ PowerPoint taqdimoti sifatli PDF ga aylantirilmoqda, iltimos kuting...")
        tmp_dir = tempfile.mkdtemp(prefix="pptx2pdf_")
        try:
            f_name = doc.file_name or "taqdimot.pptx"
            pptx_path = os.path.join(tmp_dir, f_name)
            await message.bot.download(doc.file_id, destination=pptx_path)
            
            base_name = os.path.splitext(f_name)[0] or "taqdimot"
            pdf_path = os.path.join(tmp_dir, f"{base_name}.pdf")
            await asyncio.to_thread(generator.convert_pptx_to_pdf, pptx_path, pdf_path)

            pdf_doc = FSInputFile(pdf_path, filename=f"{base_name}.pdf")
            await message.reply_document(
                document=pdf_doc,
                caption="✅ **Taqdimotingiz sifatli PDF hujjatga muvaffaqiyatli aylantirildi!** 📄✨",
                parse_mode="Markdown"
            )
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Doc presentation PDF error: {e}")
            await status_msg.edit_text(f"❌ Taqdimotni PDF ga aylantirishda xatolik yuz berdi:\n`{e}`")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    if cur_state == PptxToPdfState.waiting_for_pptx and not is_presentation:
        await message.answer(
            "⚠️ Ushbu fayl PowerPoint (.pptx yoki .ppt) formati emas.\n"
            "Iltimos, .pptx taqdimot faylini yuboring yoki bekor qilish uchun '❌ Bekor qilish' tugmasini bosing:",
            reply_markup=keyboards.get_cancel_pptx_to_pdf_keyboard()
        )
        return

    if is_image and cur_state == ImageToPdfState.waiting_for_image:
        status_msg = await message.answer("⏳ Hujjatdagi rasm PDF ga aylantirilmoqda...")
        tmp_dir = tempfile.mkdtemp(prefix="doc2pdf_")
        try:
            f_name = doc.file_name or "image.jpg"
            img_path = os.path.join(tmp_dir, f_name)
            await message.bot.download(doc.file_id, destination=img_path)
            base_name = os.path.splitext(f_name)[0] or "rasm"
            pdf_path = os.path.join(tmp_dir, f"{base_name}.pdf")
            await asyncio.to_thread(generator.convert_images_to_pdf, [img_path], pdf_path)

            pdf_doc = FSInputFile(pdf_path, filename=f"{base_name}.pdf")
            await message.reply_document(
                document=pdf_doc,
                caption="✅ **Rasmingiz sifatli PDF hujjatga aylantirildi!** 📄",
                parse_mode="Markdown"
            )
            await status_msg.delete()
            if state:
                await state.clear()
        except Exception as e:
            logger.error(f"Doc image PDF error: {e}")
            await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return

    # Boshqa barcha hujjatlar (PDF, Word, TXT, konspektlar) slayd yaratish yoki tahlil qilish uchun yuboriladi
    await handle_document_media(message, state)


@router.message(F.text.in_({"📊 Slayd tayyorlash", "📊 Yangi slayd tayyorlash", "📊 Создать слайды", "📊 Создать слайд", "📊 Create Slides", "📊 Create slide"}))
@router.message(Command("slayd"))
@router.message(Command("yangi_slayd"))
@router.message(Command("new_slide"))
async def start_new_slide(message: Message, state: FSMContext):
    # Check limit first
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or ""
    )
    user_lang = user.get("language") or "uz"
    
    is_sub = database.is_subscription_active(user)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id) or is_sub
    total_remaining = user["free_limit"] + user["paid_balance"]

    if not is_unlimited and total_remaining <= 0:
        bot_user = await message.bot.get_me()
        await message.answer(
            locales.get_text("no_limit", user_lang),
            reply_markup=keyboards.get_no_limit_keyboard(bot_user.username, message.from_user.id),
            parse_mode="HTML"
        )
        return

    await state.set_state(SlideCreation.waiting_for_slide_language)
    await message.answer(
        locales.get_text("choose_slide_lang", user_lang),
        reply_markup=keyboards.get_slide_language_keyboard(user_lang),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("slidelang_"), SlideCreation.waiting_for_slide_language)
async def process_slide_language(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    slide_lang = callback.data.split("_")[1]
    await state.update_data(slide_language=slide_lang)

    user = await database.get_user(callback.from_user.id) or {}
    user_lang = user.get("language") or "uz"
    lang_info = locales.get_slide_lang_info(slide_lang)

    await state.set_state(SlideCreation.waiting_for_topic)
    topic_prompt = locales.get_text("prompt_topic", user_lang)
    await callback.message.answer(
        f"🌐 <b>Tanlangan til / Выбранный язык / Language:</b> {lang_info['name']}\n\n{topic_prompt}",
        parse_mode="HTML"
    )

@router.message(SlideCreation.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    topic = (message.text or "").strip()
    user = await database.get_user(message.from_user.id) or {}
    user_lang = user.get("language") or "uz"

    if len(topic) < 3:
        await message.answer(locales.get_text("prompt_topic", user_lang), parse_mode="HTML")
        return

    await state.update_data(topic=topic)
    await state.set_state(SlideCreation.waiting_for_count)
    
    data = await state.get_data()
    slide_lang = data.get("slide_language", "uz")
    lang_info = locales.get_slide_lang_info(slide_lang)

    safe_topic = html.escape(topic)
    count_prompt = locales.get_text(
        "prompt_count",
        user_lang,
        topic=safe_topic,
        slide_lang=lang_info["name"]
    )
    await message.answer(
        count_prompt,
        reply_markup=keyboards.get_slide_counts_keyboard(),
        parse_mode="HTML"
    )

async def proceed_to_author_step(target_message: Message, state: FSMContext, slide_count: int):
    await state.update_data(slide_count=slide_count)
    await state.set_state(SlideCreation.waiting_for_author)

    user_id = target_message.chat.id
    user = await database.get_user(user_id) or {}
    user_lang = user.get("language") or "uz"

    author_prompt = locales.get_text("prompt_author", user_lang, count=slide_count)
    await target_message.answer(
        author_prompt,
        reply_markup=keyboards.get_skip_author_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("count_"), SlideCreation.waiting_for_count)
async def process_slide_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    count_str = callback.data.split("_")[1]
    slide_count = int(count_str)
    await proceed_to_author_step(callback.message, state, slide_count)

@router.message(SlideCreation.waiting_for_count, F.text)
async def process_slide_count_text(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    text = (message.text or "").strip()
    match = re.search(r"\d+", text)
    if not match:
        await message.answer(
            "⚠️ Iltimos, slaydlar sonini raqamda yozing (masalan: <b>7</b>, <b>12</b>, <b>15</b>) yoki quyidagi tugmalardan birini tanlang:",
            reply_markup=keyboards.get_slide_counts_keyboard(),
            parse_mode="HTML"
        )
        return

    slide_count = int(match.group())
    if slide_count < 3:
        await message.answer(
            "⚠️ Slaydlar soni kamida <b>3 ta</b> boʻlishi kerak.\nIltimos, 3 dan 30 gacha boʻlgan son kiriting:",
            parse_mode="HTML"
        )
        return
    if slide_count > 30:
        await message.answer(
            "⚠️ Slaydlar soni koʻpi bilan <b>30 ta</b> boʻlishi mumkin.\nIltimos, 3 dan 30 gacha boʻlgan son kiriting:",
            parse_mode="HTML"
        )
        return

    await proceed_to_author_step(message, state, slide_count)

@router.message(SlideCreation.waiting_for_count)
async def process_slide_count_invalid(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    await message.answer(
        "⚠️ Iltimos, slaydlar sonini raqamda yozib yuboring (masalan: <b>8</b> yoki <b>12</b>) yoki quyidagi tugmalardan birini tanlang:",
        reply_markup=keyboards.get_slide_counts_keyboard(),
        parse_mode="HTML"
    )


@router.message(SlideCreation.waiting_for_author, F.text)
async def process_author_info_message(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    author_info = (message.text or "").strip()
    await state.update_data(author_info=author_info)
    await state.set_state(SlideCreation.waiting_for_theme)
    await message.answer(
        "🎨 **Slaydning orqa fonini (dizaynini) tanlang:**\n\n"
        "Oʻzingizga yoqqan orqa fon rangini tanlang yoki **oʻz fon rasmingizni** yuboring.\n"
        "Taqdimot aynan siz tanlagan fon asosida tayyorlanadi: 👇",
        reply_markup=keyboards.get_theme_selection_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "skip_author_info", SlideCreation.waiting_for_author)
async def skip_author_info_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(author_info="")
    await state.set_state(SlideCreation.waiting_for_theme)
    await callback.message.answer(
        "🎨 **Slaydning orqa fonini (dizaynini) tanlang:**\n\n"
        "Oʻzingizga yoqqan orqa fon rangini tanlang yoki **oʻz fon rasmingizni** yuboring.\n"
        "Taqdimot aynan siz tanlagan fon asosida tayyorlanadi: 👇",
        reply_markup=keyboards.get_theme_selection_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "theme_custom_bg", SlideCreation.waiting_for_theme)
async def prompt_custom_bg_choice(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SlideCreation.waiting_for_custom_bg)
    await callback.message.answer(
        "🖼 **Slayd uchun orqa fon rasmini yuboring:**\n\n"
        "Galereyangizdan yoki Canva'dan yuklab olgan fon rasmingizni shu yerga **rasm (foto)** sifatida yuboring.\n"
        "Bot barcha slaydlarni ushbu rasm foni asosida chiroyli qilib tayyorlaydi! 🚀\n\n"
        "*(Fikringiz oʻzgarsa, quyidagi tugma orqali fon ranglariga qaytishingiz mumkin)*",
        reply_markup=keyboards.get_custom_bg_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "back_to_theme_selection", SlideCreation.waiting_for_custom_bg)
async def back_to_theme_selection(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.set_state(SlideCreation.waiting_for_theme)
    await callback.message.answer(
        "🎨 **Slaydning orqa fonini (dizaynini) tanlang:**\n\n"
        "Oʻzingizga yoqqan orqa fon rangini tanlang yoki **oʻz fon rasmingizni** yuboring.\n"
        "Taqdimot aynan siz tanlagan fon asosida tayyorlanadi: 👇",
        reply_markup=keyboards.get_theme_selection_keyboard(),
        parse_mode="Markdown"
    )

@router.message(SlideCreation.waiting_for_custom_bg, F.photo)
@router.message(SlideCreation.waiting_for_theme, F.photo)
async def process_custom_bg_photo(message: Message, state: FSMContext):
    photo = message.photo[-1]
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="bg_upload_", suffix=".jpg")
    os.close(tmp_fd)
    await message.bot.download(photo.file_id, destination=tmp_path)
    
    data = await state.get_data()
    topic = data.get("topic", "")
    slide_count = data.get("slide_count", 8)
    author_info = data.get("author_info", "")
    context_doc = data.get("context_document", "")
    slide_lang = data.get("slide_language", "uz")
    await state.clear()
    
    await generate_and_send_presentation(
        chat_message=message,
        user_id=message.from_user.id,
        topic=topic,
        slide_count=slide_count,
        author_info=author_info,
        theme_choice="auto",
        custom_bg=tmp_path,
        context_document=context_doc,
        slide_language=slide_lang
    )

@router.message(SlideCreation.waiting_for_custom_bg, F.document)
@router.message(SlideCreation.waiting_for_theme, F.document)
async def process_custom_bg_document(message: Message, state: FSMContext):
    doc = message.document
    mime = (doc.mime_type or "").lower()
    fname = (doc.file_name or "").lower()
    if mime.startswith("image/") or any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        tmp_fd, tmp_path = tempfile.mkstemp(prefix="bg_upload_", suffix=".jpg")
        os.close(tmp_fd)
        await message.bot.download(doc.file_id, destination=tmp_path)
        
        data = await state.get_data()
        topic = data.get("topic", "")
        slide_count = data.get("slide_count", 8)
        author_info = data.get("author_info", "")
        context_doc = data.get("context_document", "")
        slide_lang = data.get("slide_language", "uz")
        await state.clear()
        
        await generate_and_send_presentation(
            chat_message=message,
            user_id=message.from_user.id,
            topic=topic,
            slide_count=slide_count,
            author_info=author_info,
            theme_choice="auto",
            custom_bg=tmp_path,
            context_document=context_doc,
            slide_language=slide_lang
        )
    else:
        await message.answer(
            "⚠️ Iltimos, fon uchun **rasm (jpg, png)** yuboring yoki rang tanlashga qayting:",
            reply_markup=keyboards.get_custom_bg_keyboard(),
            parse_mode="Markdown"
        )

@router.message(SlideCreation.waiting_for_custom_bg, F.text)
async def invalid_custom_bg_text(message: Message, state: FSMContext):
    if await check_menu_navigation(message, state):
        return
    await message.answer(
        "⚠️ Iltimos, fon uchun **rasm (foto yoki skrinshot)** yuboring yoki rang tanlashga qayting:",
        reply_markup=keyboards.get_custom_bg_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data.startswith("theme_"), SlideCreation.waiting_for_theme)
async def process_theme_choice(callback: CallbackQuery, state: FSMContext):
    if callback.data == "theme_custom_bg":
        await prompt_custom_bg_choice(callback, state)
        return
    await callback.answer()
    theme_key = callback.data.replace("theme_", "")
    data = await state.get_data()
    topic = data.get("topic", "")
    if not topic:
        await callback.message.answer(
            "⚠️ Taqdimot mavzusi topilmadi yoki sessiya muddati o'tgan.\n"
            "Iltimos, '📊 Yangi slayd tayyorlash' tugmasini bosib qaytadan boshlang.",
            reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id))
        )
        await state.clear()
        return
    slide_count = data.get("slide_count", 8)
    author_info = data.get("author_info", "")
    context_doc = data.get("context_document", "")
    slide_lang = data.get("slide_language", "uz")
    await state.clear()
    await generate_and_send_presentation(
        chat_message=callback.message,
        user_id=callback.from_user.id,
        topic=topic,
        slide_count=slide_count,
        author_info=author_info,
        theme_choice=theme_key,
        context_document=context_doc,
        slide_language=slide_lang
    )

async def generate_and_send_presentation(chat_message: Message, user_id: int, topic: str, slide_count: int, author_info: str = "", theme_choice: str = "auto", custom_bg: str = None, context_document: str = "", slide_language: str = "uz"):
    time_estimate = "15-25 soniya" if slide_count >= 15 else "10-18 soniya"
    safe_topic = html.escape(topic)
    status_msg = await chat_message.answer(
        f"⏳ <b>'{safe_topic}'</b> mavzusida {slide_count} ta slayd tayyorlanmoqda...\n"
        f"🎨 Tanlangan dizayn va orqa fon shakllantirilmoqda...\n"
        f"🖼 Mavzuga mos sifatli rasmlar yuklanmoqda...\n"
        f"Bu taxminan {time_estimate} vaqt oladi, iltimos kuting...",
        parse_mode="HTML"
    )

    images_dir = None
    temp_dir = None

    try:
        if theme_choice == "gamma":
            if not gamma_service.is_gamma_available():
                await status_msg.edit_text(
                    f"⚠️ <b>Gamma API kaliti hali kiritilmagan.</b>\n"
                    f"Bot sizga yuqori sifatli infografik taqdimot tayyorlamoqda... ⏳",
                    parse_mode="HTML"
                )
                theme_choice = "blue"
            else:
                async def update_gamma_status(status_text: str):
                    try:
                        await status_msg.edit_text(f"⏳ <b>'{safe_topic}'</b>:\n{status_text}", parse_mode="HTML")
                    except Exception:
                        pass

                gamma_res = await gamma_service.generate_gamma_presentation(
                    topic=topic,
                    num_cards=slide_count,
                    author_info=author_info,
                    status_callback=update_gamma_status,
                    language=slide_language
                )
                if gamma_res.get("success") and gamma_res.get("file_path"):
                    pptx_path = gamma_res["file_path"]
                    gamma_url = gamma_res.get("gamma_url", "")

                    try:
                        content_mini = await generator.generate_presentation_content(topic, slide_count=min(slide_count, 6), language=slide_language, author_info=author_info)
                        speech_text = generator.generate_speech_script(content_mini, author_info=author_info)
                    except Exception:
                        speech_text = f"Taqdimot mavzusi: {topic}\n\nHimoya nutqi:\nHurmatli ustoz va talabalar, ushbu taqdimot '{topic}' mavzusiga bag'ishlangan bo'lib, zamonaviy axborotlar va vizual tuzilma asosida tayyorlandi."

                    user_cache_dir = os.path.join(os.path.dirname(__file__), "user_cache", str(user_id))
                    os.makedirs(user_cache_dir, exist_ok=True)
                    cached_pptx = os.path.join(user_cache_dir, "latest.pptx")
                    cached_speech = os.path.join(user_cache_dir, "latest_speech.txt")
                    cached_meta = os.path.join(user_cache_dir, "meta.json")

                    safe_name = "".join(c for c in topic[:30] if c.isalnum() or c in (" ", "_", "-")).strip() or "taqdimot"
                    shutil.copy2(pptx_path, cached_pptx)
                    with open(cached_speech, "w", encoding="utf-8") as f:
                        f.write(speech_text)
                    with open(cached_meta, "w", encoding="utf-8") as f:
                        json.dump({"topic": topic, "safe_name": safe_name, "gamma_url": gamma_url}, f, ensure_ascii=False)

                    user_info = await database.get_user(user_id) or {}
                    user_lang = user_info.get("language") or "uz"
                    is_sub = database.is_subscription_active(user_info)
                    is_unlimited_user = bool(user_info.get("is_unlimited")) or config.is_unlimited(user_id) or is_sub

                    if is_unlimited_user:
                        limit_caption = "♾ <b>Cheksiz (VIP / Boshqaruvchi)</b>"
                    elif is_sub:
                        exp_date = user_info.get("subscription_until", "")
                        limit_caption = f"⭐️ <b>Oylik obuna faol</b> (<code>{exp_date}</code> gacha)"
                    else:
                        cur_free = user_info.get("free_limit", 0)
                        cur_paid = user_info.get("paid_balance", 0)
                        rem_free = max(0, cur_free - 1) if cur_free > 0 else 0
                        rem_paid = (cur_paid - 1) if (cur_free == 0 and cur_paid > 0) else cur_paid
                        rem_total = rem_free + rem_paid
                        limit_caption = f"<b>{rem_total} ta</b> ({rem_free} ta bepul, {rem_paid} ta pulli)"

                    bot_user = await chat_message.bot.get_me()
                    share_url = f"https://t.me/share/url?url=https://t.me/{bot_user.username}?start=ref_{user_id}&text=Sun'iy%20intellekt%20yordamida%20talabalar%20uchun%20professional%20taqdimotlar%20tayyorlang!%20%F0%9F%8E%81%20Bepul%20sinab%20ko'rish:"

                    pptx_document = FSInputFile(pptx_path, filename=f"{safe_name}.pptx")
                    caption_html = (
                        f"🎉 <b>Gamma AI taqdimotingiz muvaffaqiyatli tayyorlandi!</b>\n\n"
                        f"📄 Mavzu: <i>{safe_topic}</i>\n"
                        f"🪄 AI platforma: <b>Gamma.app (Premium AI)</b>\n"
                        f"📊 Kartalar soni: <b>{slide_count} ta</b>\n"
                        f"📁 Format: <b>PowerPoint (.pptx)</b> — to'liq tahrirlanadigan\n"
                        f"💡 Qolgan limitingiz: {limit_caption}\n\n"
                        f"👇 <i>Taqdimotni Gamma vebda ko'rish, PDF ga aylantirish yoki nutq matnini olish uchun tugmalardan foydalaning:</i>"
                    )
                    await chat_message.reply_document(
                        document=pptx_document,
                        caption=caption_html,
                        reply_markup=keyboards.get_slide_action_keyboard(share_url=share_url, gamma_url=gamma_url, lang=user_lang),
                        parse_mode="HTML"
                    )
                    await database.consume_limit(user_id)
                    try:
                        await status_msg.delete()
                    except Exception:
                        pass
                    return
                else:
                    err_detail = gamma_res.get("error", "Noma'lum xatolik")
                    logger.warning(f"Gamma generation failed: {err_detail}, falling back to local Gemini engine...")
                    await status_msg.edit_text(
                        f"⚠️ <b>Gamma AI bildirishnomasi:</b> {html.escape(err_detail)}\n"
                        "🔄 <i>Bot avtomatik ravishda premium dizayn generatoriga o'tmoqda...</i> ⏳",
                        parse_mode="HTML"
                    )
                    theme_choice = "blue"

        # Generate with Gemini
        content = await generator.generate_presentation_content(
            topic,
            slide_count=slide_count,
            language=slide_language,
            author_info=author_info,
            theme_choice=theme_choice,
            context_document=context_document
        )
        
        # Fetch relevant images asynchronously
        images_dir = tempfile.mkdtemp(prefix="slayd_imgs_")
        images_map = await generator.fetch_images_for_presentation(content, images_dir)

        chosen_theme = content.get("theme", theme_choice if theme_choice != "auto" else "blue")
        if chosen_theme not in generator.THEMES:
            chosen_theme = "blue"

        # Build PPTX
        temp_dir = tempfile.mkdtemp(prefix="slayd_out_")
        safe_name = "".join(c for c in topic[:30] if c.isalnum() or c in (" ", "_", "-")).strip() or "taqdimot"
        pptx_path = os.path.join(temp_dir, f"{safe_name}.pptx")

        user_full_name = ""
        if chat_message and chat_message.from_user and not chat_message.from_user.is_bot:
            user_full_name = chat_message.from_user.full_name
        if not user_full_name:
            db_u = await database.get_user(user_id)
            if db_u and db_u.get("full_name"):
                user_full_name = db_u["full_name"]
        has_author = bool(author_info and author_info.strip())
        await asyncio.to_thread(
            generator.create_pptx_file,
            content,
            pptx_path,
            theme_name=chosen_theme,
            images_map=images_map,
            author_info=author_info,
            default_student_name=user_full_name if has_author else "",
            custom_bg=custom_bg,
            language=slide_language
        )

        # Generate defense speech text
        speech_text = generator.generate_speech_script(
            content, 
            author_info=author_info, 
            default_student_name=user_full_name if has_author else ""
        )

        # Save to user cache for on-demand PDF conversion & speech retrieval
        user_cache_dir = os.path.join(os.path.dirname(__file__), "user_cache", str(user_id))
        os.makedirs(user_cache_dir, exist_ok=True)
        cached_pptx = os.path.join(user_cache_dir, "latest.pptx")
        cached_speech = os.path.join(user_cache_dir, "latest_speech.txt")
        cached_meta = os.path.join(user_cache_dir, "meta.json")

        shutil.copy2(pptx_path, cached_pptx)
        with open(cached_speech, "w", encoding="utf-8") as f:
            f.write(speech_text)
        with open(cached_meta, "w", encoding="utf-8") as f:
            json.dump({"topic": topic, "safe_name": safe_name}, f, ensure_ascii=False)

        user_info = await database.get_user(user_id) or {}
        is_sub = database.is_subscription_active(user_info)
        is_unlimited_user = bool(user_info.get("is_unlimited")) or config.is_unlimited(user_id) or is_sub

        if is_unlimited_user:
            limit_caption = "♾ <b>Cheksiz (VIP / Boshqaruvchi)</b>"
        elif is_sub:
            exp_date = user_info.get("subscription_until", "")
            limit_caption = f"⭐️ <b>Oylik obuna faol</b> (<code>{exp_date}</code> gacha)"
        else:
            cur_free = user_info.get("free_limit", 0)
            cur_paid = user_info.get("paid_balance", 0)
            rem_free = max(0, cur_free - 1) if cur_free > 0 else 0
            rem_paid = (cur_paid - 1) if (cur_free == 0 and cur_paid > 0) else cur_paid
            rem_total = rem_free + rem_paid
            limit_caption = f"<b>{rem_total} ta</b> ({rem_free} ta bepul, {rem_paid} ta pulli)"

        if custom_bg and os.path.exists(custom_bg):
            theme_name = "🖼 Maxsus rasm foni"
        else:
            theme_info = generator.THEMES.get(chosen_theme, generator.THEMES["blue"])
            theme_name = theme_info.get("name", "Zamonaviy")
        total_slides_count = len(content.get('slides', [])) + (6 if has_author else 5)
        slides_breakdown = "(1-Titul, 2-Mavzu, 3-Reja, Asosiy qismlar, Xulosa, Adabiyotlar, E'tiboringiz uchun rahmat!)" if has_author else "(1-Mavzu, 2-Reja, Asosiy qismlar, Xulosa, Adabiyotlar, E'tiboringiz uchun rahmat!)"

        bot_user = await chat_message.bot.get_me()
        share_url = f"https://t.me/share/url?url=https://t.me/{bot_user.username}?start=ref_{user_id}&text=Sun'iy%20intellekt%20(Google%20Gemini)%20yordamida%20talabalar%20uchun%20professional%20taqdimotlar%20tayyorlang!%20%F0%9F%8E%81%20Bepul%20sinab%20ko'rish:"

        # 1. Send ONLY PPTX File!
        pptx_document = FSInputFile(pptx_path, filename=f"{safe_name}.pptx")
        caption_html = (
            f"🎉 <b>Taqdimotingiz muvaffaqiyatli tayyorlandi!</b>\n\n"
            f"📄 Mavzu: <i>{safe_topic}</i>\n"
            f"🎨 Dizayn: <b>{theme_name}</b>\n"
            f"📊 Jami slaydlar: <b>{total_slides_count} ta</b> {slides_breakdown}\n"
            f"📁 Format: <b>PowerPoint (.pptx)</b> — tahrirlash uchun\n"
            f"💡 Qolgan limitingiz: {limit_caption}\n\n"
            f"👇 <i>Taqdimotni PDF ga aylantirish yoki himoya nutq matnini (shpargalka) olish uchun quyidagi tugmalardan foydalaning:</i>"
        )
        try:
            await chat_message.reply_document(
                document=pptx_document,
                caption=caption_html,
                reply_markup=keyboards.get_slide_action_keyboard(share_url=share_url),
                parse_mode="HTML"
            )
        except Exception as send_err:
            logger.warning(f"HTML reply_document failed ({send_err}), retrying with plain text caption...")
            plain_caption = (
                f"🎉 Taqdimotingiz muvaffaqiyatli tayyorlandi!\n\n"
                f"📄 Mavzu: {topic}\n"
                f"🎨 Dizayn: {theme_name}\n"
                f"📊 Jami slaydlar: {total_slides_count} ta\n"
                f"📁 Format: PowerPoint (.pptx) — tahrirlash uchun\n\n"
                f"Taqdimotni PDF ga aylantirish yoki nutq matnini olish uchun tugmalardan foydalaning:"
            )
            await chat_message.reply_document(
                document=pptx_document,
                caption=plain_caption,
                reply_markup=keyboards.get_slide_action_keyboard(share_url=share_url)
            )

        # Decrement limit only after file is successfully delivered
        await database.consume_limit(user_id)

        await status_msg.delete()

    except Exception as e:
        logger.error(f"Xatolik: {e}")
        safe_err = html.escape(str(e))
        try:
            await status_msg.edit_text(
                f"❌ Kechirasiz, slayd tayyorlashda xatolik yuz berdi:\n<code>{safe_err}</code>\n\n"
                f"Limitlaringiz saqlanib qoldi. Iltimos, qayta urinib ko'ring yoki adminga murojaat qiling.",
                parse_mode="HTML"
            )
        except Exception:
            await status_msg.edit_text(
                "❌ Kechirasiz, slayd tayyorlashda xatolik yuz berdi.\n\nLimitlaringiz saqlanib qoldi. Iltimos, qayta urinib ko'ring."
            )
    finally:
        if custom_bg and os.path.exists(custom_bg):
            try:
                os.remove(custom_bg)
            except Exception:
                pass
        if images_dir and os.path.exists(images_dir):
            try:
                shutil.rmtree(images_dir, ignore_errors=True)
            except Exception:
                pass
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

@router.callback_query(F.data == "get_latest_pdf")
async def get_latest_pdf_handler(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user_cache_dir = os.path.join(os.path.dirname(__file__), "user_cache", str(user_id))
    cached_pptx = os.path.join(user_cache_dir, "latest.pptx")
    meta_path = os.path.join(user_cache_dir, "meta.json")

    if not os.path.exists(cached_pptx):
        await callback.message.answer(
            "⚠️ Oxirgi yaratilgan taqdimot topilmadi yoki muddati o'tgan.\n"
            "«📄 PPTX ni PDF ga aylantirish» bo'limi orqali faylingizni yuborib PDF olishingiz mumkin."
        )
        return

    status_msg = await callback.message.answer("⏳ Taqdimot PDF formatiga aylantirilmoqda, bir necha soniya kuting...")
    try:
        safe_name = "taqdimot"
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    safe_name = meta.get("safe_name", "taqdimot")
            except Exception:
                pass

        pdf_path = os.path.join(user_cache_dir, f"{safe_name}.pdf")
        await asyncio.to_thread(generator.convert_pptx_to_pdf, cached_pptx, pdf_path)

        pdf_doc = FSInputFile(pdf_path, filename=f"{safe_name}.pdf")
        await callback.message.reply_document(
            document=pdf_doc,
            caption=(
                f"📑 **Taqdimotning PDF nusxasi**\n\n"
                f"✨ Barcha slaydlar, rasmlar va ma'lumotlar bilan yuqori sifatli PDF formatda.\n"
                f"📱 Telefon yoki kompyuterda ochish, chop etish va ulashish uchun juda qulay! 🚀"
            ),
            parse_mode="Markdown"
        )
        await status_msg.delete()
    except Exception as e:
        logger.error(f"Latest PDF error: {e}")
        await status_msg.edit_text(f"❌ PDF ga aylantirishda xatolik yuz berdi: {e}")

@router.callback_query(F.data == "get_latest_speech")
async def get_latest_speech_handler(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    user_cache_dir = os.path.join(os.path.dirname(__file__), "user_cache", str(user_id))
    cached_speech = os.path.join(user_cache_dir, "latest_speech.txt")

    if not os.path.exists(cached_speech):
        await callback.message.answer("⚠️ Himoya nutq matni topilmadi.")
        return

    try:
        with open(cached_speech, "r", encoding="utf-8") as f:
            speech_text = f.read()

        if len(speech_text) <= 3900:
            await callback.message.answer(speech_text, parse_mode=None)
        else:
            doc_file = FSInputFile(cached_speech, filename="Himoya_nutq_matni.txt")
            await callback.message.reply_document(
                document=doc_file,
                caption="🎤 <b>Taqdimot himoyasi uchun to'liq nutq matni (doklad / shpargalka)</b>",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Speech script send error: {e}")
        await callback.message.answer("❌ Nutq matnini yuklashda xatolik yuz berdi.")

@router.callback_query(F.data == "cancel_generation")
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Bekor qilindi")
    user_lang = await database.get_user_language(callback.from_user.id)
    await callback.message.answer(
        locales.get_text("cancelled", user_lang),
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id), lang=user_lang)
    )


# ================= ADMIN BUYRUQLARI =================
@router.message(Command("add_limit"))
async def admin_add_limit(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    # Usage: /add_limit <user_id> <count>
    args = message.text.split()
    if len(args) != 3:
        await message.answer("Noto'g'ri format!\nFoydalanish: `/add_limit <foydalanuvchi_id> <soni>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        amount = int(args[2])
        success = await database.add_paid_limit(target_id, amount)
        if success:
            await message.answer(f"✅ Foydalanuvchi `{target_id}` ga **{amount} ta** limit qo'shildi!", parse_mode="Markdown")
            try:
                await message.bot.send_message(
                    target_id,
                    f"🎉 **Hisobingiz to'ldirildi!**\n\nSizga **{amount} ta** yangi taqdimot limiti qo'shildi. Marhamat, botdan foydalanishingiz mumkin!",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        else:
            await message.answer(f"❌ Foydalanuvchi topilmadi: `{target_id}`")
    except ValueError:
        await message.answer("ID va limit soni butun son bo'lishi kerak!")

@router.message(Command("add_sub"))
@router.message(Command("add_obuna"))
async def admin_add_subscription(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    # Usage: /add_sub <user_id> [days=30]
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Noto'g'ri format!\nFoydalanish: `/add_sub <foydalanuvchi_id> [kun=30]`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        days = int(args[2]) if len(args) >= 3 else 30
        res = await database.activate_subscription(target_id, days=days)
        if res["success"]:
            exp = res["expires_at"]
            await message.answer(f"✅ Foydalanuvchi `{target_id}` ga **{days} kunlik** oylik obuna faollashtirildi!\nAmal qilish muddati: `{exp}`", parse_mode="Markdown")
            try:
                await message.bot.send_message(
                    target_id,
                    f"🎉 **Ajoyib yangilik! Sizga {days} kunlik Oylik Obuna faollashtirildi!**\n\n"
                    f"👑 Endi siz ushbu muddat davomida **mutlaqo cheksiz** taqdimotlar yaratishingiz mumkin!\n"
                    f"⏳ Amal qilish muddati: `{exp}` gacha.\n\n"
                    f"Botdan unumli foydalaning! 🚀",
                    parse_mode="Markdown"
                )
            except Exception:
                pass
        else:
            await message.answer(f"❌ Foydalanuvchi topilmadi: `{target_id}`")
    except ValueError:
        await message.answer("ID va kun soni butun son bo'lishi kerak!")

@router.message(Command("reply"))
async def admin_reply(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    # Usage: /reply <user_id> <xabar matni>
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.answer("Noto'g'ri format!\nFoydalanish: `/reply <foydalanuvchi_id> <javob matni>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        reply_text = args[2]

        safe_reply = html.escape(reply_text)
        try:
            await message.bot.send_message(
                chat_id=target_id,
                text=f"👨‍💻 <b>Admindan javob:</b>\n\n{safe_reply}",
                parse_mode="HTML"
            )
        except Exception:
            await message.bot.send_message(
                chat_id=target_id,
                text=f"👨‍💻 Admindan javob:\n\n{reply_text}"
            )
        await message.answer(f"✅ Javob foydalanuvchi <code>{target_id}</code> ga yuborildi!", parse_mode="HTML")
    except ValueError:
        await message.answer("ID raqami butun son bo'lishi kerak!")
    except Exception as e:
        await message.answer(f"❌ Xabar yuborishda xatolik: {e}")

@router.message(Command("set_vip"))
@router.message(Command("vip"))
async def admin_set_vip(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    # Usage: /set_vip <user_id>
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Noto'g'ri format!\nFoydalanish: `/set_vip <foydalanuvchi_id>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        await database.set_unlimited_user(target_id, True)
        await message.answer(f"👑 Foydalanuvchi `{target_id}` ga doimiy **CHEKSIZ (VIP)** maqomi berildi!", parse_mode="Markdown")
        try:
            await message.bot.send_message(
                target_id,
                "👑 <b>Tabriklaymiz! Sizning hisobingizga doimiy CHEKSIZ (VIP) maqomi berildi!</b>\n\n"
                "Endi siz botdan mutlaqo bepul va limitsiz istalgancha yangi taqdimotlar yaratishingiz mumkin! 🚀",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except ValueError:
        await message.answer("Foydalanuvchi ID raqami butun son bo'lishi kerak!")

@router.message(Command("remove_vip"))
async def admin_remove_vip(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    # Usage: /remove_vip <user_id>
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Noto'g'ri format!\nFoydalanish: `/remove_vip <foydalanuvchi_id>`", parse_mode="Markdown")
        return

    try:
        target_id = int(args[1])
        await database.set_unlimited_user(target_id, False)
        await message.answer(f"❌ Foydalanuvchi `{target_id}` dan VIP maqomi olib tashlandi.", parse_mode="Markdown")
        try:
            await message.bot.send_message(
                target_id,
                "ℹ️ Sizning hisobingizdagi VIP maqomi bekor qilindi.",
                parse_mode="HTML"
            )
        except Exception:
            pass
    except ValueError:
        await message.answer("Foydalanuvchi ID raqami butun son bo'lishi kerak!")

@router.message(Command("set_gamma"))
async def admin_set_gamma(message: Message):
    if not config.is_admin(message.from_user.id):
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        curr = "Sozlangan ✅" if gamma_service.is_gamma_available() else "Sozlanmagan ❌"
        await message.answer(
            f"ℹ️ <b>Gamma API kaliti holati:</b> {curr}\n\n"
            "Kalitni sozlash uchun quyidagicha yuboring:\n"
            "<code>/set_gamma YOUR_GAMMA_API_KEY</code>",
            parse_mode="HTML"
        )
        return
    new_key = args[1].strip()
    if gamma_service.save_gamma_key(new_key):
        await message.answer("✅ <b>Gamma API kaliti muvaffaqiyatli saqlandi!</b>\nEndi bot orqali Gamma AI taqdimotlari yaratish to'liq faol.", parse_mode="HTML")
    else:
        await message.answer("❌ API kalitini saqlashda xatolik yuz berdi.")

@router.message(F.text.in_({"⚙️ Admin panel", "⚙️ Админ панель", "⚙️ Admin Panel"}))
@router.message(Command("stats"))
async def admin_panel(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    stats = await database.get_stats()
    gamma_status = "Faol ✅" if gamma_service.is_gamma_available() else "Sozlanmagan ⚠️"
    text = (
        f"⚙️ **Admin paneli va Statistika:**\n\n"
        f"👥 Jami foydalanuvchilar: **{stats['total_users']} nafar**\n"
        f"🎨 Slayd tayyorlaganlar: **{stats.get('active_users', 0)} nafar**\n"
        f"📑 Jami yaratilgan taqdimotlar: **{stats['total_slides']} ta**\n"
        f"🤝 Jami taklif qilingan do'stlar: **{stats.get('total_referrals', 0)} ta**\n"
        f"🪄 Gamma AI integratsiyasi: **{gamma_status}**\n\n"
        f"🔑 Gamma kalitini kiritish: `/set_gamma <API_KEY>`\n"
        f"👑 VIP maqom berish: `/set_vip <id>`\n"
        f"🚫 VIP ni bekor qilish: `/remove_vip <id>`\n"
        f"➕ Limit qo'shish: `/add_limit <id> <soni>`\n"
        f"⭐️ Obuna yoqish: `/add_sub <id> [kun]`\n"
        f"💬 Javob qaytarish: `/reply <id> <matn>`"
    )
    await message.answer(text, reply_markup=keyboards.get_admin_keyboard(), parse_mode="Markdown")

@router.callback_query(F.data == "admin_stats")
async def admin_stats_callback(callback: CallbackQuery):
    if not config.is_admin(callback.from_user.id):
        await callback.answer("Ruxsat berilmagan!", show_alert=True)
        return
    await callback.answer()
    stats = await database.get_stats()
    text = (
        f"📈 <b>Bot statistikasi:</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total_users']} nafar</b>\n"
        f"🎨 Slayd tayyorlagan foydalanuvchilar: <b>{stats.get('active_users', 0)} nafar</b>\n"
        f"📑 Jami tayyorlangan taqdimotlar: <b>{stats['total_slides']} ta</b>\n"
        f"🤝 Jami taklif qilingan do'stlar: <b>{stats.get('total_referrals', 0)} ta</b>"
    )
    await callback.message.answer(text, parse_mode="HTML")

@router.message(F.voice)
@router.message(F.audio)
async def handle_voice_presentation(message: Message, state: FSMContext):
    # Check limit first
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or ""
    )
    user_lang = user.get("language") or "uz"
    is_sub = database.is_subscription_active(user)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id) or is_sub
    total_remaining = user["free_limit"] + user["paid_balance"]

    if not is_unlimited and total_remaining <= 0:
        bot_user = await message.bot.get_me()
        await message.answer(
            locales.get_text("no_limit", user_lang),
            reply_markup=keyboards.get_no_limit_keyboard(bot_user.username, message.from_user.id, lang=user_lang),
            parse_mode="HTML"
        )
        return

    status_msg = await message.reply("🎙 **Ovozli xabaringiz qabul qilindi!**\nAI audio yozuvni tinglab, mavzuni aniqlamoqda... ⏳")
    
    file_id = message.voice.file_id if message.voice else message.audio.file_id
    tmp_fd, tmp_audio = tempfile.mkstemp(prefix="user_voice_", suffix=".oga" if message.voice else ".mp3")
    os.close(tmp_fd)

    try:
        await message.bot.download(file_id, destination=tmp_audio)
        parsed = await generator.parse_voice_to_presentation_details(tmp_audio)
        
        topic = parsed.get("topic", "").strip()
        slide_count = parsed.get("slide_count", 8)
        author_info = parsed.get("author_info", "").strip()

        if not topic:
            await status_msg.edit_text(
                "❌ **Ovozli xabardan aniq mavzuni ajratib boʻlmadi.**\n\n"
                "Iltimos, mavzuni aniqroq qilib qayta audio yozib yuboring yoki matn koʻrinishida yozing."
            )
            return

        raw_lang = (parsed.get("language") or "").lower()
        if "ru" in raw_lang or "rus" in raw_lang:
            slide_lang = "ru"
        elif "en" in raw_lang or "eng" in raw_lang:
            slide_lang = "en"
        elif "tr" in raw_lang or "turk" in raw_lang:
            slide_lang = "tr"
        elif "kk" in raw_lang or "kaz" in raw_lang:
            slide_lang = "kk"
        elif "ky" in raw_lang or "kyr" in raw_lang:
            slide_lang = "ky"
        elif "tg" in raw_lang or "taj" in raw_lang:
            slide_lang = "tg"
        elif "de" in raw_lang or "ger" in raw_lang or "nem" in raw_lang:
            slide_lang = "de"
        else:
            slide_lang = user_lang

        await state.update_data(
            topic=topic,
            slide_count=slide_count,
            author_info=author_info,
            slide_language=slide_lang
        )
        await state.set_state(SlideCreation.waiting_for_theme)

        lang_info = locales.get_slide_lang_info(slide_lang)
        author_display = f"\n👤 **Muallif:** {author_info}" if author_info else ""
        await status_msg.delete()
        await message.answer(
            f"🎙 **Ovozli xabaringiz muvaffaqiyatli tushunildi!** 🚀\n\n"
            f"📌 **Aniqlangan mavzu:** *{topic}*\n"
            f"🌐 **Slayd tili:** *{lang_info['name']}*\n"
            f"📊 **Slaydlar soni:** *{slide_count} ta*{author_display}\n\n"
            f"🎨 **Slaydning orqa fonini (dizaynini) tanlang:**\n"
            f"Quyidagi ranglardan birini tanlang yoki oʻz fon rasmingizni yuboring: 👇",
            reply_markup=keyboards.get_theme_selection_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Voice handling error: {e}")
        await status_msg.edit_text(f"❌ Ovozli xabarni qayta ishlashda xatolik yuz berdi:\n`{e}`")
    finally:
        if os.path.exists(tmp_audio):
            try:
                os.remove(tmp_audio)
            except Exception:
                pass

@router.message(F.photo)
async def handle_photo_media(message: Message, state: FSMContext):
    photo = message.photo[-1]
    user_lang = await database.get_user_language(message.from_user.id)
    await state.set_state(MediaChoiceState.waiting_for_action)
    await state.update_data(
        media_file_id=photo.file_id,
        media_type="photo",
        media_file_name="photo.jpg"
    )
    if user_lang == "ru":
        prompt_text = (
            "📷 **Фото книги или конспекта получено!**\n\n"
            "Искусственный интеллект изучит материал и создаст презентацию по содержанию."
        )
    elif user_lang == "en":
        prompt_text = (
            "📷 **Study material / notes photo received!**\n\n"
            "AI will analyze the content and compose a structured presentation."
        )
    else:
        prompt_text = (
            "📷 **Kitob beti yoki konspekt rasmi qabul qilindi!**\n\n"
            "Sun'iy intellekt rasm ichidagi matn va ma'lumotlarni o'rganib, to'liq taqdimot tayyorlab beradi."
        )
    await message.reply(
        prompt_text,
        reply_markup=keyboards.get_media_choice_keyboard(is_doc=False, lang=user_lang),
        parse_mode="Markdown"
    )

@router.message(F.document)
async def handle_document_media(message: Message, state: FSMContext):
    doc = message.document
    fname = (doc.file_name or "document").lower()
    user_lang = await database.get_user_language(message.from_user.id)
    
    if (doc.mime_type or "").startswith("image/") or any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        await state.set_state(MediaChoiceState.waiting_for_action)
        await state.update_data(
            media_file_id=doc.file_id,
            media_type="photo",
            media_file_name=doc.file_name or "image.jpg"
        )
        if user_lang == "ru":
            prompt_text = "🖼 **Изображение получено!**\n\nСоздать презентацию на основе этого материала?"
        elif user_lang == "en":
            prompt_text = "🖼 **Image received!**\n\nCreate a presentation based on this material?"
        else:
            prompt_text = "🖼 **Rasm hujjati qabul qilindi!**\n\nUshbu material asosida taqdimot tayyorlansinmi?"
        await message.reply(
            prompt_text,
            reply_markup=keyboards.get_media_choice_keyboard(is_doc=False, lang=user_lang),
            parse_mode="Markdown"
        )
        return

    await state.set_state(MediaChoiceState.waiting_for_action)
    await state.update_data(
        media_file_id=doc.file_id,
        media_type="document",
        media_file_name=doc.file_name or "hujjat"
    )
    is_pptx = fname.endswith(".pptx") or fname.endswith(".ppt")
    if user_lang == "ru":
        prompt_text = f"📄 **'{doc.file_name or 'Документ'}' получен!**\n\nВыберите действие:"
    elif user_lang == "en":
        prompt_text = f"📄 **'{doc.file_name or 'Document'}' received!**\n\nChoose an action:"
    else:
        prompt_text = f"📄 **'{doc.file_name or 'Hujjat'}' qabul qilindi!**\n\nKerakli amalni tanlang:"
    
    await message.reply(
        prompt_text,
        reply_markup=keyboards.get_media_choice_keyboard(is_doc=is_pptx, lang=user_lang),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "media_to_slides", MediaChoiceState.waiting_for_action)
async def media_to_slides_callback(callback: CallbackQuery, state: FSMContext):
    user = await database.get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or "",
        full_name=callback.from_user.full_name or ""
    )
    is_sub = database.is_subscription_active(user)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(callback.from_user.id) or is_sub
    total_remaining = user["free_limit"] + user["paid_balance"]

    if not is_unlimited and total_remaining <= 0:
        bot_user = await callback.bot.get_me()
        await callback.message.answer(
            "⚠️ **Kechirasiz, sizda limitlar tugagan!**\n\n"
            "Yangi taqdimot yaratish uchun limit xarid qiling yoki doʻstlaringizni taklif qiling!",
            reply_markup=keyboards.get_no_limit_keyboard(bot_user.username, callback.from_user.id),
            parse_mode="Markdown"
        )
        await callback.answer()
        return

    data = await state.get_data()
    file_id = data.get("media_file_id")
    fname = data.get("media_file_name", "material")
    ext = os.path.splitext(fname)[1].lower() or (".jpg" if data.get("media_type") == "photo" else ".pdf")
    
    await callback.answer()
    status_msg = await callback.message.answer("⏳ **Material (kitob/konspekt/hujjat) AI tomonidan oʻrganilmoqda...**\nAsosiy faktlar va konspekt matni ajratilmoqda...")

    tmp_fd, tmp_file = tempfile.mkstemp(prefix="user_media_", suffix=ext)
    os.close(tmp_fd)

    try:
        await callback.bot.download(file_id, destination=tmp_file)
        extracted = await generator.extract_topic_and_context_from_document_or_image(tmp_file)
        
        topic = extracted.get("topic", "").strip() or "Hujjat asosidagi taqdimot"
        summary = extracted.get("summary", "").strip()
        suggested_slides = extracted.get("suggested_slides", 8)

        user_lang = user.get("language") or "uz"
        await state.update_data(
            topic=topic,
            slide_count=suggested_slides,
            author_info="",
            context_document=summary,
            slide_language=user_lang
        )
        await state.set_state(SlideCreation.waiting_for_theme)

        await status_msg.delete()
        await callback.message.answer(
            f"📚 **Materialingiz muvaffaqiyatli tahlil qilindi!** 🎯\n\n"
            f"📌 **Aniqlangan mavzu:** *{topic}*\n"
            f"📊 **Tavsiya etilgan slaydlar:** *{suggested_slides} ta*\n"
            f"📝 **Konspekt:** *Hujjatdagi asosiy gʻoyalar va maʼlumotlar ajratib olindi.*\n\n"
            f"🎨 **Slaydning orqa fonini (dizaynini) tanlang:**",
            reply_markup=keyboards.get_theme_selection_keyboard(),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Media extraction error: {e}")
        await status_msg.edit_text(f"❌ Materialni tahlil qilishda xatolik yuz berdi:\n`{e}`")
    finally:
        if os.path.exists(tmp_file):
            try:
                os.remove(tmp_file)
            except Exception:
                pass

@router.callback_query(F.data == "media_to_pdf", MediaChoiceState.waiting_for_action)
async def media_to_pdf_callback(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    file_id = data.get("media_file_id")
    fname = data.get("media_file_name", "document")
    m_type = data.get("media_type")
    await state.clear()
    await callback.answer()

    if m_type == "photo":
        status_msg = await callback.message.answer("⏳ Rasm PDF ga aylantirilmoqda...")
        tmp_dir = tempfile.mkdtemp(prefix="img_to_pdf_")
        try:
            in_path = os.path.join(tmp_dir, "input.jpg")
            out_pdf = os.path.join(tmp_dir, "rasm_hujjati.pdf")
            await callback.bot.download(file_id, destination=in_path)
            await asyncio.to_thread(generator.convert_images_to_pdf, [in_path], out_pdf)
            pdf_doc = FSInputFile(out_pdf, filename="rasm_hujjati.pdf")
            await callback.message.reply_document(
                document=pdf_doc,
                caption="✅ **Rasmingiz sifatli PDF hujjatga muvaffaqiyatli aylantirildi!** 📄✨",
                parse_mode="Markdown"
            )
            await status_msg.delete()
        except Exception as e:
            logger.error(f"Photo to PDF error: {e}")
            await status_msg.edit_text(f"❌ Xatolik yuz berdi: `{e}`")
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
    else:
        if fname.lower().endswith(".pptx"):
            status_msg = await callback.message.answer("⏳ Taqdimot (.pptx) PDF ga aylantirilmoqda...")
            tmp_dir = tempfile.mkdtemp(prefix="pptx_to_pdf_")
            try:
                in_pptx = os.path.join(tmp_dir, fname)
                base_name = os.path.splitext(fname)[0] or "taqdimot"
                out_pdf = os.path.join(tmp_dir, f"{base_name}.pdf")
                await callback.bot.download(file_id, destination=in_pptx)
                await asyncio.to_thread(generator.convert_pptx_to_pdf, in_pptx, out_pdf)
                pdf_doc = FSInputFile(out_pdf, filename=f"{base_name}.pdf")
                await callback.message.reply_document(
                    document=pdf_doc,
                    caption="✅ **Taqdimotingiz sifatli PDF hujjatga aylantirildi!** 📄✨",
                    parse_mode="Markdown"
                )
                await status_msg.delete()
            except Exception as e:
                logger.error(f"Doc PPTX to PDF error: {e}")
                await status_msg.edit_text(f"❌ Xatolik yuz berdi: `{e}`")
            finally:
                shutil.rmtree(tmp_dir, ignore_errors=True)
        else:
            await callback.message.answer(
                "ℹ️ PDF ga aylantirish faqat **rasmlar** yoki **PowerPoint (.pptx)** fayllari uchun moʻljallangan.\n"
                "Ushbu fayldan slayd yasash uchun **'📊 Ushbu hujjatdan taqdimot yasash'** tugmasini bosing."
            )

