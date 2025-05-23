from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from bs4 import BeautifulSoup
import logging
import asyncio
import os
import requests

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("Регистрация", callback_data="registration"),
    InlineKeyboardButton("Проверить адрес", callback_data="check_address"),
    InlineKeyboardButton("Выбрать продукт", callback_data="select_product")
)

product_menu = InlineKeyboardMarkup(row_width=2)
product_menu.add(
    InlineKeyboardButton("Для печени", callback_data="liver"),
    InlineKeyboardButton("Для волос", callback_data="hair"),
    InlineKeyboardButton("Для суставов", callback_data="joints"),
    InlineKeyboardButton("Витамины", callback_data="vitamins"),
    InlineKeyboardButton("Задать вопрос", callback_data="ask_question"),
    InlineKeyboardButton("Сообщить об ошибке", callback_data="report_error")
)

PRODUCT_URLS = [
    "https://aur-ora.com/catalog/zdorove/640",
    "https://aur-ora.com/catalog/aktsii_3_a/703",
    "https://aur-ora.com/catalog/vse_produkty/10118",
    "https://aur-ora.com/catalog/zdorove/643",
    "https://aur-ora.com/catalog/zdorove/9130"
]

user_carousel_positions = {}

def fetch_product_data_sync(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("h1").text.strip()
    description_tag = soup.find("div", class_="description")
    description = description_tag.text.strip() if description_tag else "Нет описания"
    img_tag = soup.find("img")
    img_url = "https://aur-ora.com" + img_tag["src"] if img_tag and img_tag.get("src") else None
    return title, description, img_url

async def fetch_product_data(url):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fetch_product_data_sync, url)

async def send_product(user_id):
    index = user_carousel_positions.get(user_id, 0)
    if index >= len(PRODUCT_URLS):
        await bot.send_message(user_id, "Вы просмотрели все товары.", reply_markup=main_menu)
        return

    url = PRODUCT_URLS[index]
    title, description, img_url = await fetch_product_data(url)
    caption = f"<b>{title}</b>\n\n{description}\n\n<a href='{url}'>Перейти на сайт</a>"

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

@dp.message_handler(commands=["start", "menu"])
async def send_welcome(message: types.Message):
    await message.answer("Выбери что тебе подходит:", reply_markup=main_menu)

@dp.message_handler(commands=["registration"])
async def registration_command(message: types.Message):
    await message.answer("https://aur-ora.com/auth/registration/666282189484")

@dp.message_handler(commands=["catalog"])
async def catalog_command(message: types.Message):
    await message.answer("https://aur-ora.com/catalog/vse_produkty/")

@dp.callback_query_handler(lambda c: c.data in ["liver", "next_product", "prev_product"])
async def handle_carousel(callback_query: types.CallbackQuery):
    logging.info(f"НАЖАТА КНОПКА: {callback_query.data}")
    await callback_query.answer()
    user_id = callback_query.from_user.id
    data = callback_query.data

    if data == "liver":
        user_carousel_positions[user_id] = 0
    elif data == "next_product":
        user_carousel_positions[user_id] += 1
    elif data == "prev_product":
        user_carousel_positions[user_id] = max(0, user_carousel_positions[user_id] - 1)

    await send_product(user_id)

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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)


