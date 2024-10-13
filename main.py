import logging
import os
import random
import telebot
import json
import re
import requests

from datetime import datetime, timezone, timedelta
from flask import Flask, request
from telebot import types


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")

file_path = "/app/user_data.json"

# Проверяем, существует ли файл, прежде чем пытаться его открыть
if os.path.exists(file_path):
    with open(file_path, 'r') as f:
        try:
            user_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error reading JSON file: {e}")
else:
    print(f"File {file_path} does not exist")


USER_STEAM_IDS = user_data["user_mappings"]
BOSS_USER_ID = user_data["boss_user"]
SPECIAL_USER_IDS = user_data["special_users"]
STEAM_ID_TOEXTEND = user_data["steam_id_toextend"]
PING_LIST = user_data["ping_list"]
STEAM_ID_PATTERN = re.compile(r"^\d{17}$")
DOTA_APP_ID = 570

bot = telebot.TeleBot(TOKEN)

# Инициализация Flask-приложения
app = Flask(__name__)

bot_start_time = datetime.now(timezone.utc)

# Обработка команды /start
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Hello! Local Test.")

# Список эмодзи фруктов для слота
FRUITS = ['🍎', '🍊', '🍋', '🍒', '🍇', '🍉', '🍓']

# Функция для генерации результата слота
def spin_slots(mode):
    if mode == 1:
        # С повышенным шансом генерируем выигрышную комбинацию
        if random.random() < 0.8:
            fruit = random.choice(FRUITS)  # Выбираем случайный фрукт
            row1 = random.choices(FRUITS, k=3)
            row2 = [fruit, fruit, fruit]
            row3 = random.choices(FRUITS, k=3)
        else:
            # В остальных случаях генерируем случайную комбинацию
            row1 = random.choices(FRUITS, k=3)
            row2 = random.choices(FRUITS, k=3)
            row3 = random.choices(FRUITS, k=3)
    else:
        # Для обычных пользователей генерируем случайную комбинацию
        row1 = random.choices(FRUITS, k=3)
        row2 = random.choices(FRUITS, k=3)
        row3 = random.choices(FRUITS, k=3)

    # Формирование результата
    slot_result = f"{row1[0]} | {row1[1]} | {row1[2]}\n" \
                  f"{row2[0]} | {row2[1]} | {row2[2]}\n" \
                  f"{row3[0]} | {row3[1]} | {row3[2]}"

    is_win = (
            # Проверка горизонтальных линий
            row1[0] == row1[1] == row1[2] or  # Верхняя линия
            row2[0] == row2[1] == row2[2] or  # Средняя линия
            row3[0] == row3[1] == row3[2] or  # Нижняя линия

            # Проверка диагональных линий
            row1[0] == row2[1] == row3[2] or  # Главная диагональ
            row1[2] == row2[1] == row3[0]     # Обратная диагональ
        )

    # Проверка, есть ли выигрыш (например, три одинаковых в средней линии)
    if is_win:
        win_message = "🎉 Поздравляем! Вы выиграли! 🎉"
    else:
        win_message = "К сожалению, вы не выиграли. Попробуйте еще раз!"

    return slot_result, win_message

@bot.message_handler(commands=['slot'])
def slot_machine(message):
    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    if SPECIAL_USER_IDS and message.from_user.id in SPECIAL_USER_IDS:
        result, win_message = spin_slots(1)
    else:
        result, win_message = spin_slots(0)

    bot.reply_to(message, f"🎰 Турик-слоты 🎰\n\n{result}\n\n{win_message}")
    logger.info(f"Пользователь {message.from_user.id} запустил слот-машину.")

@bot.message_handler(commands=['howgay'])
def how_gay(message):
    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    if str(message.from_user.id) == str(BOSS_USER_ID):
          gay_percentage = 0
    else:
          gay_percentage = random.randint(50, 100)

    response = f"Ты гей на {gay_percentage}% 🌈"
    bot.reply_to(message, response)

@bot.message_handler(commands=['info'])
def info(message):
    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    response = f"Хочешь узнать как я работаю? 🤖\nВся информация тут - https://github.com/Anoriely/DotaBot"
    bot.reply_to(message, response)

