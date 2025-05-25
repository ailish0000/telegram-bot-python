# Импортируем нужные модули из aiogram
import os
import asyncio
import random
from dotenv import load_dotenv

try:
    import ssl
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
    print("⚠️ Библиотека SSL недоступна. Бот не сможет установить HTTPS-соединения.")

if SSL_AVAILABLE:
    from aiogram import Bot, Dispatcher, executor, types
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # Изображения
    WELCOME_IMAGE = "https://github.com/user-attachments/assets/474d0575-01ed-45cc-8253-5e35bccda672"
    MENU_IMAGE = "https://github.com/user-attachments/assets/832593ee-2617-4ef6-9656-ff4d4f9506b8"

    # Данные
    user_started = set()
    user_messages = []
    waiting_for_question = set()
    waiting_for_error = set()

    # Меню
    def main_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Регистрация 💚", url="https://aur-ora.com/auth/registration/666282189484"),
            InlineKeyboardButton("1⃣ Подборка продуктов", callback_data="select_product"),
            InlineKeyboardButton("2⃣ Задать вопрос", callback_data="ask_question"),
            InlineKeyboardButton("3⃣ Каталог всех продуктов", callback_data="catalog"),
            InlineKeyboardButton("4⃣ Адреса магазинов", callback_data="check_city"),
            InlineKeyboardButton("Сообщить об ошибке ❌", callback_data="report_error")
        )
        return markup

    def admin_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
            InlineKeyboardButton("💬 Обращения", callback_data="admin_messages"),
            InlineKeyboardButton("📢 Сделать рассылку", callback_data="admin_broadcast")
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
            InlineKeyboardButton("Личный топ", callback_data="top"),
            InlineKeyboardButton("◀️ Назад", callback_data="back_to_main")
        )
        return markup

    def city_menu():
        cities = [
            ("Минск", "Minsk"), ("Минская область", "Minsk_region"),
            ("Гомель", "Gomel"), ("Гомельская область", "Gomel_region"),
            ("Брест", "Brest"), ("Брестская область", "Brest_region"),
            ("Витебск", "Vitebsk"), ("Витебская область", "Vitebsk_region"),
            ("Могилев", "Mogilev"), ("Могилевская область", "Mogilev_region"),
            ("Нет моего города", "none_city")
        ]
        markup = InlineKeyboardMarkup(row_width=1)
        for name, data in cities:
            markup.add(InlineKeyboardButton(name, callback_data=data))
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data="back_to_main"))
        return markup

    async def delete_message_safe(chat_id, message_id):
        try:
            await bot.delete_message(chat_id, message_id)
        except:
            pass

    async def thanos_effect(chat_id):
        try:
            messages = await bot.get_chat_history(chat_id, limit=50)
            to_delete = random.sample(messages, k=len(messages)//2)
            for msg in to_delete:
                try:
                    await bot.delete_message(chat_id, msg.message_id)
                except:
                    continue
        except:
            pass

    @dp.message_handler(commands=["start", "menu"])
    async def send_start(message: types.Message):
        user_id = message.from_user.id
        user_started.add(user_id)
        await bot.send_photo(
            chat_id=user_id,
            photo=WELCOME_IMAGE,
            caption="Привет! Меня зовут Наталья Кумасинская. Я мама двоих сыновей и давно использую продукцию Авроры. Хочу поделиться опытом и помочь выбрать хорошие продукты этой фирмы"
        )
        await asyncio.sleep(6)
        await delete_message_safe(user_id, message.message_id)
        await thanos_effect(user_id)
        await bot.send_photo(
            chat_id=user_id,
            photo=MENU_IMAGE,
            caption="Выбери, что тебе подходит 👇",
            reply_markup=main_menu()
        )

    @dp.message_handler(commands=["registration"])
    async def send_registration(message: types.Message):
        await message.answer("Для регистрации перейдите по ссылке:", reply_markup=main_menu())

    @dp.message_handler(commands=["catalog"])
    async def send_catalog(message: types.Message):
        await message.answer("Каталог продукции доступен на сайте: https://aur-ora.com/catalog/")

    @dp.message_handler(commands=["admin"])
    async def show_admin_panel(message: types.Message):
        if message.from_user.id == ADMIN_ID:
            await message.answer("Админ-панель:", reply_markup=admin_menu())
        else:
            await message.answer("⛔ Доступ запрещён.")

    @dp.callback_query_handler(lambda c: c.data.startswith("admin_"))
    async def handle_admin_actions(callback_query: types.CallbackQuery):
        data = callback_query.data
        user_id = callback_query.from_user.id
        if user_id != ADMIN_ID:
            await callback_query.answer("⛔ Нет доступа", show_alert=True)
            return

        if data == "admin_stats":
            await bot.send_message(user_id, f"👥 Пользователей: {len(user_started)}\n📨 Обращений: {len(user_messages)}")
        elif data == "admin_messages":
            if user_messages:
                for msg in user_messages[-10:]:
                    await bot.send_message(user_id, msg)
            else:
                await bot.send_message(user_id, "Нет обращений.")
        elif data == "admin_broadcast":
            await bot.send_message(user_id, "Введите текст для рассылки:")
            dp.register_message_handler(broadcast_message, state=None)

        await bot.answer_callback_query(callback_query.id)

    async def broadcast_message(message: types.Message):
        if message.from_user.id != ADMIN_ID:
            return
        count = 0
        for uid in user_started:
            try:
                await bot.send_message(uid, f"📢 Сообщение от Натальи:\n\n{message.text}")
                count += 1
            except:
                continue
        await message.answer(f"✅ Рассылка отправлена {count} пользователям.")
        dp.unregister_message_handler(broadcast_message, state=None)

    @dp.callback_query_handler()
    async def handle_callbacks(callback_query: types.CallbackQuery):
        data = callback_query.data
        user_id = callback_query.from_user.id

        if data == "select_product":
            await bot.send_photo(chat_id=user_id, photo=MENU_IMAGE, caption="Выберите категорию продукта:", reply_markup=product_menu())
        elif data == "ask_question":
            waiting_for_question.add(user_id)
            await bot.send_message(user_id, "✉️ Напишите ваш вопрос в чат, и я обязательно на него отвечу.")
        elif data == "report_error":
            waiting_for_error.add(user_id)
            await bot.send_message(user_id, "⚠️ Расскажите подробнее об ошибке, чтобы я могла её исправить.")
        elif data == "catalog":
            await bot.send_message(user_id, "Каталог продукции доступен на сайте: https://aur-ora.com/catalog/")
        elif data == "check_city":
            await bot.send_photo(chat_id=user_id, photo=MENU_IMAGE, caption="Выберите город:", reply_markup=city_menu())
        elif data == "back_to_main":
            await bot.send_photo(chat_id=user_id, photo=MENU_IMAGE, caption="Выбери, что тебе подходит 👇", reply_markup=main_menu())

        from handlers.products import handle_product_carousels
        await handle_product_carousels(callback_query, bot, MENU_IMAGE, main_menu, product_menu)

        await bot.answer_callback_query(callback_query.id)

    @dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
    async def forward_user_message(message: types.Message):
        user_id = message.from_user.id
        if user_id in waiting_for_question:
            user_messages.append(f"❓ Вопрос от @{message.from_user.username or 'без username'} (ID: {user_id}):\n{message.text}")
            waiting_for_question.remove(user_id)
            await message.reply("✅ Ваш вопрос отправлен. Я постараюсь ответить как можно скорее.")
        elif user_id in waiting_for_error:
            user_messages.append(f"🐞 Ошибка от @{message.from_user.username or 'без username'} (ID: {user_id}):\n{message.text}")
            waiting_for_error.remove(user_id)
            await message.reply("✅ Спасибо! Я постараюсь исправить ошибку в ближайшее время.")
        else:
            user_messages.append(f"📩 Сообщение от @{message.from_user.username or 'без username'} (ID: {user_id}):\n{message.text}")
            await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")
        await bot.send_message(ADMIN_ID, user_messages[-1])

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)
else:
    print("❌ Бот не может быть запущен без поддержки SSL. Пожалуйста, используйте среду с поддержкой HTTPS.")
