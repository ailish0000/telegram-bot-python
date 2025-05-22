import os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.contrib.middlewares.logging import LoggingMiddleware

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Получение токена и ID администратора из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(KeyboardButton("Регистрация"))
main_menu.add(KeyboardButton("Проверить адрес"))
main_menu.add(KeyboardButton("Выбрать продукт"))
main_menu.add(KeyboardButton("Задать вопрос"))
main_menu.add(KeyboardButton("Сообщить об ошибке"))

# Подменю для выбора продукта
product_menu = ReplyKeyboardMarkup(resize_keyboard=True)
product_menu.add(KeyboardButton("Для волос"))
product_menu.add(KeyboardButton("Для суставов"))
product_menu.add(KeyboardButton("Для печени"))
product_menu.add(KeyboardButton("Витамины"))
product_menu.add(KeyboardButton("Назад"))

# Обработка команды /start и /menu
@dp.message_handler(commands=["start", "menu"])
async def send_welcome(message: types.Message):
    await message.reply("Выбери что тебе подходит:", reply_markup=main_menu)
    # Уведомление администратора о новом пользователе
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"Новый пользователь: {message.from_user.full_name} (@{message.from_user.username})")

# Обработка кнопки "Регистрация"
@dp.message_handler(Text(equals="Регистрация"))
async def registration(message: types.Message):
    await message.reply("Пожалуйста, зарегистрируйтесь по ссылке:\nhttps://aur-ora.com/auth/registration/666282189484")

# Обработка кнопки "Проверить адрес"
@dp.message_handler(Text(equals="Проверить адрес"))
async def check_address(message: types.Message):
    await message.reply("Введите свой город:")

# Обработка ввода города
@dp.message_handler(lambda message: message.text and message.text not in ["Регистрация", "Проверить адрес", "Выбрать продукт", "Задать вопрос", "Сообщить об ошибке", "Назад", "Для волос", "Для суставов", "Для печени", "Витамины"])
async def handle_city(message: types.Message):
    await message.reply(f"Вы ввели город: {message.text}")

# Обработка кнопки "Выбрать продукт"
@dp.message_handler(Text(equals="Выбрать продукт"))
async def choose_product(message: types.Message):
    await message.reply("Выберите категорию продукта:", reply_markup=product_menu)

# Обработка выбора продукта
@dp.message_handler(Text(equals=["Для волос", "Для суставов", "Для печени", "Витамины"]))
async def product_selected(message: types.Message):
    await message.reply(f"Вы выбрали: {message.text}")

# Обработка кнопки "Назад"
@dp.message_handler(Text(equals="Назад"))
async def back_to_menu(message: types.Message):
    await message.reply("Вы вернулись в главное меню.", reply_markup=main_menu)

# Обработка кнопки "Задать вопрос"
@dp.message_handler(Text(equals="Задать вопрос"))
async def ask_question(message: types.Message):
    await message.reply("Напишите ваш вопрос в чат, и я обязательно на него отвечу.")

# Обработка кнопки "Сообщить об ошибке"
@dp.message_handler(Text(equals="Сообщить об ошибке"))
async def report_error(message: types.Message):
    await message.reply("Расскажите подробнее об ошибке, чтобы я смогла её исправить и сделать бота лучше.")

# Обработка всех остальных сообщений (вопросов и ошибок)
@dp.message_handler()
async def handle_messages(message: types.Message):
    if ADMIN_ID:
        await bot.send_message(ADMIN_ID, f"Сообщение от {message.from_user.full_name} (@{message.from_user.username}):\n{message.text}")
    await message.reply("Спасибо за ваше сообщение! Я передала его администратору.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
