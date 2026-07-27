import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
)

import db

logging.basicConfig(level=logging.INFO)

# ---------- SOZLAMALAR ----------
BOT_TOKEN = os.getenv("BOT_TOKEN", "SIZNING_BOT_TOKEN_BU_YERGA")
# Birinchi (bosh) admin - botni ishga tushirgan odam. Bu ID doim admin bo'lib qoladi.
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

bot = Bot(8948791881:AAHWiUQWqmNBuUrhV5Cc8HUd73ro7YR7sXw)
dp = Dispatcher(storage=MemoryStorage())


# ---------- HOLATLAR (FSM) ----------
class Broadcast(StatesGroup):
    waiting_text = State()


class AdminManage(StatesGroup):
    waiting_new_admin_id = State()
    waiting_remove_admin_id = State()


# ---------- KLAVIATURALAR ----------
def main_menu_kb() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="📋 Guruhlar ro'yxati"), KeyboardButton(text="🧑‍💼 Adminlar")],
        [KeyboardButton(text="➕ Admin qo'shish"), KeyboardButton(text="➖ Admin o'chirish")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, yubor", callback_data="confirm_send"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel_send"),
            ]
        ]
    )


# ---------- YORDAMCHI ----------
async def check_admin(message: Message) -> bool:
    if message.from_user.id == OWNER_ID or await db.is_admin(message.from_user.id):
        return True
    await message.answer("⛔ Sizda bu botdan foydalanish huquqi yo'q.")
    return False


# ---------- START ----------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    if message.chat.type != "private":
        return  # guruhda /start ga javob bermaydi

    if message.from_user.id == OWNER_ID:
        await db.add_admin(OWNER_ID, message.from_user.full_name)

    if not await check_admin(message):
        return

    await message.answer(
        "Salom! 👋\nMen guruhlaringizga xabar tarqatish botiman.\n\n"
        "Meni kerakli guruhlarga (oddiy a'zo sifatida, admin qilish shart emas) qo'shing — "
        "men avtomatik ravishda o'sha guruhni ro'yxatimga qo'shib olaman.\n\n"
        "Pastdagi tugmalardan foydalaning:",
        reply_markup=main_menu_kb(),
    )


# ---------- BOT GURUHGA QO'SHILGANDA / CHIQARILGANDA ----------
@dp.message(F.new_chat_members)
async def on_bot_added(message: Message):
    for member in message.new_chat_members:
        if member.id == bot.id:
            await db.add_group(message.chat.id, message.chat.title or "Noma'lum guruh")
            for admin_id, _ in await db.get_all_admins():
                try:
                    await bot.send_message(
                        admin_id,
                        f"✅ Yangi guruhga qo'shildim: {message.chat.title}",
                    )
                except Exception:
                    pass


@dp.message(F.left_chat_member)
async def on_bot_removed(message: Message):
    if message.left_chat_member.id == bot.id:
        await db.remove_group(message.chat.id)


# ---------- GURUHLAR RO'YXATI ----------
@dp.message(F.text == "📋 Guruhlar ro'yxati")
async def list_groups(message: Message):
    if not await check_admin(message):
        return
    groups = await db.get_all_groups()
    if not groups:
        await message.answer("Hozircha hech qanday guruh yo'q. Botni biror guruhga qo'shing.")
        return
    text = "📋 Ro'yxatdagi guruhlar:\n\n" + "\n".join(
        f"• {title} (`{chat_id}`)" for chat_id, title in groups
    )
    await message.answer(text, parse_mode="Markdown")


# ---------- ADMINLAR RO'YXATI ----------
@dp.message(F.text == "🧑‍💼 Adminlar")
async def list_admins(message: Message):
    if not await check_admin(message):
        return
    admins = await db.get_all_admins()
    text = "🧑‍💼 Adminlar ro'yxati:\n\n" + "\n".join(
        f"• {name or 'Nomsiz'} (`{uid}`)" for uid, name in admins
    )
    await message.answer(text, parse_mode="Markdown")


