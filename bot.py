import json
from aiogram import Bot, Dispatcher, executor, types

TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# ------------------------
# Загрузка данных
# ------------------------
def load_tasks():
    with open("tasks.json", "r", encoding="utf-8") as f:
        return json.load(f)

def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

tasks = load_tasks()


# ------------------------
# Команда /start
# ------------------------
@dp.message_handler(commands=["start"])
async def start_cmd(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)

    if user_id not in data:
        data[user_id] = {"day": 1, "progress": {}}
        save_data(data)

    await send_day(message.from_user.id)


# ------------------------
# Кнопки
# ------------------------
def day_keyboard(day):
    buttons = [
        [types.InlineKeyboardButton("✔ Выполнено", callback_data=f"done_{day}")],
        [types.InlineKeyboardButton("➖ Пропустить", callback_data=f"skip_{day}")],
        [types.InlineKeyboardButton("📊 Статистика", callback_data="stats")]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


# ------------------------
# Отправить задачи дня
# ------------------------
async def send_day(user_id):
    data = load_data()
    user = data[str(user_id)]

    day = user["day"]
    if day > 30:
        await bot.send_message(user_id, "🎉 Ты прошёл весь курс! Красавчик!")
        return

    text = f"📅 День {day}\n\n📝 Задачи:\n{tasks[str(day)]}"
    await bot.send_message(user_id, text, reply_markup=day_keyboard(day))


# ------------------------
# Обработка кнопок
# ------------------------
@dp.callback_query_handler()
async def process_callback(call: types.CallbackQuery):
    data = load_data()
    user = data[str(call.from_user.id)]
    day = user["day"]

    # Выполнено
    if call.data.startswith("done_"):
        user["progress"][str(day)] = 1
        user["day"] += 1
        save_data(data)

        await call.message.edit_text(f"День {day} — ✔ Выполнен!")
        await send_day(call.from_user.id)

    # Пропустить
    elif call.data.startswith("skip_"):
        user["progress"][str(day)] = 0
        user["day"] += 1
        save_data(data)

        await call.message.edit_text(f"День {day} — ➖ Пропущен.")
        await send_day(call.from_user.id)

    # Статистика
    elif call.data == "stats":
        await send_stats(call.from_user.id)


# ------------------------
# Простая статистика
# ------------------------
async def send_stats(user_id):
    data = load_data()
    user = data[str(user_id)]
    progress = user["progress"]

    total = len(progress)
    done = sum(progress.values())
    skipped = total - done
    percent = int((done / total) * 100) if total else 0

    text = (
        f"📊 Статистика\n\n"
        f"Всего дней прошло: {total}\n"
        f"✔ Выполнено: {done}\n"
        f"➖ Пропущено: {skipped}\n"
        f"📈 Прогресс: {percent}%"
    )

    await bot.send_message(user_id, text)


# ------------------------
# Запуск
# ------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
