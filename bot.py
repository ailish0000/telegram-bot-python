# Импортируем нужные модули из aiogram
import os
from dotenv import load_dotenv  # Для загрузки переменных из .env

# Проверка на поддержку SSL (важно для aiogram)
try:
    import ssl
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
    print("⚠️ Библиотека SSL недоступна. Бот не сможет установить HTTPS-соединения.")

if SSL_AVAILABLE:
    from aiogram import Bot, Dispatcher, executor, types
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    # Загружаем переменные окружения из файла .env
    load_dotenv()

    # Получаем токен бота и ID администратора из переменных окружения
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))  # Важно: должен быть числом

    # Создаём экземпляры бота и диспетчера
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(bot)

    # Функция, создающая главное меню (inline-кнопки)
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

    # Функция, создающая меню выбора продукта
    def product_menu():
        markup = InlineKeyboardMarkup(row_width=2)
        markup.add(
            InlineKeyboardButton("Для волос", callback_data="hair"),
            InlineKeyboardButton("Для суставов", callback_data="joints"),
            InlineKeyboardButton("Для печени", callback_data="liver"),
            InlineKeyboardButton("Витамины", callback_data="vitamins"),
            InlineKeyboardButton("Сообщить об ошибке ❌", callback_data="report_error")
        )
        return markup

    # Меню выбора города
    def city_menu():
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("Минск", callback_data="Minsk"),
            InlineKeyboardButton("Гомель", callback_data="Gomel"),
            InlineKeyboardButton("Брест", callback_data="Brest"),
            InlineKeyboardButton("Витебск", callback_data="Vitebsk"),
            InlineKeyboardButton("Могилев", callback_data="Mogilev"),
            InlineKeyboardButton("Нет моего города", callback_data="none_city"),
            InlineKeyboardButton("Сообщить об ошибке ❌", callback_data="report_error")
        )
        return markup

    # Обработчик команды /start и /menu
    @dp.message_handler(commands=["start", "menu"])
    async def send_welcome(message: types.Message):
        await message.answer("Выбери, что тебе подходит 👇", reply_markup=main_menu())

    # Обработчик команды /registration
    @dp.message_handler(commands=["registration"])
    async def send_registration_link(message: types.Message):
        await message.answer("Ссылка для регистрации: https://aur-ora.com/auth/registration/666282189484")

    # Обработчик команды /catalog
    @dp.message_handler(commands=["catalog"])
    async def send_catalog_link(message: types.Message):
        await message.answer("Ссылка на каталог: https://aur-ora.com/catalog/vse_produkty/")

    # Обработчик нажатий на inline-кнопки
    @dp.callback_query_handler(lambda c: True)
    async def handle_callback(callback_query: types.CallbackQuery):
        data = callback_query.data
        user_id = callback_query.from_user.id

        if data == "check_address":
            await bot.send_message(user_id, "Введите свой город:")

        elif data == "select_product":
            await bot.send_message(user_id, "Выберите категорию продукта:", reply_markup=product_menu())

        elif data == "ask_question":
            await bot.send_message(user_id, "✉️ Напишите ваш вопрос в чат, и я обязательно на него отвечу.")

        elif data == "check_city":
            await bot.send_message(user_id, "Выберите город:", reply_markup=city_menu())

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

        elif data in ["hair", "joints", "liver", "vitamins"]:
            await bot.send_message(user_id, f"Вы выбрали категорию: {data}")

        await bot.answer_callback_query(callback_query.id)

    # Обработчик текстовых сообщений (не команд)
    @dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
    async def forward_user_message(message: types.Message):
        await bot.send_message(
            ADMIN_ID,
            f"📩 Сообщение от @{message.from_user.username or 'без username'} (ID: {message.from_user.id}):\n\n{message.text}"
        )
        await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")

    # Запускаем бота
    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)
else:
    print("❌ Бот не может быть запущен без поддержки SSL. Пожалуйста, используйте среду с поддержкой HTTPS.")



