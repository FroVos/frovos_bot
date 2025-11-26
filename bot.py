import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ➤ ВСТАВЬ СВОЙ ТОКЕН
TOKEN = "В8279321581:AAHyX4ji9T3FQQxocDDNM_2xWvZ3lTtIFcE"

bot = Bot(token=TOKEN)
dp = Dispatcher()

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
# Кнопки
# ------------------------
def day_keyboard(day):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✔ Выполнено", callback_data=f"done_{day}")],
        [InlineKeyboardButton(text="➖ Пропустить", callback_data=f"skip_{day}")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])


# ------------------------
# Команда /start
# ------------------------
@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    data = load_data()
    user_id = str(message.from_user.id)

    if user_id not in data:
        data[user_id] = {"day": 1, "progress": {}}
        save_data(data)

    await send_day(message.from_user.id)


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

    text = f"📅 *День {day}*\n\n📝 Задачи:\n{tasks[str(day)]}"
    await bot.send_message(user_id, text, parse_mode="Markdown", reply_markup=day_keyboard(day))


# ------------------------
# Обработка кнопок
# ------------------------
@dp.callback_query()
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
# УПРОЩЁННАЯ СТАТИСТИКА (работает на Render)
# ------------------------
async def send_stats(user_id):
    data = load_data()
    user = data[str(user_id)]
    progress = user["progress"]

    total = len(progress)
    done = sum(progress.values())
    skipped = total - done

    percent = int((done / total) * 100) if total > 0 else 0

    text = (
        f"📊 *Статистика*\n\n"
        f"Всего дней прошло: {total}\n"
        f"✔ Выполнено: {done}\n"
        f"➖ Пропущено: {skipped}\n"
        f"📈 Прогресс: {percent}%"
    )

    await bot.send_message(user_id, text, parse_mode="Markdown")


# ------------------------
# Старт бота
# ------------------------
if __name__ == "__main__":
    import asyncio
    asyncio.run(dp.start_polling(bot))
