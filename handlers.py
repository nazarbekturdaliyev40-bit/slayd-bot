import os
import json
import tempfile
import logging
import shutil
import asyncio
import html
from aiogram import Router, F
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import config
import database
import keyboards
import generator

logger = logging.getLogger(__name__)
router = Router()

class SlideCreation(StatesGroup):
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

class MediaChoiceState(StatesGroup):
    waiting_for_action = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject = None):
    await state.clear()
    
    # Check if user can be counted as a referral
    existing_user = await database.get_user(message.from_user.id)
    can_be_referred = (existing_user is None) or (existing_user.get("referrer_id") is None)

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

    welcome_text = (
        f"Assalomu alaykum, {message.from_user.first_name}! 👋\n\n"
        f"🤖 Ushbu bot sun'iy intellekt (Google Gemini) yordamida rasmlar, infografikalar va ma'lumotlar bilan boyitilgan professional **PowerPoint (.pptx)** hamda **PDF (.pdf)** taqdimotlarini tayyorlab beradi.\n\n"
        f"⚡️ **Yangi imkoniyatlar (boshqa botlarda yo'q):**\n"
        f"🎙 **Ovozli xabar:** Istalgan vaqtda mavzuni audio tarzda ayting, bot oʻzi tushunib slayd yasaydi!\n"
        f"📚 **Kitob / Konspekt / Hujjat:** Kitob beti rasmini yoki PDF/Word fayl tashlang, bot undan slayd chiqarib beradi!\n"
        f"📊 **Standart slayd:** Quyidagi **'📊 Yangi slayd tayyorlash'** tugmasi orqali mavzu kiritish.\n\n"
        f"🎁 Sizda **{user['free_limit']} ta bepul taqdimot** limiti mavjud!\n"
        f"👥 Do'stlaringizni taklif qilib (har 2 ta do'st uchun **+1 ta limit**) bepul limitlar olishingiz mumkin!\n\n"
        f"Quyidagi menyudan foydalaning yoki toʻgʻridan-toʻgʻri **ovoz/fayl** yuboring:"
    )
    await message.answer(
        welcome_text,
        reply_markup=keyboards.get_main_menu(is_admin=is_admin),
        parse_mode="Markdown"
    )

@router.message(F.text == "🎁 Bepul limit olish")
async def show_referral_program(message: Message):
    bot_user = await message.bot.get_me()
    stats = await database.get_referral_stats(message.from_user.id)
    ref_link = f"https://t.me/{bot_user.username}?start=ref_{message.from_user.id}"
    
    text = (
        f"🎁 **Do'stlarni taklif qiling va bepul limit oling!**\n\n"
        f"Har **2 ta do'stingiz** ushbu havola orqali botga kirsa, sizga **+1 ta yangi taqdimot yaratish limiti** sovg'a qilinadi!\n\n"
        f"📊 **Sizning referal statistikangiz:**\n"
        f"👥 Taklif qilingan do'stlar: **{stats['invited_count']} nafar**\n"
        f"🎁 Olingan bonus limitlar: **{stats['earned_limits']} ta**\n"
        f"⏳ Keyingi limit uchun kerak: **{stats['needed_for_next']} ta do'st**\n\n"
        f"🔗 **Sizning shaxsiy referal havolangiz:**\n"
        f"`{ref_link}`\n\n"
        f"👇 *Quyidagi tugmani bosing va havolani do'stlaringizga yoki guruhlarga yuboring:*"
    )
    await message.answer(
        text,
        reply_markup=keyboards.get_referral_keyboard(bot_user.username, message.from_user.id),
        parse_mode="Markdown"
    )

