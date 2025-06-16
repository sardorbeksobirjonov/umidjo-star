import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.client.default import DefaultBotProperties

# === MA'LUMOTLARINGIZ ===
API_TOKEN = '7758544011:AAGqUJ4C0u9qEB0MG7nUoFqqsglfrgLvX8Y'
CHANNEL_ID = -1002338934845
ADMIN_ID = 7450742944
CHANNEL_URL = "https://t.me/umidjon_pmn"
USERS_FILE = "users.txt"

# === Yozuvlar va sozlamalar ===
logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# === Foydalanuvchini ro'yxatga olish ===
async def register_user(user_id: int):
    if not os.path.exists(USERS_FILE):
        open(USERS_FILE, "w", encoding="utf-8").close()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        if str(user_id) not in f.read():
            with open(USERS_FILE, "a", encoding="utf-8") as fa:
                fa.write(str(user_id) + "\n")

# === Tugmalar ===
def user_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Kanalga obuna bo‘lish", url=CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="verify")]
    ])

def admin_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="👥 Foydalanuvchilar ro‘yxati", callback_data="show_users")]
    ])

# === /start komandasi ===
@dp.message(F.text == "/start")
async def cmd_start(message: Message):
    uid = message.from_user.id
    if uid == ADMIN_ID:
        await message.answer("👨‍💻 Admin panel: Vazifa yuboring yoki foydalanuvchilar ro‘yxatini ko‘ring.", reply_markup=admin_keyboard())
    else:
        await message.answer("👋 Assalomu alaykum! Botdan foydalanish uchun kanalga obuna bo‘ling:", reply_markup=user_keyboard())

# === Obunani tekshirish ===
@dp.callback_query(F.data == "verify")
async def verify_callback(callback: CallbackQuery):
    uid = callback.from_user.id
    try:
        member = await bot.get_chat_member(CHANNEL_ID, uid)
        if member.status in ["member", "administrator", "creator"]:
            await register_user(uid)
            await callback.message.edit_text("✅ Obuna bo‘ldingiz! Endi botdan to‘liq foydalanishingiz mumkin.")
        else:
            await callback.message.edit_text("❌ Hali obuna bo‘lmagansiz. Iltimos, obuna bo‘ling.")
    except Exception as e:
        logging.error(f"Obuna tekshiruvida xatolik: {e}")
        await callback.message.edit_text("❌ Xatolik yuz berdi. Bot admini bilan bog‘laning.")

# === Foydalanuvchilar ro‘yxatini ko‘rsatish (faqat admin) ===
@dp.callback_query(F.data == "show_users")
async def show_users(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        return await callback.answer("🚫 Sizda ruxsat yo‘q!")
    if not os.path.exists(USERS_FILE):
        return await callback.message.answer("📂 Hozircha hech kim ro‘yxatda yo‘q.")
    users = open(USERS_FILE, "r", encoding="utf-8").read().splitlines()
    if not users:
        await callback.message.answer("📂 Ro‘yxat bo‘sh.")
    else:
        user_list = "\n".join(users)
        await callback.message.answer(f"👥 Foydalanuvchilar ID ro‘yxati:\n{user_list}")

# === Barcha foydalanuvchilarga xabar yuborish (faqat admin) ===
@dp.message()
async def broadcast_or_register(message: Message):
    uid = message.from_user.id
    if uid == ADMIN_ID:
        text = message.text.strip()
        if not text:
            return await message.answer("❗️ Yuboriladigan vazifa matni bo‘sh.")
        if not os.path.exists(USERS_FILE):
            return await message.answer("❗️ Foydalanuvchilar topilmadi.")
        count = 0
        for line in open(USERS_FILE, "r", encoding="utf-8"):
            user_id = line.strip()
            if user_id and int(user_id) != ADMIN_ID:
                try:
                    await bot.send_message(int(user_id), f"🆕 <b>Yangi vazifa:</b>\n{text}")
                    count += 1
                except:
                    continue
        await message.answer(f"✅ Vazifa {count} foydalanuvchiga yuborildi.")
    else:
        pass  # oddiy foydalanuvchi uchun hech narsa qilinmaydi

# === Botni ishga tushurish ===
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
