import os
import asyncio
import sqlite3
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

DB_PATH = "bot.db"

# --- Работа с базой ---

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        username TEXT,
        message TEXT,
        is_answered INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()

def add_user(user_id: int, username: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users(user_id, username) VALUES (?, ?)", (user_id, username))
    conn.commit()
    conn.close()

def add_message(user_id: int, username: str, message: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages(user_id, username, message, is_answered) VALUES (?, ?, ?, 0)", (user_id, username, message))
    conn.commit()
    conn.close()

def get_user_count():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    conn.close()
    return count

def get_unanswered_messages(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, user_id, username, message FROM messages WHERE is_answered=0 ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def mark_message_answered(message_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE messages SET is_answered=1 WHERE id=?", (message_id,))
    conn.commit()
    conn.close()

# --- FSM для рассылки и ответа ---

class BroadcastStates(StatesGroup):
    waiting_for_text = State()

class ReplyStates(StatesGroup):
    waiting_for_reply = State()

# --- Клавиатуры ---

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

def admin_menu():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        InlineKeyboardButton("💬 Обращения", callback_data="admin_requests"),
        InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast_start"),
        InlineKeyboardButton("❌ Выйти из админки", callback_data="admin_logout")
    )
    return markup

def message_keyboard(message_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("Ответить", callback_data=f"reply_{message_id}"),
        InlineKeyboardButton("Отметить как прочитано", callback_data=f"markread_{message_id}")
    )
    return markup

# --- Хендлеры ---

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    add_user(user_id, username)
    await message.answer("Привет! Это стартовое сообщение.", reply_markup=main_menu())

@dp.message_handler(commands=["admin"])
async def cmd_admin(message: types.Message):
    user_id = message.from_user.id
    if user_id == ADMIN_ID:
        await message.answer("Добро пожаловать в админ-панель:", reply_markup=admin_menu())
    else:
        await message.answer("У вас нет доступа к админ-панели.")

@dp.callback_query_handler(lambda c: c.data)
async def callbacks_handler(callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id

    if user_id != ADMIN_ID and data.startswith("admin_"):
        await callback_query.answer("У вас нет доступа.", show_alert=True)
        return

    if data == "admin_stats":
        count = get_user_count()
        await callback_query.message.answer(f"Количество пользователей: {count}")
    elif data == "admin_requests":
        messages = get_unanswered_messages()
        if not messages:
            await callback_query.message.answer("Нет новых обращений.")
        else:
            for msg_id, u_id, username, text in messages:
                await callback_query.message.answer(
                    f"Сообщение от @{username} (ID: {u_id}):\n\n{text}",
                    reply_markup=message_keyboard(msg_id)
                )
    elif data == "admin_broadcast_start":
        await callback_query.message.answer("Введите текст рассылки:")
        await BroadcastStates.waiting_for_text.set()
    elif data == "admin_logout":
        await callback_query.message.answer("Вы вышли из админ-панели.")
        await callback_query.message.edit_reply_markup(reply_markup=None)
    elif data.startswith("reply_"):
        msg_id = int(data.split("_")[1])
        await callback_query.message.answer("Введите ответ пользователю:")
        await ReplyStates.waiting_for_reply.set()
        # Сохраним id сообщения в FSM context
        state = dp.current_state(user=user_id)
        await state.update_data(reply_message_id=msg_id)
    elif data.startswith("markread_"):
        msg_id = int(data.split("_")[1])
        mark_message_answered(msg_id)
        await callback_query.message.answer("Отмечено как прочитано.")
        await callback_query.message.delete()
    else:
        # Обработка основного меню, как в твоём коде
        if data == "select_product":
            await callback_query.message.answer("Вы выбрали подборку продуктов.")
        elif data == "ask_question":
            await callback_query.message.answer("Напишите ваш вопрос в чат.")
        elif data == "catalog":
            await callback_query.message.answer("Ссылка на каталог: https://aur-ora.com/catalog/vse_produkty")
        elif data == "check_city":
            await callback_query.message.answer("Выберите город (список будет позже).")
        elif data == "report_error":
            await callback_query.message.answer("Опишите ошибку подробно.")
    await callback_query.answer()

@dp.message_handler(lambda message: message.text and not message.text.startswith("/"))
async def handle_user_message(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    text = message.text
    add_user(user_id, username)
    add_message(user_id, username, text)
    await message.reply("✅ Ваше сообщение отправлено. Ожидайте ответа.")

# Обработка рассылки (админ)
@dp.message_handler(state=BroadcastStates.waiting_for_text)
async def process_broadcast(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.reply("У вас нет доступа.")
        await state.finish()
        return

    text = message.text
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    conn.close()

    sent = 0
    for (uid,) in users:
        try:
            await bot.send_message(uid, f"📢 Рассылка от Админа:\n\n{text}")
            sent += 1
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Ошибка при отправке {uid}: {e}")

    await message.answer(f"Рассылка завершена. Отправлено сообщений: {sent}")
    await state.finish()

# Обработка ответа админа на сообщение пользователя
@dp.message_handler(state=ReplyStates.waiting_for_reply)
async def process_reply(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != ADMIN_ID:
        await message.reply("У вас нет доступа.")
        await state.finish()
        return

    data = await state.get_data()
    msg_id = data.get("reply_message_id")
    reply_text = message.text

    # Получаем ID пользователя, которому отвечаем
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM messages WHERE id=?", (msg_id,))
    row = cursor.fetchone()
    conn.close()

    if row:
        target_user_id = row[0]
        try:
            await bot.send_message(target_user_id, f"Ответ от Администратора:\n\n{reply_text}")
            mark_message_answered(msg_id)
            await message.answer("Ответ отправлен пользователю.")
        except Exception as e:
            await message.answer(f"Ошибка при отправке: {e}")
    else:
        await message.answer("Сообщение не найдено.")

    await state.finish()

# --- Инициализация базы и запуск ---

if __name__ == "__main__":
    init_db()
    print("Бот запущен")
    executor.start_polling(dp, skip_updates=True)