@router.message(F.text == "👤 Mening profilim")
async def show_profile(message: Message):
    user = await database.get_user(message.from_user.id)
    if not user:
        user = await database.get_or_create_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username or "",
            full_name=message.from_user.full_name or ""
        )
    
    stats = await database.get_referral_stats(message.from_user.id)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id)
    is_sub = database.is_subscription_active(user)
    total_remaining = user["free_limit"] + user["paid_balance"]
    
    if is_unlimited:
        text = (
            f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
            f"🆔 ID: `{user['telegram_id']}`\n"
            f"👑 **Tarif:** Mutlaqo Tekin va Cheksiz (Bot Egasi / VIP)\n"
            f"✨ **Mavjud limit:** ♾ **Cheksiz (Umuman tugamaydi)**\n"
            f"📊 **Jami yaratilgan slaydlar:** **{user['total_generated']} ta**\n"
            f"👥 **Taklif qilgan do'stlaringiz:** **{stats['invited_count']} nafar**\n\n"
            f"🎉 **Siz bot egasisiz!** Barcha xizmatlar va slaydlar siz uchun 100% MUTLAQO TEKIN va CHEKSIZ!\n"
            f"Xohlagancha slayd yaratishingiz mumkin, to'lov qilish shart emas."
        )
    elif is_sub:
        sub_until = user.get("subscription_until", "")
        text = (
            f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
            f"🆔 ID: `{user['telegram_id']}`\n"
            f"👑 **Tarif:** ⭐️ **Oylik cheksiz obuna faol!**\n"
            f"⏳ **Amal qilish muddati:** `{sub_until}` gacha\n"
            f"✨ **Mavjud limit:** ♾ **Obuna davrida cheksiz!**\n"
            f"📊 **Jami yaratilgan slaydlar:** **{user['total_generated']} ta**\n"
            f"👥 **Taklif qilgan do'stlaringiz:** **{stats['invited_count']} nafar**\n\n"
            f"✅ Siz ushbu muddat davomida bemalol istalgancha yangi slaydlar yaratishingiz mumkin! 🚀"
        )
    else:
        text = (
            f"👤 **Foydalanuvchi ma'lumotlari:**\n\n"
            f"🆔 ID: `{user['telegram_id']}`\n"
            f"🎁 Boshlang'ich bepul limit: **{user['free_limit']} ta**\n"
            f"💳 Pulli balans: **{user['paid_balance']} ta**\n"
            f"✨ Jami mavjud limit: **{total_remaining} ta**\n"
            f"📊 Jami tayyorlangan: **{user['total_generated']} ta**\n"
            f"👥 Taklif qilgan do'stlaringiz: **{stats['invited_count']} nafar** (sovg'a: {stats['earned_limits']} ta limit)\n\n"
        )
        if total_remaining == 0:
            text += (
                "⚠️ **Sizning limitingiz tugagan!**\n\n"
                "💡 Yangi taqdimot yaratish uchun 1 ta slayd (5 000 so'm) yoki oylik cheksiz obuna (20 000 so'm) xarid qilishingiz, yoki do'stlaringizni taklif qilib bepul limit olishingiz mumkin."
            )
        else:
            text += "✅ Siz bemalol yangi slayd yaratishingiz mumkin!"

    await message.answer(text, parse_mode="Markdown")

