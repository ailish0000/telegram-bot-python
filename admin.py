from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot import dp, bot, user_started, ADMIN_ID

# Состояния для FSM
class BroadcastStates(StatesGroup):
    waiting_for_text = State()

class ReplyStates(StatesGroup):
    waiting_for_message = State()

# Проверка на администратора
def is_admin(user_id: int) -> bool:
    return user_id == ADMIN_ID

# Команда /broadcast — запуск рассылки
@dp.message_handler(commands=['broadcast'])
async def cmd_broadcast(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("⛔️ Вы не администратор.")
        return
    await message.reply("Введите текст сообщения для рассылки всем пользователям:")
    await BroadcastStates.waiting_for_text.set()

# Обработка текста для рассылки
@dp.message_handler(state=BroadcastStates.waiting_for_text)
async def process_broadcast_text(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.finish()
        return

    text = message.text
    count = 0
    for user_id in user_started:
        try:
            await bot.send_message(user_id, f"📢 Рассылка от администратора:\n\n{text}")
            count += 1
        except Exception:
            pass

    await message.reply(f"✅ Рассылка отправлена {count} пользователям.")
    await state.finish()

# Команда /stats — количество пользователей
@dp.message_handler(commands=['stats'])
async def cmd_stats(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("⛔️ Вы не администратор.")
        return
    count = len(user_started)
    await message.reply(f"👥 Количество зарегистрированных пользователей: {count}")

# Команда /users — ручной выбор пользователя для ответа
@dp.message_handler(commands=['users'])
async def cmd_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return
    if not user_started:
        await message.reply("Нет зарегистрированных пользователей.")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    for uid in user_started:
        markup.add(InlineKeyboardButton(f"Пользователь {uid}", callback_data=f"reply_{uid}"))

    await message.reply("Выберите пользователя для ответа:", reply_markup=markup)

# Обработка кнопки "Ответить" (из пересланного сообщения или команды /users)
@dp.callback_query_handler(lambda c: c.data.startswith("reply_"), user_id=ADMIN_ID)
async def enter_reply_mode(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = int(callback_query.data.split("_")[-1])
    await state.update_data(reply_user_id=user_id)
    await ReplyStates.waiting_for_message.set()
    await callback_query.message.answer(f"✉️ Введите сообщение для пользователя {user_id}:")
    await bot.answer_callback_query(callback_query.id)

# Отправка ответа пользователю
@dp.message_handler(state=ReplyStates.waiting_for_message)
async def process_reply_message(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.finish()
        return
    data = await state.get_data()
    user_id = data.get('reply_user_id')
    if user_id:
        try:
            await bot.send_message(user_id, f"📩 Ответ администратора:\n\n{message.text}")
            await message.reply("✅ Сообщение отправлено пользователю.")
        except Exception:
            await message.reply("❌ Ошибка при отправке сообщения пользователю.")
    else:
        await message.reply("⚠️ Пользователь не найден.")
    await state.finish()