@bot.message_handler(commands=['pingdota'])
def ping_users(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Эта команда недоступна в личном чате.")
        return

    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    mention_text = "Эй, Тузы, время жестко подолбиться в доте 🌈:\n"
    for user in PING_LIST:
        # Упоминание каждого пользователя по его ID и имени
        mention_text += f"[{user['first_name']}](tg://user?id={user['id']})\n"

    # Отправка сообщения в чат
    bot.reply_to(message, mention_text, parse_mode="Markdown")

@bot.message_handler(commands=['regsteam'])
def register_steam_id(message):
    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    user_telegram_id = str(message.from_user.id)

    try:
        steam_id = message.text.split()[1]
    except IndexError:
        bot.reply_to(message, "Хочешь показать всем насколько пробит твой туз? Правильное решение!\nДля этого нужно привязать свой steamID64 к Telegram.\nSteamID64 можно узнать используя сайт https://steamid.io/, указав ссылку на свой профиль. Потом используй команду /regsteam.\nПример: /regsteam 76561198197419761")
        return

    # Проверка, что переданный Steam ID соответствует формату 17 цифр
    if not STEAM_ID_PATTERN.match(steam_id):
        bot.reply_to(message, "Неправильный формат Steam ID. Steam ID должен состоять из 17 цифр.")
        return

    # Проверка, что переданный Steam ID не привязан к другому пользователю
    for tg_id, existing_steam_id in USER_STEAM_IDS.items():
        if existing_steam_id == steam_id:
            bot.reply_to(message, f"Этот Steam ID уже привязан к другому пользователю с Telegram ID: {tg_id}.\nНе жульничай!")
            return

    # Проверка, есть ли у текущего пользователя уже привязанный Steam ID
    if user_telegram_id in USER_STEAM_IDS:
        bot.reply_to(message, f"Твой аккаунт уже привязан к Steam ID: {USER_STEAM_IDS[user_telegram_id]}.\nЕсли хочешь привязать другой steamID, то обратись к моему создателю.")
        return

    # Привязка нового Steam ID к Telegram ID пользователя
    USER_STEAM_IDS[user_telegram_id] = steam_id

    # Обновление данных в JSON-файле
    user_data["user_mappings"] = USER_STEAM_IDS
    try:
            with open(file_path, 'w') as f:
                json.dump(user_data, f, indent=4, ensure_ascii=False)
                logger.info(f"Данные успешно записаны в {file_path}")
    except Exception as e:
            logger.info(f"Ошибка записи в файл {file_path}: {e}")

    # Уведомление пользователя об успешной привязке
    bot.reply_to(message, f"Твой Steam ID: {steam_id} успешно привязан к твоему Telegram ID: {user_telegram_id}.")

# Функция для получения времени в Dota 2 для определенного Steam ID
def get_dota2_playtime(steam_id) -> int:
    # URL для запроса времени в игре Dota 2
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&format=json&input_json={{\"steamid\":{steam_id},\"appids_filter\":[{DOTA_APP_ID}],\"include_played_free_games\":true}}"

    try:
        response = requests.get(url)
        # Проверка успешности запроса
        if response.status_code != 200:
            logger.error(f"Ошибка при запросе к Steam API: {response.status_code}")
            return 0

        data = response.json()

        # Проверяем, содержит ли ответ данные об играх и что в нем есть список игр
        if "response" in data and "games" in data["response"] and isinstance(data["response"]["games"], list) and len(data["response"]["games"]) > 0:
            # Предполагаем, что запрос возвращает только одну игру — Dota 2
            dota2_game = data["response"]["games"][0]

            # Получаем общее время в Dota 2 в минутах
            dota2_playtime_minutes = dota2_game.get('playtime_forever', 0)
            dota2_playtime_hours = dota2_playtime_minutes // 60

            if steam_id == STEAM_ID_TOEXTEND:
                dota2_playtime_hours += 1555

            return dota2_playtime_hours


        else:
            logger.warning(f"Некорректный формат данных в ответе для SteamID {steam_id}.")
                   # Если данные об играх не найдены, возвращаем 0
        return 0

    except Exception as e:
        print(f"Ошибка при получении данных для SteamID {steam_id}: {e}")
        return 0

@bot.message_handler(commands=['time_dota'])
def get_dota2_playtime_command(message):
     if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
         logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
         return  # Игнорируем сообщение, если оно отправлено до старта бота

     user_telegram_id = message.from_user.id

     if str(user_telegram_id).strip() not in USER_STEAM_IDS.keys():
         bot.reply_to(message, "Твой Telegram ID не связан с каким-либо SteamID в базе.\n Попробуй сначала /regsteam!")
         return

    # Получаем Steam ID пользователя из словаря
     steam_id = USER_STEAM_IDS.get(str(user_telegram_id).strip(), None)
     dota2_playtime_hours = get_dota2_playtime(steam_id)

    # Если пользователь не играл в Dota 2 или профиль скрыт
     if dota2_playtime_hours == 0:
        bot.reply_to(message, "Похоже, что вы не играли в Dota 2, или твой профиль скрыт.")
     else:
        # Отправляем сообщение с временем в игре
         bot.reply_to(message, f"Твое общее время в Dota 2: {dota2_playtime_hours} часов.")

# Команда для отображения общего времени всех пользователей в порядке убывания
@bot.message_handler(commands=['top_dota'])
def show_top_dota2_playtime(message):
    if message.chat.type == "private":
        bot.reply_to(message, "Эта команда недоступна в личном чате.")
        return

    if message.date < (bot_start_time - timedelta(minutes=5)).timestamp():
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    playtime_list = []

    # Перебираем всех пользователей из списка USER_STEAM_IDS
    for telegram_id, steam_id in USER_STEAM_IDS.items():
        try:

            chat_member = bot.get_chat_member(message.chat.id, telegram_id)
            if chat_member.status in ["member", "administrator", "creator"]:
             playtime_hours = get_dota2_playtime(steam_id)

            playtime_list.append((telegram_id, playtime_hours))
        except Exception as e:
            logger.warning(f"Не удалось получить информацию о пользователе {telegram_id} в чате {message.chat.id}: {e}")
            continue

    # Сортируем список по количеству часов в убывающем порядке
    playtime_list.sort(key=lambda x: x[1], reverse=True)
    total_participants = 0

    # Формирование итогового сообщения
    result_message = "🌈 Топ <b>пробитых тузов</b> по времени в Dota 2:\n\n"
    for index, (telegram_id, hours) in enumerate(playtime_list, start=1):
        try:
            member = bot.get_chat_member(message.chat.id, telegram_id)
            if member.user.username:
                user_tag = f"{member.user.username}"
            else:
                user_tag = f"{member.user.full_name}"  # Если нет username, используем ID

        except telebot.apihelper.ApiTelegramException as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                user_tag = f"Пользователь ({telegram_id}) недоступен в этом чате"
            else:
                user_tag = f"Неизвестный пользователь ({telegram_id})"

        # Добавляем информацию в сообщение
        result_message += f"<b>{index}</b>. {user_tag} — {hours} часов\n"
        total_participants += 1

    result_message += f"\nВсего пробитых тузов — {total_participants}"

    # Отправляем сообщение в чат
    bot.reply_to(message, result_message, parse_mode="HTML")


# Маршрут для получения обновлений от Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '!', 200

# Маршрут для проверки работы
@app.route('/')
def index():
    return 'Webhook is set', 200

if __name__ == '__main__':
    bot.set_my_commands([
           types.BotCommand(command="/slot", description="Покрутить слоты 🎰"),
           types.BotCommand(command="/howgay", description="Узнай насколько ты гей 🌈"),
           types.BotCommand(command="/pingdota", description="Позови Тузевичей в Доту! 🌈"),
           types.BotCommand(command="/time_dota", description="Узнай сколько часов у тебя в доте!"),
           types.BotCommand(command="/top_dota", description="Топ пробитых тузов!"),
           types.BotCommand(command="/regsteam", description="Покажи всем насколько ты пробит!"),
           types.BotCommand(command="/info", description="Все обо мне")
       ])
    # Установим вебхук
    WEBHOOK_URL = f"{WEBHOOK_URL}/{TOKEN}"
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    # Запуск приложения
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