@router.message(F.text.in_({"💳 Limit sotib olish", "💳 Limit va Obuna", "💳 Tariflar"}))
async def buy_limits(message: Message):
    user = await database.get_user(message.from_user.id)
    is_unlimited = (user and bool(user.get("is_unlimited"))) or config.is_unlimited(message.from_user.id)
    if is_unlimited:
        await message.answer(
            "👑 **Siz VIP / Cheksiz ta'rifdasiz!**\n\n"
            "Sizga hech qanday to'lov qilish yoki limit sotib olish kerak emas. "
            "Sizning hisobingizda **♾ CHEKSIZ va 100% MUTLAQO TEKIN** taqdimot yaratish imkoniyati yoqilgan!\n\n"
            "Marhamat, bemalol yangi slaydlar yaratavering! 🚀",
            parse_mode="Markdown"
        )
        return

    text = (
        f"💳 **Tariflar va To'lov:**\n\n"
        f"🎁 **2 ta bepul taqdimot** — har bir yangi foydalanuvchiga taqdim etiladi!\n\n"
        f"2 ta bepul limitdan so'ng:\n"
        f"1️⃣ **1 ta taqdimot** — **5 000 so'm**\n"
        f"2️⃣ **3 ta taqdimot** — **12 000 so'm** (chegirma bilan)\n"
        f"👑 **Oylik obuna (1 oy)** — **20 000 so'm** (1 oy davomida mutlaqo CHEKSIZ taqdimotlar yaratish! 🚀)\n\n"
        f"📌 **To'lov qilish tartibi:**\n"
        f"1. Quyidagi kartaga kerakli summani o'tkazing:\n"
        f"💳 Karta raqami: `{config.CARD_NUMBER}`\n"
        f"👤 Egasi: **{config.CARD_HOLDER}**\n\n"
        f"2. Pul o'tkazgach, pastdagi **'🧾 To'lov chekini yuborish'** tugmasini bosing va to'lov chekining rasmini (skrinshotini) botga yuboring.\n"
        f"3. 5 daqiqa ichida admin chekni tasdiqlaydi va limitingiz avtomatik qo'shiladi!"
    )
    await message.answer(text, reply_markup=keyboards.get_payment_keyboard(config.ADMIN_USERNAME), parse_mode="Markdown")

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

    admin_targets = set([config.ADMIN_ID] + config.UNLIMITED_USERS)
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

    admin_targets = set([config.ADMIN_ID] + config.UNLIMITED_USERS)
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
async def process_receipt_text_invalid(message: Message):
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
@router.message(F.text.in_({"👨‍💻 Adminga murojaat", "Adminga murojaat"}))
async def contact_admin_menu(message: Message, state: FSMContext):
    await state.clear()
    if config.ADMIN_USERNAME:
        await message.answer(
            f"👨‍💻 <b>Admin bilan bog'lanish:</b>\n\n"
            f"Adminga yozish uchun: @{config.ADMIN_USERNAME}",
            parse_mode="HTML"
        )
        return

    await state.set_state(AdminContactState.waiting_for_message)
    await message.answer(
        "✍️ <b>Adminga xabar yuborish:</b>\n\n"
        "Savolingiz yoki murojaatingizni shu yerga yozing. Admin ko'rib chiqib, sizga tez orada javob beradi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_contact")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "contact_admin")
async def contact_admin_callback(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if config.ADMIN_USERNAME:
        await callback.message.answer(
            f"👨‍💻 <b>Admin bilan bog'lanish:</b>\n\n"
            f"Adminga yozish uchun: @{config.ADMIN_USERNAME}",
            parse_mode="HTML"
        )
        return

    await state.set_state(AdminContactState.waiting_for_message)
    await callback.message.answer(
        "✍️ <b>Adminga xabar yuborish:</b>\n\n"
        "Savolingiz yoki murojaatingizni shu yerga yozing. Admin ko'rib chiqib, sizga tez orada javob beradi.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_contact")]
        ]),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "cancel_contact")
async def cancel_contact_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Murojaat bekor qilindi.")
    await callback.message.answer("❌ Adminga murojaat bekor qilindi.", reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id)))

