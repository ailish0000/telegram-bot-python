from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from bs4 import BeautifulSoup
import logging
import asyncio
import os
import requests  # Используем requests вместо aiohttp

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Токен из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# Главное меню с кнопками
main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("Регистрация", callback_data="registration"),
    InlineKeyboardButton("Проверить адрес", callback_data="check_address"),
    InlineKeyboardButton("Выбрать продукт", callback_data="select_product")
)

# Подменю выбора продуктов
product_menu = InlineKeyboardMarkup(row_width=2)
product_menu.add(
    InlineKeyboardButton("Для волос", callback_data="hair"),
    InlineKeyboardButton("Для суставов", callback_data="joints"),
    InlineKeyboardButton("Для печени", callback_data="liver"),
    InlineKeyboardButton("Витамины", callback_data="vitamins"),
    InlineKeyboardButton("Задать вопрос", callback_data="ask_question"),
    InlineKeyboardButton("Сообщить об ошибке", callback_data="report_error")
)

# Ссылки на продукты (для карусели)
PRODUCT_URLS = [
    "https://aur-ora.com/catalog/zdorove/640",
    "https://aur-ora.com/catalog/aktsii_3_a/703",
    "https://aur-ora.com/catalog/vse_produkty/10118",
    "https://aur-ora.com/catalog/zdorove/643",
    "https://aur-ora.com/catalog/zdorove/9130"
]

# Словарь для отслеживания позиции каждого пользователя
user_carousel_positions = {}

# Загрузка данных товара с сайта (через requests)
def fetch_product_data_sync(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.find("h1").text.strip()
    description_tag = soup.find("div", class_="description")
    description = description_tag.text.strip() if description_tag else "Нет описания"
    img_tag = soup.find("img")
    img_url = "https://aur-ora.com" + img_tag["src"] if img_tag and img_tag.get("src") else None

    return title, description, img_url

# Асинхронная обертка для requests
async def fetch_product_data(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_product_data_sync, url)

# Отправка информации о текущем товаре
async def send_product(user_id):
    index = user_carousel_positions.get(user_id, 0)
    if index >= len(PRODUCT_URLS):
        await bot.send_message(user_id, "Вы просмотрели все товары.", reply_markup=main_menu)
        return

    url = PRODUCT_URLS[index]
    title, description, img_url = await fetch_product_data(url)

    caption = f"<b>{title}</b>\n\n{description}\n\n<a href='{url}'>Перейти на сайт</a>"

    # Кнопки "Назад", "Дальше" и "Назад в меню"
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    if index > 0:
        buttons.append(InlineKeyboardButton("⬅ Назад", callback_data="prev_product"))
    if index < len(PRODUCT_URLS) - 1:
        buttons.append(InlineKeyboardButton("➡ Дальше", callback_data="next_product"))
    markup.row(*buttons)
    markup.add(InlineKeyboardButton("🏠 Назад в меню", callback_data="back_to_menu"))

    await bot.send_photo(
        chat_id=user_id,
        photo=img_url,
        caption=caption,
        parse_mode="HTML",
        reply_markup=markup
    )

# Команда /start и /menu
@dp.message_handler(commands=["start", "menu"])
async def send_welcome(message: types.Message):
    await message.answer("Выбери что тебе подходит:", reply_markup=main_menu)

# Команда /registration
@dp.message_handler(commands=["registration"])
async def registration_command(message: types.Message):
    await message.answer("https://aur-ora.com/auth/registration/666282189484")

# Команда /catalog
@dp.message_handler(commands=["catalog"])
async def catalog_command(message: types.Message):
    await message.answer("https://aur-ora.com/catalog/vse_produkty/")

# Обработка кнопки "Для печени"
@dp.callback_query_handler(lambda c: c.data == "liver")
async def handle_liver(callback_query: types.CallbackQuery):
    await callback_query.answer()  # Убирает "часики" после нажатия кнопки
    user_id = callback_query.from_user.id
    user_carousel_positions[user_id] = 0
    await send_product(user_id)

# Обработка кнопки "дальше"
@dp.callback_query_handler(lambda c: c.data == "next_product")
async def next_product(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_carousel_positions[user_id] += 1
    await send_product(user_id)

# Обработка кнопки "назад"
@dp.callback_query_handler(lambda c: c.data == "prev_product")
async def prev_product(callback_query: types.CallbackQuery):
    await callback_query.answer()
    user_id = callback_query.from_user.id
    user_carousel_positions[user_id] = max(0, user_carousel_positions[user_id] - 1)
    await send_product(user_id)

# Обработка нажатий на остальные кнопки меню (должна быть последней!)
@dp.callback_query_handler()
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data

    if data == "registration":
        await bot.send_message(callback_query.from_user.id, "https://aur-ora.com/auth/registration/666282189484")
    elif data == "check_address":
        await bot.send_message(callback_query.from_user.id, "Введите свой город")
    elif data == "select_product":
        await bot.send_message(callback_query.from_user.id, "Выберите категорию:", reply_markup=product_menu)
    elif data == "ask_question":
        await bot.send_message(callback_query.from_user.id, "Напишите ваш вопрос в чат и я обязательно на него отвечу")
    elif data == "report_error":
        await bot.send_message(callback_query.from_user.id, "Расскажите подробнее об ошибке, чтобы я смогла ее исправить и сделать бота лучше")
    elif data == "back_to_menu":
        await bot.send_message(callback_query.from_user.id, "Выбери что тебе подходит:", reply_markup=main_menu)

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)


