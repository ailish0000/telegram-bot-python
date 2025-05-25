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
        """
        Удаляет все предыдущие сообщения в чате, создавая эффект Таноса.
        """
        try:
            # Получаем историю чата (до 100 сообщений)
            async for msg in bot.iter_history(chat_id, limit=100):
                try:
                    # Удаляем каждое сообщение
                    await bot.delete_message(chat_id, msg.message_id)
                except:
                    continue
        except Exception as e:
            # Игнорируем ошибки при удалении
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

    @dp.callback_query_handler()
    async def handle_callbacks(callback_query: types.CallbackQuery):
        data = callback_query.data
        user_id = callback_query.from_user.id

        await thanos_effect(user_id)

        if data == "select_product":
            await bot.send_photo(chat_id=user_id, photo=MENU_IMAGE, caption="Выберите категорию продукта:", reply_markup=product_menu())

        elif data == "prostuda":
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/543/"))
            markup.row(
                InlineKeyboardButton("◀️ Назад", callback_data="select_product"),
                InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_2")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/ac7b0dcc-2786-4c3e-b2bb-49e2d5c5af64",
                caption="1️⃣ Антиоксидант из сока облепихи.",
                reply_markup=markup
            )

        elif data == "prostuda_2":
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/641/"))
            markup.row(
                InlineKeyboardButton("◀️ Назад", callback_data="prostuda"),
                InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_3")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/2becd1b4-cb70-42d1-8052-c12d2a750fa1",
                caption="2️⃣ Сок свеклы.",
                reply_markup=markup
            )

        elif data == "prostuda_3":
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/447/"))
            markup.row(InlineKeyboardButton("◀️ Назад", callback_data="prostuda_2"))
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/df53f6da-2cdd-4d75-b20e-0206c3252456",
                caption="3️⃣ Коллоидное серебро.",
                reply_markup=markup
            )

        await bot.answer_callback_query(callback_query.id)

    if __name__ == "__main__":
        executor.start_polling(dp, skip_updates=True)
else:
    print("❌ Бот не может быть запущен без поддержки SSL. Пожалуйста, используйте среду с поддержкой HTTPS.")
