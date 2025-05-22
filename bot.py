from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню
def main_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Регистрация", url="https://aur-ora.com/auth/registration/666282189484"),
        InlineKeyboardButton("Проверить адрес", callback_data="check_address"),
        InlineKeyboardButton("Выбрать продукт", callback_data="select_product")
    )
    return markup

# Меню продуктов
def product_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Для волос", callback_data="hair"),
        InlineKeyboardButton("Для суставов", callback_data="joints"),
        InlineKeyboardButton("Для печени", callback_data="liver"),
        InlineKeyboardButton("Витамины", callback_data="vitamins"),
        InlineKeyboardButton("Задать вопрос", callback_data="ask_question"),
        InlineKeyboardButton("Сообщить об ошибке", callback_data="report_error")
    )
    return markup

# Приветствие
@dp.message_handler(commands=["start", "menu"])
async def send_welcome(message: types.Message):
    await message.answer("Выбери, что тебе подходит 👇", reply_markup=main_menu())

# Обработка нажатий на кнопки
@dp.callback_query_handler(lambda c: True)
async def handle_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    message_id = callback_query.message.message_id

    # Удаляем кнопки
    await bot.edit_message_reply_markup(chat_id=user_id, message_id=message_id, reply_markup=None)

    # Обработка действий
    if data == "check_address":
        await bot.send_message(user_id, "Введите свой город:")

    elif data == "select_product":
        await bot.send_message(user_id, "Выберите категорию продукта:", reply_markup=product_menu())

    elif data == "ask_question":
        await bot.send_message(user_id, "✉️ Напишите ваш вопрос в чат, и я обязательно на него отвечу.")

    elif data == "report_error":
        await bot.send_message(user_id, "⚠️ Расскажите подробнее об ошибке, чтобы я могла её исправить.")

    elif data in ["hair", "joints", "liver", "vitamins"]:
        await bot.send_message(user_id, f"Вы выбрали категорию: {data}")

    await bot.answer_callback_query(callback_query.id)

# Пересылка сообщений админу
@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def forward_user_message(message: types.Message):
    await bot.send_message(ADMIN_ID,
        f"📩 Сообщение от @{message.from_user.username or 'без username'} (ID: {message.from_user.id}):\n\n{message.text}"
    )
    await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
