import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import executor
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from collections import defaultdict
import os

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "123456789"))

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

stats = {
    "users": set(),
    "messages": defaultdict(int),
    "errors": 0
}

class UserMessageStates(StatesGroup):
    waiting_for_user_input = State()

main_menu = InlineKeyboardMarkup(row_width=2)
main_menu.add(
    InlineKeyboardButton("\ud83c\udfe3 \u041a\u0430\u0442\u0430\u043b\u043e\u0433 \u043f\u0440\u043e\u0434\u0443\u043a\u0446\u0438\u0438", callback_data="select_product"),
    InlineKeyboardButton("\u2753 \u0417\u0430\u0434\u0430\u0442\u044c \u0432\u043e\u043f\u0440\u043e\u0441", callback_data="ask_question"),
    InlineKeyboardButton("\u26a0\ufe0f \u0421\u043e\u043e\u0431\u0449\u0438\u0442\u044c \u043e\u0431 \u043e\u0448\u0438\u0431\u043a\u0435", callback_data="report_issue")
)

product_menu = InlineKeyboardMarkup(row_width=2)
product_menu.add(
    InlineKeyboardButton("\ud83e\udc8a \u041e\u0442 \u043f\u0440\u043e\u0441\u0442\u0443\u0434\u044b", callback_data="prostuda"),
    InlineKeyboardButton("\ud83d\udc87 \u0412\u043e\u043b\u043e\u0441\u044b / \u041d\u043e\u0433\u0442\u0438", callback_data="hair"),
    InlineKeyboardButton("\ud83e\uddb4 \u0421\u0443\u0441\u0442\u0430\u0432\u044b", callback_data="joints"),
    InlineKeyboardButton("\ud83e\udda0 \u041f\u0435\u0447\u0435\u043d\u044c", callback_data="liver"),
    InlineKeyboardButton("\ud83d\udc8a \u0412\u0438\u0442\u0430\u043c\u0438\u043d\u044b", callback_data="vitamins"),
    InlineKeyboardButton("\ud83e\uddec \u0410\u043d\u0442\u0438\u043f\u0430\u0440\u0430\u0437\u0438\u0442\u0430\u0440\u043a\u0430", callback_data="antiparazit"),
    InlineKeyboardButton("\ud83e\uddf9 \u0421\u043e\u0440\u0431\u0435\u043d\u0442\u044b", callback_data="sorbent"),
    InlineKeyboardButton("\ud83d\udd25 \u0425\u0438\u0442\u044b \u043f\u0440\u043e\u0434\u0430\u0436", callback_data="top"),
    InlineKeyboardButton("\ud83c\udf3f \u0414\u0435\u0442\u043e\u043a\u0441", callback_data="detox"),
    InlineKeyboardButton("\u21a9\ufe0f \u041d\u0430\u0437\u0430\u0434", callback_data="main_menu")
)

@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    stats["users"].add(user_id)
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=main_menu)

@dp.callback_query_handler(lambda c: c.data in ["ask_question", "report_issue"])
async def handle_user_issue(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = callback_query.from_user.id
    issue_type = "вопрос" if callback_query.data == "ask_question" else "ошибку"
    await state.update_data(issue_type=issue_type, sender_id=user_id)
    await UserMessageStates.waiting_for_user_input.set()
    await bot.send_message(user_id, f"✍️ Пожалуйста, введите ваш {issue_type}, и администратор получит его.")
    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(state=UserMessageStates.waiting_for_user_input)
async def forward_user_issue(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("sender_id")
    issue_type = data.get("issue_type")

    if user_id and issue_type:
        await bot.send_message(
            ADMIN_ID,
            f"📩 Новое обращение:\n\n"
            f"Тип: {issue_type}\n"
            f"ID пользователя: {user_id}\n"
            f"Сообщение:\n{message.text}",
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("✉️ Ответить", callback_data=f"reply_{user_id}")
            )
        )
        await message.reply("✅ Спасибо! Ваше сообщение передано администратору.")
    else:
        await message.reply("❌ Произошла ошибка. Попробуйте снова.")
    await state.finish()

@dp.callback_query_handler(lambda c: True)
async def callback_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    data = callback_query.data
    stats["messages"][user_id] += 1

    try:
        if data == "main_menu":
            await bot.send_message(chat_id=user_id, text="Главное меню:", reply_markup=main_menu)

        elif data == "select_product":
            await bot.send_message(chat_id=user_id, text="Выберите категорию:", reply_markup=product_menu)

        elif data.split("_")[0] in ["prostuda", "hair", "joints", "liver", "vitamins", "antiparazit", "sorbent", "top", "detox"]:
            parts = data.split("_")
            prefix = parts[0]
            step = int(parts[1]) if len(parts) > 1 else 1

            messages = [
                ("https://github.com/user-attachments/assets/ac7b0dcc-2786-4c3e-b2bb-49e2d5c5af64", "1️⃣ ...", "https://aur-ora.com/catalog/zdorove/543/"),
                ("https://github.com/user-attachments/assets/2becd1b4-cb70-42d1-8052-c12d2a750fa1", "2️⃣ ...", "https://aur-ora.com/catalog/zdorove/641/"),
                ("https://github.com/user-attachments/assets/0d0ee28f-3110-4b2e-9f82-d20989091e0f", "3️⃣ ...", "https://aur-ora.com/catalog/zdorove/447/"),
                ("https://github.com/user-attachments/assets/89b794f8-7c3f-4d45-bc65-d980ba18fbeb", "4️⃣ ...", "https://aur-ora.com/catalog/vse_produkty/24839"),
                ("https://github.com/user-attachments/assets/6be0aed7-982b-4867-a039-4c7005743769", "5️⃣ ...", "https://aur-ora.com/catalog/vse_produkty/7347/")
            ]

            index = step - 1
            if 0 <= index < len(messages):
                markup = InlineKeyboardMarkup(row_width=2)
                markup.add(InlineKeyboardButton("Читать подробнее", url=messages[index][2]))

                nav_buttons = []
                if index > 0:
                    nav_buttons.append(InlineKeyboardButton("◀️ Назад", callback_data=f"{prefix}_{index}"))
                if index < len(messages) - 1:
                    nav_buttons.append(InlineKeyboardButton("Дальше ▶️", callback_data=f"{prefix}_{index + 2}"))
                if nav_buttons:
                    markup.add(*nav_buttons)
                markup.add(InlineKeyboardButton("↩️ К выбору категории", callback_data="select_product"))

                await bot.send_photo(
                    chat_id=user_id,
                    photo=messages[index][0],
                    caption=messages[index][1],
                    reply_markup=markup
                )

    except Exception as e:
        stats["errors"] += 1
        logging.exception("Ошибка в callback_handler")

if __name__ == "__main__":
    import admin
    executor.start_polling(dp, skip_updates=True)
