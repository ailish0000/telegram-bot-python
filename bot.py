# Импортируем нужные модули из aiogram
import os
import asyncio
from dotenv import load_dotenv  # Для загрузки переменных из .env

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

    WELCOME_IMAGE = "https://github.com/user-attachments/assets/474d0575-01ed-45cc-8253-5e35bccda672"
    MENU_IMAGE = "https://github.com/user-attachments/assets/832593ee-2617-4ef6-9656-ff4d4f9506b8"

    user_started = set()

    def main_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Регистрация 💚", url="https://aur-ora.com/auth/registration/666282189484"),
            InlineKeyboardButton("1️⃣ Подборка продуктов", callback_data="select_product"),
            InlineKeyboardButton("2️⃣ Задать вопрос", callback_data="ask_question"),
            InlineKeyboardButton("3️⃣ Каталог всех продуктов", callback_data="catalog"),
            InlineKeyboardButton("4️⃣ Адреса магазинов", callback_data="check_city"),
            InlineKeyboardButton("Сообщить об ошибке ❌", callback_data="report_error")
        )
        return markup

    def product_menu():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("От простуды", callback_data="prostuda_1"),
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

    # Приветствие
    @dp.message_handler(commands=["start"])
    async def send_start(message: types.Message):
        user_id = message.from_user.id
        if user_id not in user_started:
            user_started.add(user_id)
            await bot.send_photo(
                chat_id=user_id,
                photo=WELCOME_IMAGE,
                caption="Привет! Меня зовут Наталья Кумасинская. Я мама двоих сыновей и давно использую продукцию Авроры. Хочу поделиться опытом и помочь выбрать хорошие продукты этой фирмы"
            )
            await asyncio.sleep(6)
        await delete_message_safe(user_id, message.message_id)
        await bot.send_photo(
            chat_id=user_id,
            photo=MENU_IMAGE,
            caption="Выбери, что тебе подходит 👇",
            reply_markup=main_menu()
        )

    # Меню с эффектом Таноса
    @dp.message_handler(commands=["menu"])
    async def send_menu(message: types.Message):
        user_id = message.from_user.id
        await delete_message_safe(user_id, message.message_id)
        await bot.send_photo(
            chat_id=user_id,
            photo=MENU_IMAGE,
            caption="Выбери, что тебе подходит 👇",
            reply_markup=main_menu()
        )

    @dp.message_handler(commands=["registration"])
    async def send_registration_link(message: types.Message):
        user_id = message.from_user.id
        await delete_message_safe(user_id, message.message_id)
        await message.answer("Ссылка для регистрации: https://aur-ora.com/auth/registration/666282189484")

    @dp.message_handler(commands=["catalog"])
    async def send_catalog_link(message: types.Message):
        user_id = message.from_user.id
        await delete_message_safe(user_id, message.message_id)
        await message.answer("Ссылка на каталог: https://aur-ora.com/catalog/vse_produkty")

    @dp.callback_query_handler(lambda c: True)
    async def handle_callback(callback_query: types.CallbackQuery):
        data = callback_query.data
        user_id = callback_query.from_user.id
        message_id = callback_query.message.message_id

        await delete_message_safe(user_id, message_id)

        if data == "select_product":
            await bot.send_photo(
                chat_id=user_id,
                photo=MENU_IMAGE,
                caption="Выберите категорию продукта:",
                reply_markup=product_menu()
            )

        elif data == "ask_question":
            await bot.send_message(user_id, "✉️ Напишите ваш вопрос в чат, и я обязательно на него отвечу.")

        elif data == "check_city":
            await bot.send_photo(
                chat_id=user_id,
                photo=MENU_IMAGE,
                caption="Выберите город:",
                reply_markup=city_menu()
            )

        elif data == "back_to_main":
            await bot.send_photo(
                chat_id=user_id,
                photo=MENU_IMAGE,
                caption="Выбери, что тебе подходит 👇",
                reply_markup=main_menu()
            )

        elif data == "Minsk":
            await bot.send_message(user_id, "📍 Минск: пр-т Независимости, 123. Тел: +375 29 000 0000")
        elif data == "Gomel":
            await bot.send_message(user_id, "📍 Гомель: ул. Советская, 45. Тел: +375 29 111 1111")
        elif data == "Brest":
            await bot.send_message(user_id, "📍 Брест: ул. Ленина, 10. Тел: +375 29 222 2222")
        elif data == "Vitebsk":
            await bot.send_message(user_id, "📍 Витебск: ул. Чкалова, 15. Тел: +375 29 333 3333")
        elif data == "Mogilev":
            await bot.send_message(user_id, "📍 Могилев: пр-т Мира, 7. Тел: +375 29 444 4444")

        elif data == "report_error":
            await bot.send_message(user_id, "⚠️ Расскажите подробнее об ошибке, чтобы я могла её исправить.")

        # Обработка продуктов "От простуды" с листанием
        elif data.startswith("prostuda"):
            # определяем номер продукта
            parts = data.split("_")
            step = parts[1] if len(parts) > 1 else "1"

            if step == "1":
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/543/"),
                    InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_2"),
                    InlineKeyboardButton("◀️ Назад", callback_data="select_product")
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://github.com/user-attachments/assets/ac7b0dcc-2786-4c3e-b2bb-49e2d5c5af64",
                    caption="1️⃣ Антиоксидант из сока облепихи. Используется вместе с соком свеклы и серебром",
                    reply_markup=markup
                )

            elif step == "2":
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/641/"),
                    InlineKeyboardButton("◀️ Назад", callback_data="prostuda_1"),
                    InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_3")  # Если будет 3-й продукт, можно потом поправить
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://github.com/user-attachments/assets/2becd1b4-cb70-42d1-8052-c12d2a750fa1",
                    caption="2️⃣ Антиоксидант из сока свеклы. Используется совместно с облепихой и серебром",
                    reply_markup=markup
                )

            elif step == "3":
                # Здесь пример третьего продукта, если его пока нет, можно заменить или убрать
                markup = InlineKeyboardMarkup(row_width=1)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/641/"),  # заменить при необходимости
                    InlineKeyboardButton("◀️ Назад", callback_data="prostuda_2")
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://example.com/product3.jpg",  # заменить на реальную картинку 3-го продукта
                    caption="3️⃣ Пример третьего продукта.",
                    reply_markup=markup
                )

        elif data in ["joints", "liver", "vitamins"]:
            await bot.send_message(user_id, f"Вы выбрали категорию: {data}")

        await bot.answer_callback_query(callback_query.id)

    @dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
    async def forward_user_message(message: types.Message):
        await bot.send_message(
            ADMIN_ID,
            f"📩 Сообщение от @{message.from_user.username or 'без username'} (ID: {message.from_user.id}):\n\n{message.text}"
        )
        await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)

else:
    print("❌ Бот не может быть запущен без поддержки SSL. Пожалуйста, используйте среду с поддержкой HTTPS.")
