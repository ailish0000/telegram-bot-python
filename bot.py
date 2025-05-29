import os
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

try:
    import ssl
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
    print("⚠️ Библиотека SSL недоступна. Бот не сможет установить HTTPS-соединения.")

if SSL_AVAILABLE:
    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))

    storage = MemoryStorage()
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    WELCOME_IMAGE = "https://github.com/user-attachments/assets/474d0575-01ed-45cc-8253-5e35bccda672"
    MENU_IMAGE = "https://github.com/user-attachments/assets/832593ee-2617-4ef6-9656-ff4d4f9506b8"

    user_started = set()
    user_modes = {}
    admin_reply_sessions = {}
    broadcast_sessions = {}

    def main_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Регистрация 💚", url="https://aur-ora.com/auth/registration/666282189484"),
            InlineKeyboardButton("Подборка продуктов", callback_data="select_product"),
            InlineKeyboardButton("Каталог всех продуктов", callback_data="catalog"),
            InlineKeyboardButton("Адреса магазинов", callback_data="check_city"),
            InlineKeyboardButton("Задать вопрос", callback_data="ask_question"),
            InlineKeyboardButton("Сообщить об ошибке ❌", callback_data="report_error")
        )
        return markup

    def product_menu():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("От простуды", callback_data="prostuda"),
            InlineKeyboardButton("Волосы/ногти", callback_data="hair"),
            InlineKeyboardButton("Для суставов", callback_data="joints"),
            InlineKeyboardButton("Для печени", callback_data="liver"),
            InlineKeyboardButton("Витамины", callback_data="vitamins"),
            InlineKeyboardButton("Антипаразитарка", callback_data="antiparazit"),
            InlineKeyboardButton("Сорбенты", callback_data="sorbent"),
            InlineKeyboardButton("Мои фавориты", callback_data="top"),
            InlineKeyboardButton("Детокс", callback_data="detox"),
            InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        )
        return markup

    def city_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Минск", callback_data="Minsk"),
            InlineKeyboardButton("Минская область", callback_data="Minsk_region"),
            InlineKeyboardButton("Гомель", callback_data="Gomel"),
            InlineKeyboardButton("Гомельская область", callback_data="Gomel_region"),
            InlineKeyboardButton("Брест", callback_data="Brest"),
            InlineKeyboardButton("Брестская область", callback_data="Brest_region"),
            InlineKeyboardButton("Витебск", callback_data="Vitebsk"),
            InlineKeyboardButton("Витебская область", callback_data="Vitebsk_region"),
            InlineKeyboardButton("Могилев", callback_data="Mogilev"),
            InlineKeyboardButton("Могилевская область", callback_data="Mogilev_region"),
            InlineKeyboardButton("Нет моего города", callback_data="none_city"),
            InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        )
        return markup

    async def delete_message_safe(chat_id, message_id):
        try:
            await bot.delete_message(chat_id, message_id)
        except:
            pass

    @dp.message_handler(commands=["start"])
    async def send_start(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_started:
            user_started.add(user_id)
            await bot.send_photo(
                chat_id=user_id,
                photo=WELCOME_IMAGE,
                caption="Привет! Меня зовут Наталья Кумасинская..."
            )
            await asyncio.sleep(6)
        await delete_message_safe(user_id, message.message_id)
        await bot.send_photo(
            chat_id=user_id,
            photo=MENU_IMAGE,
            caption="Выбери, что тебе подходит 👇",
            reply_markup=main_menu()
        )

    @dp.message_handler(commands=["menu"])
    async def send_menu(message: types.Message):
        await delete_message_safe(message.chat.id, message.message_id)
        await bot.send_photo(message.chat.id, MENU_IMAGE, caption="Выбери, что тебе подходит 👇", reply_markup=main_menu())

    @dp.message_handler(commands=["registration"])
    async def send_registration_link(message: types.Message):
        await delete_message_safe(message.chat.id, message.message_id)
        await message.answer("Ссылка для регистрации: https://aur-ora.com/auth/registration/666282189484")

    @dp.message_handler(commands=["catalog"])
    async def send_catalog_link(message: types.Message):
        await delete_message_safe(message.chat.id, message.message_id)
        await message.answer("Ссылка на каталог: https://aur-ora.com/catalog/vse_produkty")

    # --- Admin Panel ---
    @dp.message_handler(commands=["stats"])
    async def stats(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return await message.reply("⛔️ Доступ запрещён.")
        await message.reply(f"📊 Количество пользователей: {len(user_started)}")

    @dp.message_handler(commands=["broadcast"])
    async def start_broadcast(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return await message.reply("⛔️ Доступ запрещён.")
        broadcast_sessions[ADMIN_ID] = True
        await message.reply("✉️ Введите текст сообщения для рассылки или /cancel для отмены.")

    @dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and m.text == "/cancel")
    async def cancel_broadcast(message: types.Message):
        if broadcast_sessions.pop(ADMIN_ID, None):
            await message.reply("✅ Рассылка отменена.")
        else:
            await message.reply("Нет активной рассылки.")

    @dp.message_handler(lambda m: m.from_user.id == ADMIN_ID and ADMIN_ID in broadcast_sessions)
    async def process_broadcast(message: types.Message):
        text = message.text
        broadcast_sessions.pop(ADMIN_ID, None)
        success = 0
        fail = 0
        for uid in user_started:
            try:
                await bot.send_message(uid, text)
                success += 1
            except:
                fail += 1
        await message.reply(f"✅ Отправлено: {success}\n❌ Не доставлено: {fail}")

    # --- Остальная логика обработки кнопок и сообщений будет добавлена здесь ---

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)

else:
    print("Бот не запущен, т.к. нет SSL.")
