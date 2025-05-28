import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.contrib.middlewares.logging import LoggingMiddleware

API_TOKEN = 'YOUR_BOT_TOKEN_HERE'

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("Для волос и ногтей", callback_data="hair_1"),
        InlineKeyboardButton("Для печени", callback_data="liver_1"),
        InlineKeyboardButton("Для иммунитета", callback_data="immune_1")
    )
    await message.answer("Выберите категорию:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: True)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    # начало кнопки волосы
    if data.startswith("hair"):
        step = data.replace("hair", "").strip("_") or "1"

        if step == "1":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/vse_produkty/10033/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="select_product"),
                InlineKeyboardButton("Дальше ▶️", callback_data="hair_2")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/2fc926af-13d2-4b11-9e3c-7c4aaf8008f3",
                caption="1️⃣ Витамины для укрепления волос и ногтей",
                reply_markup=markup
            )

        elif step == "2":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/vse_produkty/10119/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="hair_1")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/d0204052-0c91-4338-b52f-1f7fa9703819",
                caption="2️⃣ Натуральная маска для питания и восстановления волос",
                reply_markup=markup
            )

    # конец кнопки волосы

    # начало кнопки печень
    elif data.startswith("liver"):
        step = data.replace("liver", "").strip("_") or "1"

        if step == "1":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/640/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="select_product"),
                InlineKeyboardButton("Дальше ▶️", callback_data="liver_2")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/667eac4a-18de-4fc2-9c1d-e4fba256dfd4",
                caption="1️⃣ Порошок для очищения печени на основе расторопши и артишока",
                reply_markup=markup
            )

        elif step == "2":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/aktsii_3_a/703/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="liver_1"),
                InlineKeyboardButton("Дальше ▶️", callback_data="liver_3")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/e96ef2cf-0de6-4d04-b404-4e1cfc2cd79b",
                caption="2️⃣ Комплекс для детокса организма и поддержания функций печени",
                reply_markup=markup
            )

        elif step == "3":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/vse_produkty/10118/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="liver_2"),
                InlineKeyboardButton("Дальше ▶️", callback_data="liver_4")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/7a496d2e-3ef9-41fa-9a1f-11efb74a3a3a",
                caption="3️⃣ Натуральный комплекс для нормализации работы печени",
                reply_markup=markup
            )

        elif step == "4":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/643/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="liver_3"),
                InlineKeyboardButton("Дальше ▶️", callback_data="liver_5")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/f23cfc7a-8e8c-4d8d-92ec-48649177a30c",
                caption="4️⃣ Поддержка печени и ЖКТ на основе растительных экстрактов",
                reply_markup=markup
            )

        elif step == "5":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/9130/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="liver_4")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/8fdc2fa9-02df-4c75-a13c-0e96fd816800",
                caption="5️⃣ Комплекс с лецитином для восстановления клеток печени",
                reply_markup=markup
            )
    # конец кнопки печень

    # начало кнопки иммунитет
    elif data.startswith("immune"):
        step = data.replace("immune", "").strip("_") or "1"

        if step == "1":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/667/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="select_product"),
                InlineKeyboardButton("Дальше ▶️", callback_data="immune_2")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/2850e931-b583-4c87-a899-f1a490e4d746",
                caption="1️⃣ Сироп с эхинацеей и шиповником для укрепления иммунитета",
                reply_markup=markup
            )

        elif step == "2":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/zdorove/676/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="immune_1"),
                InlineKeyboardButton("Дальше ▶️", callback_data="immune_3")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/1b6c4b5c-1037-46b3-8d87-1d7ea1e3c356",
                caption="2️⃣ Натуральный бальзам с прополисом и травами для иммунной поддержки",
                reply_markup=markup
            )

        elif step == "3":
            markup = InlineKeyboardMarkup(row_width=2)
            markup.add(
                InlineKeyboardButton("Читать подробнее", url="https://aur-ora.com/catalog/vse_produkty/10032/")
            )
            markup.add(
                InlineKeyboardButton("◀️ Назад", callback_data="immune_2")
            )
            await bot.send_photo(
                chat_id=user_id,
                photo="https://github.com/user-attachments/assets/ef42d9e2-cf2e-4b1b-88be-b4060e8fae95",
                caption="3️⃣ Формула иммунитета с витаминами и цинком",
                reply_markup=markup
            )
    # конец кнопки иммунитет

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
