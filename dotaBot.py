import requests
import logging
import random
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from datetime import datetime, timezone
from dotenv import load_dotenv
import os
import json
import re


# Логирование ошибок и событий
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

bot_start_time = datetime.now(timezone.utc)

load_dotenv()
API_TOKEN = os.getenv("API_TOKEN")
STEAM_API_KEY = os.getenv("STEAM_API_KEY")
USER_DATA_FILE = os.getenv("USER_DATA_FILE")

with open(USER_DATA_FILE, "r") as user_data_file:
    user_data = json.load(user_data_file)

USER_STEAM_IDS = user_data["user_mappings"]
BOSS_USER_ID = user_data["boss_user"]
SPECIAL_USER_IDS = user_data["special_users"]
STEAM_ID_TOEXTEND = user_data["steam_id_toextend"]
PING_LIST = user_data["ping_list"]

STEAM_ID_PATTERN = re.compile(r"^\d{17}$")

DOTA_APP_ID = 570

bot = Bot(token=API_TOKEN)
dp = Dispatcher()





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



# Обработчик команды /slot
@dp.message(Command(commands=['slot']))
async def slot_machine(message: types.Message):

    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    if message.from_user.id in SPECIAL_USER_IDS:      
        result, win_message = spin_slots(1)
    else:
        result, win_message = spin_slots(0)

    # Отправка результата пользователю
    await message.reply(f"🎰 Турик-слоты 🎰\n\n{result}\n\n{win_message}")

    # Логирование результата
    logger.info(f"Пользователь {message.from_user.id} запустил слот-машину.")

@dp.message(Command(commands=['howgay']))
async def how_cool(message: types.Message):
    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота
    
    if message.from_user.id == BOSS_USER_ID:
          gay_percentage = 0
    else:
          # Генерация случайного значения от 50% до 100% для остальных пользователей
          gay_percentage = random.randint(50, 100)    
    # Отправка сообщения пользователю
    response = f"Ты гей на {gay_percentage}% 🌈"
    await message.reply(response)

@dp.message(Command(commands=['info']))
async def info(message: types.Message):
    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота
    
    response = f"Хочешь узнать как я работаю? 🤖\nВся информация тут - https://github.com/Anoriely/DotaBot"
    await message.reply(response)

@dp.message(Command(commands=['pingdota']))
async def ping_users(message: types.Message):
    if message.chat.type == "private":
        await message.reply("Эта команда недоступна в личном чате.")
        return 
    
    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота
    
    mention_text = "Эй, Тузы, время жестко подолбиться в доте 🌈:\n"
    for user in PING_LIST:
        # Упоминание каждого пользователя по его ID и имени
        mention_text += f"[{user['first_name']}](tg://user?id={user['id']})\n"

    # Отправка сообщения в чат
    await message.reply(mention_text, parse_mode="Markdown")






@dp.message(Command(commands=['regsteam']))
async def register_steam_id(message: types.Message):
    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота
    
    # Получаем ID пользователя Telegram
    user_telegram_id = str(message.from_user.id)

    try:
        steam_id = message.text.split()[1]  
    except IndexError:
        await message.reply("Хочешь показать всем насколько пробит твой туз? Правильное решение!\nДля этого нужно привязать свой steamID64 к Telegram.\nSteamID64 можно узнать используя сайт https://steamid.io/, указав ссылку на свой профиль. Потом используй команду /regsteam.\nПример: /regsteam 76561198197419761")
        return

    # Проверка, что переданный Steam ID соответствует формату 17 цифр
    if not STEAM_ID_PATTERN.match(steam_id):
        await message.reply("Неправильный формат Steam ID. Steam ID должен состоять из 17 цифр.")
        return

    # Проверка, что переданный Steam ID не привязан к другому пользователю
    for tg_id, existing_steam_id in USER_STEAM_IDS.items():
        if existing_steam_id == steam_id:
            await message.reply(f"Этот Steam ID уже привязан к другому пользователю с Telegram ID: {tg_id}.\nНе жульничай!")
            return

    # Проверка, есть ли у текущего пользователя уже привязанный Steam ID
    if user_telegram_id in USER_STEAM_IDS:
        await message.reply(f"Твой аккаунт уже привязан к Steam ID: {USER_STEAM_IDS[user_telegram_id]}.\nЕсли хочешь привязать другой steamID, то обратись к моему создателю.")
        return

    # Привязка нового Steam ID к Telegram ID пользователя
    USER_STEAM_IDS[user_telegram_id] = steam_id

    # Обновление данных в JSON-файле
    user_data["user_mappings"] = USER_STEAM_IDS
    with open(USER_DATA_FILE, "w", encoding='utf-8') as user_data_file:
        json.dump(user_data, user_data_file, ensure_ascii=False, indent=4)

    # Уведомление пользователя об успешной привязке
    await message.reply(f"Твой Steam ID: {steam_id} успешно привязан к твоему Telegram ID: {user_telegram_id}.")