# ---------- YANGI ADMIN QO'SHISH ----------
@dp.message(F.text == "➕ Admin qo'shish")
async def ask_new_admin(message: Message, state: FSMContext):
    if not await check_admin(message):
        return
    await message.answer(
        "Yangi adminning Telegram ID raqamini yuboring.\n\n"
        "ID ni bilmasa, do'stingiz @userinfobot ga /start bosib ID sini bilib olishi mumkin."
    )
    await state.set_state(AdminManage.waiting_new_admin_id)


@dp.message(AdminManage.waiting_new_admin_id)
async def save_new_admin(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Iltimos, faqat raqamdan iborat ID yuboring.")
        return
    new_id = int(message.text.strip())
    await db.add_admin(new_id)
    await state.clear()
    await message.answer(f"✅ Admin qo'shildi: `{new_id}`", parse_mode="Markdown", reply_markup=main_menu_kb())
    try:
        await bot.send_message(new_id, "🎉 Siz endi ushbu botda admin etib tayinlandingiz!")
    except Exception:
        pass


# ---------- ADMIN O'CHIRISH ----------
@dp.message(F.text == "➖ Admin o'chirish")
async def ask_remove_admin(message: Message, state: FSMContext):
    if not await check_admin(message):
        return
    await message.answer("O'chirmoqchi bo'lgan adminning Telegram ID raqamini yuboring.")
    await state.set_state(AdminManage.waiting_remove_admin_id)


@dp.message(AdminManage.waiting_remove_admin_id)
async def save_remove_admin(message: Message, state: FSMContext):
    if not message.text or not message.text.strip().isdigit():
        await message.answer("❌ Iltimos, faqat raqamdan iborat ID yuboring.")
        return
    rem_id = int(message.text.strip())
    if rem_id == OWNER_ID:
        await message.answer("⛔ Bosh adminni o'chirib bo'lmaydi.")
        await state.clear()
        return
    await db.remove_admin(rem_id)
    await state.clear()
    await message.answer(f"✅ Admin o'chirildi: `{rem_id}`", parse_mode="Markdown", reply_markup=main_menu_kb())


# ---------- XABAR YUBORISH (BROADCAST) ----------
@dp.message(F.text == "📢 Xabar yuborish")
async def ask_broadcast_text(message: Message, state: FSMContext):
    if not await check_admin(message):
        return
    await message.answer(
        "Guruhlarga yubormoqchi bo'lgan matnni yuboring.\n"
        "(Bold, italic, link kabi formatlashdan foydalanishingiz mumkin)"
    )
    await state.set_state(Broadcast.waiting_text)


@dp.message(Broadcast.waiting_text)
async def preview_broadcast(message: Message, state: FSMContext):
    await state.update_data(text=message.html_text)
    groups = await db.get_all_groups()
    await message.answer(
        f"Quyidagi xabar {len(groups)} ta guruhga yuboriladi:\n\n{message.html_text}",
        parse_mode="HTML",
        reply_markup=confirm_kb(),
    )


@dp.callback_query(F.data == "cancel_send")
async def cancel_broadcast(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("❌ Bekor qilindi.")
    await call.message.answer("Bosh menyu:", reply_markup=main_menu_kb())


@dp.callback_query(F.data == "confirm_send")
async def confirm_broadcast(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    text = data.get("text")
    await state.clear()
    await call.message.edit_text("⏳ Yuborilmoqda...")

    groups = await db.get_all_groups()
    success, failed = 0, 0
    for chat_id, title in groups:
        try:
            await bot.send_message(chat_id, text, parse_mode="HTML")
            success += 1
        except Exception as e:
            failed += 1
            logging.warning(f"Xabar yuborilmadi ({title} - {chat_id}): {e}")
        await asyncio.sleep(0.05)  # Telegram rate limit uchun kichik kechikish

    await call.message.answer(
        f"✅ Yuborish yakunlandi.\nMuvaffaqiyatli: {success}\nXato: {failed}",
        reply_markup=main_menu_kb(),
    )


# ---------- ISHGA TUSHIRISH ----------
async def main():
    await db.init_db()
    if OWNER_ID:
        await db.add_admin(OWNER_ID, "Bosh admin")
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