@router.message(AdminContactState.waiting_for_message, F.text)
async def process_admin_contact(message: Message, state: FSMContext):
    if message.text.startswith("/") or message.text in [
        "📊 Yangi slayd tayyorlash", "📄 PPTX ni PDF ga aylantirish",
        "🖼 Rasmni PDF ga aylantirish", "👤 Mening profilim",
        "🎁 Bepul limit olish", "💳 Limit va Obuna", "💳 Limit sotib olish",
        "ℹ️ Bot haqida", "👨‍💻 Adminga murojaat", "⚙️ Admin panel"
    ]:
        await state.clear()
        if message.text.startswith("/start"):
            await cmd_start(message, state)
        elif message.text == "📊 Yangi slayd tayyorlash":
            await start_new_slide(message, state)
        elif message.text == "📄 PPTX ni PDF ga aylantirish":
            await prompt_pptx_to_pdf(message, state)
        elif message.text == "🖼 Rasmni PDF ga aylantirish":
            await prompt_image_to_pdf(message, state)
        elif message.text == "👤 Mening profilim":
            await show_profile(message)
        elif message.text == "🎁 Bepul limit olish":
            await show_referral_program(message)
        elif message.text in ("💳 Limit va Obuna", "💳 Limit sotib olish"):
            await buy_limits(message)
        elif message.text == "ℹ️ Bot haqida":
            await about_bot(message)
        elif message.text == "⚙️ Admin panel" and config.is_admin(message.from_user.id):
            await admin_panel(message)
        elif message.text in ("👨‍💻 Adminga murojaat", "Adminga murojaat"):
            await contact_admin_menu(message, state)
        return

    await state.clear()
    user_id = message.from_user.id
    user_name = message.from_user.full_name or "Foydalanuvchi"
    username = f"@{message.from_user.username}" if message.from_user.username else "Username yo'q"
    user_text = message.text

    await message.answer(
        "✅ <b>Xabaringiz adminga yetkazildi!</b> Tez orada sizga javob beramiz.",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(user_id)),
        parse_mode="HTML"
    )

    safe_name = html.escape(user_name)
    safe_username = html.escape(username)
    safe_text = html.escape(user_text)

    admin_msg = (
        f"📩 <b>YANGI MUROJAAT (Adminga xabar):</b>\n\n"
        f"👤 <b>Yuboruvchi:</b> {safe_name} ({safe_username})\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n\n"
        f"💬 <b>Xabar matni:</b>\n{safe_text}\n\n"
        f"Javob berish uchun: <code>/reply {user_id} Javob matni</code>"
    )

    admin_targets = set([config.ADMIN_ID] + config.UNLIMITED_USERS)
    for adm_id in admin_targets:
        try:
            await message.bot.send_message(chat_id=adm_id, text=admin_msg, parse_mode="HTML")
        except Exception as e:
            logger.error(f"HTML forward failed for admin {adm_id}: {e}")
            try:
                plain_msg = f"📩 YANGI MUROJAAT:\n\n👤 {user_name} ({username})\n🆔 ID: {user_id}\n\n💬 Xabar:\n{user_text}\n\nJavob: /reply {user_id} matn"
                await message.bot.send_message(chat_id=adm_id, text=plain_msg)
            except Exception as e2:
                logger.error(f"Plain forward failed for admin {adm_id}: {e2}")

@router.message(F.text == "ℹ️ Bot haqida")
async def about_bot(message: Message):
    text = (
        f"ℹ️ **Talabalar uchun Slayd & PDF Generator Bot haqida:**\n\n"
        f"🎓 **OTM talablari boʻyicha taqdimotlar:**\n"
        f"• Titul varaqasi (Universitet, fakultet, talaba va oʻqituvchi maʼlumotlari)\n"
        f"• Taqdimot rejasi (Mundarija) va mazmuniy slaydlar\n"
        f"• Xulosa va **Foydalanilgan adabiyotlar (manbalar)**\n"
        f"• **Himoya nutq matni (doklad / shpargalka)** — darsda nima deb gapirishni toʻliq koʻrsatadi!\n\n"
        f"🔹 **Formatlar:** Tahrirlash mumkin boʻlgan zamonaviy **PowerPoint (.pptx)**.\n"
        f"🔹 **Alohida PDF qilish:** Xohlagan vaqtda bir tugma bilan PDF olish yoki istalgan .pptx faylni botga tashlab PDF ga aylantirish mumkin.\n"
        f"🔹 **Rasmni PDF ga aylantirish:** Istalgan rasm(lar)ni bir zumda PDF qilib beradi.\n"
        f"🔹 **Tariflar:** 2 ta bepul taqdimot, so'ngra 1 ta taqdimot — 5 000 so'm, oylik cheksiz — 20 000 so'm.\n"
        f"🔹 **Referal:** Har 2 ta do'st taklif qilsangiz, +1 ta bepul limit beriladi!\n\n"
        f"Savol va takliflar uchun adminga murojaat qiling."
    )
    await message.answer(text, parse_mode="Markdown")


# ================= RASMNI PDF GA AYLANTIRISH =================
MEDIA_GROUP_CACHE = {}

async def _process_media_group(group_id: str, bot):
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
    except Exception as e:
        logger.error(f"Album PDF error: {e}")
        await status_msg.edit_text(f"❌ Xatolik yuz berdi: {e}")
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)

# ================= PPTX NI PDF GA AYLANTIRISH =================
@router.message(F.text == "📄 PPTX ni PDF ga aylantirish")
async def prompt_pptx_to_pdf(message: Message, state: FSMContext):
    await state.set_state(PptxToPdfState.waiting_for_pptx)
    await message.answer(
        "📄 **PowerPoint (.pptx yoki .ppt) taqdimotingizni yuboring:**\n\n"
        "Bot uni bir necha soniyada sifatli **PDF** hujjatga aylantirib beradi! ⚡️\n\n"
        "*(Istalgan vaqtda botga to'g'ridan-to'g'ri taqdimot faylini tashlasangiz ham, avtomatik PDF qilib beradi)*",
        reply_markup=keyboards.get_cancel_pptx_to_pdf_keyboard(),
        parse_mode="Markdown"
    )