# Функция для получения времени в Dota 2 для определенного Steam ID
def get_dota2_playtime(steam_id) -> int:
    # URL для запроса времени в игре Dota 2
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={STEAM_API_KEY}&format=json&input_json={{\"steamid\":{steam_id},\"appids_filter\":[{DOTA_APP_ID}],\"include_played_free_games\":true}}"

    try:
        response = requests.get(url)
        data = response.json()

        # Проверяем, содержит ли ответ данные об играх и что в нем есть список игр
        if "response" in data and "games" in data["response"] and isinstance(data["response"]["games"], list) and len(data["response"]["games"]) > 0:
            # Предполагаем, что запрос возвращает только одну игру — Dota 2
            dota2_game = data["response"]["games"][0]
                    
            # Получаем общее время в Dota 2 в минутах
            dota2_playtime_minutes = dota2_game.get('playtime_forever', 0)

                    # Переводим в часы
            dota2_playtime_hours = dota2_playtime_minutes // 60

            if steam_id == STEAM_ID_TOEXTEND:  
                dota2_playtime_hours += 1555  

            return dota2_playtime_hours

        # Если данные об играх не найдены, возвращаем 0
        return 0
    except Exception as e:
        print(f"Ошибка при получении данных для SteamID {steam_id}: {e}")
        return 0

@dp.message(Command(commands=['time_dota']))
async def get_dota2_playtime_handler(message: types.Message):
    
    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота

    user_telegram_id = str(message.from_user.id)

    if user_telegram_id not in USER_STEAM_IDS:
        await message.reply("Твой Telegram ID не связан с каким-либо SteamID в базе.\n Попробуй сначала /regsteam!")
        return

    # Получаем Steam ID пользователя из словаря
    steam_id = USER_STEAM_IDS[user_telegram_id]

    dota2_playtime_hours = get_dota2_playtime(steam_id)

    # Если пользователь не играл в Dota 2 или профиль скрыт
    if dota2_playtime_hours == 0:
        await message.reply("Похоже, что вы не играли в Dota 2, или твой профиль скрыт.")
    else:
        # Отправляем сообщение с временем в игре
        await message.reply(f"Твое общее время в Dota 2: {dota2_playtime_hours} часов.")


# Команда для отображения общего времени всех пользователей в порядке убывания
@dp.message(Command(commands=['top_dota']))
async def show_top_dota2_playtime(message: types.Message):
    if message.chat.type == "private":
        await message.reply("Эта команда недоступна в личном чате.")
        return 

    if message.date < bot_start_time:
        logger.info(f"Сообщение от {message.from_user.id} проигнорировано (старое сообщение).")
        return  # Игнорируем сообщение, если оно отправлено до старта бота
    
    playtime_list = []

    # Перебираем всех пользователей из списка USER_STEAM_IDS
    for telegram_id, steam_id in USER_STEAM_IDS.items():
        # Получаем время, проведенное в Dota 2, для каждого Steam ID
        playtime_hours = get_dota2_playtime(steam_id)

        # Добавляем данные в список
        playtime_list.append((telegram_id, playtime_hours))

    # Сортируем список по количеству часов в убывающем порядке
    playtime_list.sort(key=lambda x: x[1], reverse=True)
    total_participants = 0
    
    # Формирование итогового сообщения
    result_message = "🌈 Топ <b>пробитых тузов</b> по времени в Dota 2:\n\n"
    for index, (telegram_id, hours) in enumerate(playtime_list, start=1):
        try:
            member = await bot.get_chat_member(message.chat.id, telegram_id)
                # Используем username, если он доступен
            if member.user.username:
                user_tag = f"{member.user.username}"
            else:
                user_tag = f"{member.user.full_name}"  # Если нет username, используем ID

        except exceptions.TelegramBadRequest as e:
            if "PARTICIPANT_ID_INVALID" in str(e):
                user_tag = f"Пользователь ({telegram_id}) недоступен в этом чате"
            else:
                user_tag = f"Неизвестный пользователь ({telegram_id})"
        
        # Добавляем информацию в сообщение
        result_message += f"<b>{index}</b>. {user_tag} — {hours} часов\n"
        total_participants += 1
   

    result_message += f"\nВсего пробитых тузов — {total_participants}"

    # Отправляем сообщение в чат
    await message.reply(result_message, parse_mode="HTML")


# Основная функция для запуска бота
async def main():
    # Устанавливаем команды бота (опционально)
    await bot.set_my_commands([
        types.BotCommand(command="/slot", description="Покрутить слоты 🎰"),
        types.BotCommand(command="/howgay", description="Узнай насколько ты гей 🌈"),
        types.BotCommand(command="/pingdota", description="Позови Тузевичей в Доту! 🌈"),
       # types.BotCommand(command="/members", description="dev tool"),
        types.BotCommand(command="/time_dota", description="Узнай сколько часов у тебя в доте!"),
        types.BotCommand(command="/top_dota", description="Топ пробитых тузов!"),
        types.BotCommand(command="/regsteam", description="Покажи всем насколько ты пробит!"),
        types.BotCommand(command="/info", description="Все обо мне")
    ])

    # Запуск поллинга
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен вручную.")
