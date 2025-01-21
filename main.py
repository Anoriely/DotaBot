import os
import random
import json
import re
import logging
from flask import Flask, request
from telebot import TeleBot, types
from datetime import datetime, timezone, timedelta
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Константы
TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
FILE_PATH = "user_data.json"
DOTA_APP_ID = 570
STEAM_ID_PATTERN = re.compile(r"^\d{17}$")

# Инициализация данных
if os.path.exists(FILE_PATH):
    try:
        with open(FILE_PATH, 'r') as f:
            user_data = json.load(f)
    except json.JSONDecodeError:
        logger.warning("Ошибка чтения JSON файла. Использую пустую структуру.")
        user_data = {}
else:
    logger.warning(f"Файл {FILE_PATH} не найден. Использую пустую структуру.")
    user_data = {}

USER_STEAM_IDS = user_data.get("user_mappings", {})
BOSS_USER_ID = user_data.get("boss_user", None)
SPECIAL_USER_IDS = user_data.get("special_users", [])
STEAM_ID_TOEXTEND = user_data.get("steam_id_toextend", None)
PING_LIST = user_data.get("ping_list", [])

# Инициализация бота и Flask
bot = TeleBot(TOKEN)
app = Flask(__name__)

# Время старта бота
bot_start_time = datetime.now(timezone.utc)

# Общие функции

def save_user_data():
    #Сохраняет данные в JSON файл.
    with open(FILE_PATH, 'w') as f:
        json.dump(user_data, f, indent=4, ensure_ascii=False)


def is_recent_message(message):
    #Проверяет, является ли сообщение недавним.
    return message.date >= (bot_start_time - timedelta(minutes=5)).timestamp()


# Команды бота
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(message, "Привет! Я бот для игр и статистики.")


@bot.message_handler(commands=['slot'])
def slot_machine(message):
    if not is_recent_message(message):
        return

    fruits = ['🍎', '🍊', '🍋', '🍒', '🍇', '🍉', '🍓']
    row1, row2, row3 = [random.choices(fruits, k=3) for _ in range(3)]

    is_win = (
        row1[0] == row1[1] == row1[2] or
        row2[0] == row2[1] == row2[2] or
        row3[0] == row3[1] == row3[2] or
        row1[0] == row2[1] == row3[2] or
        row1[2] == row2[1] == row3[0]
    )

    result = f"{row1[0]} | {row1[1]} | {row1[2]}\n" \
             f"{row2[0]} | {row2[1]} | {row2[2]}\n" \
             f"{row3[0]} | {row3[1]} | {row3[2]}"

    message_text = "🎉 Вы выиграли! 🎉" if is_win else "😢 Попробуйте еще раз!"
    bot.reply_to(message, f"🎰 Результат:\n{result}\n{message_text}")


@bot.message_handler(commands=['howgay'])
def how_gay(message):
    if not is_recent_message(message):
        return

    if str(message.from_user.id) == str(BOSS_USER_ID):
        percentage = 0
    else:
        percentage = random.randint(50, 100)

    bot.reply_to(message, f"Ты гей на {percentage}% 🌈")


@bot.message_handler(commands=['info'])
def info(message):
    if not is_recent_message(message):
        return

    bot.reply_to(message, "Я бот для игр, статистики и веселья. Исходный код: https://github.com/Anoriely/DotaBot")


@bot.message_handler(commands=['pingdota'])
def ping_users(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Эта команда недоступна в личном чате.")
        return

    if not is_recent_message(message):
        return

    mention_text = "Эй, Тузы, время в Доту!\n" + "\n".join([
        f"[{user['first_name']}](tg://user?id={user['id']})" for user in PING_LIST
    ])

    bot.reply_to(message, mention_text, parse_mode="Markdown")


@bot.message_handler(commands=['regsteam'])
def register_steam_id(message):
    if not is_recent_message(message):
        return

    try:
        steam_id = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Укажите Steam ID после команды. Пример: /regsteam 76561198123456789")
        return

    if not STEAM_ID_PATTERN.match(steam_id):
        bot.reply_to(message, "Неверный формат Steam ID. Попробуйте еще раз.")
        return

    user_id = str(message.from_user.id)
    if steam_id in USER_STEAM_IDS.values():
        bot.reply_to(message, "Этот Steam ID уже привязан к другому пользователю.")
        return

    USER_STEAM_IDS[user_id] = steam_id
    user_data["user_mappings"] = USER_STEAM_IDS
    save_user_data()

    bot.reply_to(message, f"Ваш Steam ID: {steam_id} успешно привязан!")


@bot.message_handler(commands=['time_dota'])
def get_dota2_playtime_command(message):
    if not is_recent_message(message):
        logger.info("Сообщение старше 5 минут, игнорируем.")
        return

    user_id = str(message.from_user.id)
    steam_id = USER_STEAM_IDS.get(user_id)

    if not steam_id:
        bot.reply_to(message, "Ваш Steam ID не привязан. Используйте /regsteam.")
        logger.info(f"Пользователь {user_id} запросил данные без привязанного Steam ID.")
        return

    try:
        payload = {
            "steamid": steam_id,
            "appids_filter": [DOTA_APP_ID],
            "include_played_free_games": True
        }
        url = (f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
               f"?key={STEAM_API_KEY}&format=json&input_json={json.dumps(payload)}")
        logger.info(f"Отправка запроса к Steam API: {url}")
        response = requests.get(url)

        if response.status_code != 200:
            logger.error(f"Ошибка HTTP {response.status_code} при запросе к Steam API: {response.text}")
            bot.reply_to(message, "Ошибка подключения к Steam API. Попробуйте позже.")
            return

        response_data = response.json()
        logger.debug(f"Ответ от Steam API: {response_data}")

        games = response_data.get("response", {}).get("games", [])
        dota2 = next((game for game in games if game["appid"] == DOTA_APP_ID), None)

        if dota2:
            hours = dota2.get("playtime_forever", 0) // 60
            logger.info(f"Пользователь {user_id} сыграл в Dota 2 {hours} часов.")
            bot.reply_to(message, f"Вы сыграли в Dota 2: {hours} часов.")
        else:
            logger.info(f"Dota 2 не найдена в библиотеке пользователя {user_id}.")
            bot.reply_to(message, "Вы не играли в Dota 2 или профиль скрыт.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка подключения к Steam API: {e}")
        bot.reply_to(message, "Ошибка подключения к Steam API. Попробуйте позже.")

    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")
        bot.reply_to(message, "Не удалось получить данные. Попробуйте позже.")



# Webhook маршруты
@app.route(f"/{TOKEN}", methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return 'OK', 200

@app.route('/')
def index():
    return 'Webhook is active!', 200

if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