@router.callback_query(F.data == "cancel_pptx_to_pdf")
async def cancel_pptx_to_pdf_callback(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer("Bekor qilindi")
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id))
    )

@router.message(F.text == "🖼 Rasmni PDF ga aylantirish")
async def prompt_image_to_pdf(message: Message, state: FSMContext):
    await state.set_state(ImageToPdfState.waiting_for_image)
    await message.answer(
        "📷 **Rasmni PDF ga aylantirish:**\n\n"
        "Menga bir yoki bir nechta rasm yuboring (alohida yoki birgalikda albom qilib).\n"
        "Men ularni bir zumda yuqori sifatli **PDF** hujjatga aylantirib beraman! 🚀",
        reply_markup=keyboards.get_cancel_image_to_pdf_keyboard(),
        parse_mode="Markdown"
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
                "task": asyncio.create_task(_process_media_group(group_id, message.bot))
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

    if not is_image:
        return

    # Image document is only converted to PDF if user is in ImageToPdfState
    if cur_state != ImageToPdfState.waiting_for_image:
        return

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


@router.message(F.text == "📊 Yangi slayd tayyorlash")
async def start_new_slide(message: Message, state: FSMContext):
    # Check limit first
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or ""
    )
    
    is_sub = database.is_subscription_active(user)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id) or is_sub
    total_remaining = user["free_limit"] + user["paid_balance"]

    if not is_unlimited and total_remaining <= 0:
        bot_user = await message.bot.get_me()
        await message.answer(
            "⚠️ **Kechirasiz, sizda limitlar tugagan!**\n\n"
            "Siz yangi taqdimot yaratish uchun:\n"
            "1️⃣ **Limit yoki Oylik obuna xarid qilishingiz mumkin** (1 ta taqdimot — 5 000 so'm, oylik cheksiz — 20 000 so'm);\n"
            "2️⃣ **Do'stlaringizni taklif qiling** — har 2 ta yangi do'st uchun **+1 ta bepul limit** oling!",
            reply_markup=keyboards.get_no_limit_keyboard(bot_user.username, message.from_user.id),
            parse_mode="Markdown"
        )
        return

    await state.set_state(SlideCreation.waiting_for_topic)
    await message.answer(
        "✍️ **Taqdimot mavzusini yozib yuboring:**\n\n"
        "Masalan: *Sun'iy intellektning tibbiyotdagi o'rni va kelajagi*",
        parse_mode="Markdown"
    )

@router.message(SlideCreation.waiting_for_topic)
async def process_topic(message: Message, state: FSMContext):
    topic = message.text.strip()
    if len(topic) < 3:
        await message.answer("Iltimos, mavzuni to'liqroq yozing:")
        return

    await state.update_data(topic=topic)
    await state.set_state(SlideCreation.waiting_for_count)
    safe_topic = html.escape(topic)
    await message.answer(
        f"Mavzu: <b>{safe_topic}</b>\n\n"
        f"Nechta slayd bo'lsin? Tanlang:",
        reply_markup=keyboards.get_slide_counts_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data.startswith("count_"), SlideCreation.waiting_for_count)
