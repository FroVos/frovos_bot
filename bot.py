import json
import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import matplotlib.pyplot as plt

TOKEN = "8279321581:AAHyX4ji9T3FQQxocDDNM_2xWvZ3lTtIFcE"

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
        await bot.send_message(user_id, "🎉 Ты прошёл весь курс! Поздравляю!")
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
    if call.data.startswith("skip_"):
        user["progress"][str(day)] = 0
        user["day"] += 1
        save_data(data)

        await call.message.edit_text(f"День {day} — ➖ Пропущен.")
        await send_day(call.from_user.id)

    # Статистика
    if call.data == "stats":
        await send_stats(call.from_user.id)


# ------------------------
# Генерация графика прогресса
# ------------------------
async def send_stats(user_id):
    data = load_data()
    user = data[str(user_id)]
    progress = user["progress"]

    days = list(range(1, len(progress) + 1))
    values = [progress.get(str(d), 0) for d in days]

    if not days:
        await bot.send_message(user_id, "Пока статистики нет 🙃")
        return

    plt.figure(figsize=(8, 4))
    plt.plot(days, values, marker="o")
    plt.title("Прогресс обучения (1=выполнено, 0=нет)")
    plt.xlabel("Дни")
    plt.ylabel("Прогресс")
    plt.grid(True)
    plt.savefig("progress.png")
    plt.close()

    await bot.send_photo(user_id, photo=open("progress.png", "rb"))


# ------------------------
# Старт бота
# -------------------
