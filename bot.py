# Импортируем нужные модули из aiogram
import os
import asyncio
from dotenv import load_dotenv

try:
    import ssl
    SSL_AVAILABLE = True
except ImportError:
    SSL_AVAILABLE = False
    print("⚠️ Библиотека SSL недоступна. Бот не сможет установить HTTPS-соединения.")

if SSL_AVAILABLE:
    from aiogram import Bot, Dispatcher, executor, types
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
    from aiogram.dispatcher.filters.state import State, StatesGroup
    from aiogram.contrib.fsm_storage.memory import MemoryStorage
    from aiogram.dispatcher import FSMContext

    load_dotenv()

    BOT_TOKEN = os.getenv("BOT_TOKEN")
    ADMIN_ID = int(os.getenv("ADMIN_ID"))

    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    WELCOME_IMAGE = "https://github.com/user-attachments/assets/474d0575-01ed-45cc-8253-5e35bccda672"
    MENU_IMAGE = "https://github.com/user-attachments/assets/832593ee-2617-4ef6-9656-ff4d4f9506b8"

    user_started = set()

    # Хранилище обращений: user_id -> список сообщений
    user_messages = {}

    class AdminReply(StatesGroup):
        waiting_for_reply = State()

    # Главное меню пользователя
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

    # Меню выбора продукта
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

    # Меню выбора города
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

    # --------------------- ОБРАБОТЧИКИ ПОЛЬЗОВАТЕЛЯ ---------------------

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

        elif data == "report_error":
            await bot.send_message(user_id, "⚠️ Расскажите подробнее об ошибке, чтобы я могла её исправить.")

        elif data.startswith("prostuda"):
            step = data.replace("prostuda", "").strip("_") or "1"

            if step == "1":
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/543/")
                )
                markup.add(
                    InlineKeyboardButton("◀️ Назад", callback_data="select_product"),
                    InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_2")
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://github.com/user-attachments/assets/ac7b0dcc-2786-4c3e-b2bb-49e2d5c5af64",
                    caption="1️⃣ Антиоксидант из сока облепихи. Используется вместе с соком свеклы и серебром",
                    reply_markup=markup
                )

            elif step == "2":
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/641/")
                )
                markup.add(
                    InlineKeyboardButton("◀️ Назад", callback_data="prostuda_1"),
                    InlineKeyboardButton("Дальше ▶️", callback_data="prostuda_3")
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://github.com/user-attachments/assets/2becd1b4-cb70-42d1-8052-c12d2a750fa1",
                    caption="2️⃣ Антиоксидант из сока свеклы. Используется совместно с облепихой и серебром",
                    reply_markup=markup
                )

            elif step == "3":
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(
                    InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/7160/")
                )
                markup.add(
                    InlineKeyboardButton("◀️ Назад", callback_data="prostuda_2"),
                    InlineKeyboardButton("В меню ▶️", callback_data="select_product")
                )
                await bot.send_photo(
                    chat_id=user_id,
                    photo="https://github.com/user-attachments/assets/01561f93-7dbd-46aa-a6a2-c0caaad30d68",
                    caption="3️⃣ Серебро коллоидное — сильный антисептик. Используется для борьбы с вирусами и бактериями",
                    reply_markup=markup
                )

            else:
                await bot.send_message(user_id, "Неверный шаг.")

        # Аналогично можно добавить другие категории продуктов

        elif data in ("Minsk", "Minsk_region", "Gomel", "Gomel_region", "Brest", "Brest_region",
                      "Vitebsk", "Vitebsk_region", "Mogilev", "Mogilev_region", "none_city"):
            city_urls = {
                "Minsk": "https://aur-ora.com/shop/minsk",
                "Minsk_region": "https://aur-ora.com/shop/minsk-region",
                "Gomel": "https://aur-ora.com/shop/gomel",
                "Gomel_region": "https://aur-ora.com/shop/gomel-region",
                "Brest": "https://aur-ora.com/shop/brest",
                "Brest_region": "https://aur-ora.com/shop/brest-region",
                "Vitebsk": "https://aur-ora.com/shop/vitebsk",
                "Vitebsk_region": "https://aur-ora.com/shop/vitebsk-region",
                "Mogilev": "https://aur-ora.com/shop/mogilev",
                "Mogilev_region": "https://aur-ora.com/shop/mogilev-region",
                "none_city": "https://aur-ora.com/shop",
            }
            url = city_urls.get(data, "https://aur-ora.com/shop")
            await bot.send_message(user_id, f"Список магазинов в вашем регионе: {url}")

        else:
            await bot.send_message(user_id, "Неизвестная команда.")

    # --------------------- ОБРАБОТЧИКИ АДМИН-ПАНЕЛИ ---------------------

    # Уведомление админу о новых сообщениях
    async def notify_admin_about_message(user_id, text):
        try:
            await bot.send_message(ADMIN_ID, f"Новое сообщение от пользователя {user_id}:\n\n{text}")
        except Exception:
            pass

    @dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
    async def handle_user_message(message: types.Message):
        user_id = message.from_user.id
        if user_id == ADMIN_ID:
            # Админ пишет обычный текст вне FSM — игнорируем здесь
            return
        if user_id not in user_messages:
            user_messages[user_id] = []
        user_messages[user_id].append(message.text)
        await notify_admin_about_message(user_id, message.text)
        await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")

    admin_menu = ReplyKeyboardMarkup(resize_keyboard=True).add(
        KeyboardButton("📊 Статистика"),
        KeyboardButton("💬 Обращения"),
        KeyboardButton("📢 Рассылка"),
        KeyboardButton("❌ Выйти из админки")
    )

    @dp.message_handler(lambda message: message.from_user.id == ADMIN_ID and message.text == "/admin")
    async def admin_start(message: types.Message):
        await message.answer("Вы в админ-панели. Выберите действие:", reply_markup=admin_menu)

    @dp.message_handler(lambda message: message.from_user.id == ADMIN_ID)
    async def admin_handler(message: types.Message, state: FSMContext):
        if message.text == "📊 Статистика":
            total_users = len(user_messages)
            total_messages = sum(len(msgs) for msgs in user_messages.values())
            await message.answer(f"Пользователей: {total_users}\nСообщений: {total_messages}")

        elif message.text == "💬 Обращения":
            if not user_messages:
                await message.answer("Обращений пока нет.")
                return

            text = "Последние обращения:\n"
            # Покажем последние 10 пользователей с их последними 3 сообщениями
            for user_id, msgs in list(user_messages.items())[-10:]:
                text += f"\nПользователь {user_id}:\n"
                for i, msg_text in enumerate(msgs[-3:], 1):
                    text += f"{i}. {msg_text}\n"
                text += f"➡️ /reply_{user_id} — Ответить этому пользователю\n"
            await message.answer(text)

        elif message.text and message.text.startswith("/reply_"):
            try:
                user_id_to_reply = int(message.text.split("_")[1])
                await state.update_data(reply_to=user_id_to_reply)
                await AdminReply.waiting_for_reply.set()
                await message.answer(f"Введите сообщение для пользователя {user_id_to_reply}:", reply_markup=ReplyKeyboardRemove())
            except Exception:
                await message.answer("Ошибка при определении пользователя.")

        elif message.text == "📢 Рассылка":
            await message.answer("Введите сообщение для рассылки всем пользователям:", reply_markup=ReplyKeyboardRemove())
            await AdminReply.waiting_for_reply.set()
            await state.update_data(reply_to="broadcast")

        elif message.text == "❌ Выйти из админки":
            await message.answer("Вы вышли из админ-панели.", reply_markup=ReplyKeyboardRemove())
            await state.finish()

        else:
            await message.answer("Неизвестная команда админки. Используйте меню.")

    @dp.message_handler(state=AdminReply.waiting_for_reply)
    async def process_admin_reply(message: types.Message, state: FSMContext):
        data = await state.get_data()
        reply_to = data.get("reply_to")
        text = message.text

        if reply_to == "broadcast":
            count = 0
            for user_id in user_messages.keys():
                try:
                    await bot.send_message(user_id, f"📢 Рассылка:\n\n{text}")
                    count += 1
                except Exception:
                    pass
            await message.answer(f"Рассылка отправлена {count} пользователям.")
        else:
            try:
                await bot.send_message(reply_to, f"💬 Ответ администратора:\n\n{text}")
                await message.answer("Ответ отправлен пользователю.")
            except Exception:
                await message.answer("Не удалось отправить сообщение пользователю.")
        await state.finish()

    if __name__ == '__main__':
        print("Бот запущен...")
        executor.start_polling(dp, skip_updates=True)

else:
    print("SSL не доступен, бот не запущен.")