async def process_slide_count(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    count_str = callback.data.split("_")[1]
    slide_count = int(count_str)
    
    await state.update_data(slide_count=slide_count)
    await state.set_state(SlideCreation.waiting_for_author)

    await callback.message.answer(
        "🎓 **1-slayd: Titul varaqasi uchun ma'lumotlar**\n"
        "*(OTM, fakultet, yoʻnalish, guruh, talaba va ilmiy rahbar)*\n\n"
        "Maʼlumotlarni tagma-tag yoki bir qatorda yozib yuborishingiz mumkin (hammasi 1-slaydda chiroyli chiqadi):\n"
        "💡 *Masalan:*\n"
        "OTM: TATU\n"
        "Fakultet: Dasturiy injiniring\n"
        "Yo'nalish: DI\n"
        "Guruh: 210-21\n"
        "Talaba: Nazarbek Turdaliyev\n"
        "O'qituvchi: Eshpolatov Ozodbek\n\n"
        "⏩ Agar maʼlumot kiritishni xohlamasangiz, **«O'tkazib yuborish»** tugmasini bosing:\n"
        "*(Keyingi bosqichda slaydning orqa fonini tanlaysiz 🎨)*",
        reply_markup=keyboards.get_skip_author_keyboard(),
        parse_mode="Markdown"
    )


@router.message(SlideCreation.waiting_for_author, F.text)
async def process_author_info_message(message: Message, state: FSMContext):
    author_info = message.text.strip()
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
    await state.clear()
    
    await generate_and_send_presentation(
        chat_message=message,
        user_id=message.from_user.id,
        topic=topic,
        slide_count=slide_count,
        author_info=author_info,
        theme_choice="auto",
        custom_bg=tmp_path,
        context_document=context_doc
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
        await state.clear()
        
        await generate_and_send_presentation(
            chat_message=message,
            user_id=message.from_user.id,
            topic=topic,
            slide_count=slide_count,
            author_info=author_info,
            theme_choice="auto",
            custom_bg=tmp_path,
            context_document=context_doc
        )
    else:
        await message.answer(
            "⚠️ Iltimos, fon uchun **rasm (jpg, png)** yuboring yoki rang tanlashga qayting:",
            reply_markup=keyboards.get_custom_bg_keyboard(),
            parse_mode="Markdown"
        )

@router.message(SlideCreation.waiting_for_custom_bg, F.text)
async def invalid_custom_bg_text(message: Message):
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
    slide_count = data.get("slide_count", 8)
    author_info = data.get("author_info", "")
    context_doc = data.get("context_document", "")
    await state.clear()
    await generate_and_send_presentation(
        chat_message=callback.message,
        user_id=callback.from_user.id,
        topic=topic,
        slide_count=slide_count,
        author_info=author_info,
        theme_choice=theme_key,
        context_document=context_doc
    )

async def generate_and_send_presentation(chat_message: Message, user_id: int, topic: str, slide_count: int, author_info: str = "", theme_choice: str = "auto", custom_bg: str = None, context_document: str = ""):
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
        # Generate with Gemini
        content = await generator.generate_presentation_content(
            topic,
            slide_count=slide_count,
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

        user_full_name = chat_message.from_user.full_name if (chat_message and chat_message.from_user) else ""
        has_author = bool(author_info and author_info.strip())
        await asyncio.to_thread(
            generator.create_pptx_file,
            content,
            pptx_path,
            theme_name=chosen_theme,
            images_map=images_map,
            author_info=author_info,
            default_student_name=user_full_name if has_author else "",
            custom_bg=custom_bg
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
        slides_breakdown = "(1-Titul, 2-Mavzu, 3-Reja, Asosiy qismlar, Xulosa, Foydalanilgan adabiyotlar, Yakun)" if has_author else "(1-Mavzu, 2-Reja, Asosiy qismlar, Xulosa, Foydalanilgan adabiyotlar, Yakun)"

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
    await callback.message.answer(
        "Asosiy menyu:",
        reply_markup=keyboards.get_main_menu(is_admin=config.is_admin(callback.from_user.id))
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

@router.message(F.text == "⚙️ Admin panel")
@router.message(Command("stats"))
async def admin_panel(message: Message):
    if not config.is_admin(message.from_user.id):
        return

    stats = await database.get_stats()
    text = (
        f"⚙️ **Admin paneli va Statistika:**\n\n"
        f"👥 Jami foydalanuvchilar: **{stats['total_users']} nafar**\n"
        f"🤝 Jami taklif qilingan do'stlar: **{stats.get('total_referrals', 0)} ta**\n"
        f"📑 Jami yaratilgan taqdimotlar: **{stats['total_slides']} ta**\n\n"
        f"👑 VIP maqom berish: `/set_vip <id>`\n"
        f"🚫 VIP ni bekor qilish: `/remove_vip <id>`\n"
        f"➕ Limit qo'shish: `/add_limit <id> <soni>`\n"
        f"⭐️ Obuna yoqish: `/add_sub <id> [kun]`\n"
        f"💬 Javob qaytarish: `/reply <id> <matn>`"
    )
    await message.answer(text, parse_mode="Markdown")

@router.message(F.voice)
@router.message(F.audio)
async def handle_voice_presentation(message: Message, state: FSMContext):
    # Check limit first
    user = await database.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or "",
        full_name=message.from_user.full_name or ""
    )
    is_sub = database.is_subscription_active(user)
    is_unlimited = bool(user.get("is_unlimited")) or config.is_unlimited(message.from_user.id) or is_sub
    total_remaining = user["free_limit"] + user["paid_balance"]

    if not is_unlimited and total_remaining <= 0:
        bot_user = await message.bot.get_me()
        await message.answer(
            "⚠️ **Kechirasiz, sizda limitlar tugagan!**\n\n"
            "Siz yangi taqdimot yaratish uchun:\n"
            "1️⃣ **Limit yoki Oylik obuna xarid qilishingiz mumkin** (1 ta taqdimot — 5 000 so'm, oylik cheksiz — 20 000 so'm);\n"
            "2️⃣ **Do'stlaringizni taklif qiling** — har 2 ta yangi do'st uchun **+1 ta bepul limit** oling!",
            reply_markup=keyboards.get_no_limit_keyboard(bot_user.username, message.from_user.id),
            parse_mode="Markdown"
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

        await state.update_data(
            topic=topic,
            slide_count=slide_count,
            author_info=author_info
        )
        await state.set_state(SlideCreation.waiting_for_theme)

        author_display = f"\n👤 **Muallif:** {author_info}" if author_info else ""
        await status_msg.delete()
        await message.answer(
            f"🎙 **Ovozli xabaringiz muvaffaqiyatli tushunildi!** 🚀\n\n"
            f"📌 **Aniqlangan mavzu:** *{topic}*\n"
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
    await state.set_state(MediaChoiceState.waiting_for_action)
    await state.update_data(
        media_file_id=photo.file_id,
        media_type="photo",
        media_file_name="photo.jpg"
    )
    await message.reply(
        "📷 **Rasm (Kitob beti yoki konspekt) qabul qilindi!**\n\n"
        "Ushbu rasm bilan nima qilmoqchisiz?\n\n"
        "1️⃣ **Taqdimot tayyorlash:** Rasm ichidagi mavzu va maʼlumotlar asosida toʻliq slayd yaratish;\n"
        "2️⃣ **PDF ga aylantirish:** Rasmni sifatli PDF hujjatga oʻgirish.",
        reply_markup=keyboards.get_media_choice_keyboard(is_doc=False),
        parse_mode="Markdown"
    )

@router.message(F.document)
async def handle_document_media(message: Message, state: FSMContext):
    doc = message.document
    fname = (doc.file_name or "document").lower()
    
    if (doc.mime_type or "").startswith("image/") or any(fname.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        await state.set_state(MediaChoiceState.waiting_for_action)
        await state.update_data(
            media_file_id=doc.file_id,
            media_type="photo",
            media_file_name=doc.file_name or "image.jpg"
        )
        await message.reply(
            "🖼 **Rasm hujjati qabul qilindi!**\n\n"
            "Ushbu rasm bilan nima qilmoqchisiz?",
            reply_markup=keyboards.get_media_choice_keyboard(is_doc=False),
            parse_mode="Markdown"
        )
        return

    await state.set_state(MediaChoiceState.waiting_for_action)
    await state.update_data(
        media_file_id=doc.file_id,
        media_type="document",
        media_file_name=doc.file_name or "hujjat"
    )
    
    await message.reply(
        f"📄 **'{doc.file_name or 'Hujjat'}' qabul qilindi!**\n\n"
        "Ushbu fayl bilan nima qilmoqchisiz?\n\n"
        "1️⃣ **Taqdimot yasash:** Hujjatdagi asosiy mazmun boʻyicha toʻliq taqdimot yaratish;\n"
        "2️⃣ **PDF ga aylantirish:** (.pptx boʻlsa sifatli PDF ga oʻgirish).",
        reply_markup=keyboards.get_media_choice_keyboard(is_doc=True),
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

        await state.update_data(
            topic=topic,
            slide_count=suggested_slides,
            author_info="",
            context_document=summary
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

