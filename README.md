# DotaBot — Telegram Bot for Boys 🎮🌈

![DotaBot](https://img.shields.io/badge/DotaBot-v1.0-blue) ![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)

## Функциональные возможности

- **Команда `/slot`**: Поиграйте в слоты с ботом и попробуйте поймать выигрышную комбинацию! 🎰
- **Команда `/howgay`**: Узнайте, насколько вы гей! 🌈
- **Команда `/pingdota`**: Пригласите своих друзей из группы в Dota 2! 🌈
- **Команда `/time_dota`**: Получите информацию о времени, проведенном в Dota 2, для привязанного аккаунта Steam.
- **Команда `/top_dota`**: Посмотрите список игроков в группе и их общее время в Dota 2 в порядке убывания.
- **Команда `/regsteam`**: Привяжите свой Steam ID к вашему аккаунту Telegram, чтобы бот мог отслеживать ваше время в игре!
- **Команда `/info`**: Ссылка на github.

## Установка

Поднимается в вирутальном окружении 🐍 **Python**:
```
python3 -m venv venv
source venv/bin/activate
```

Используется **aiogram**:
```
Name: aiogram
Version: 3.13.1
Summary: Modern and fully asynchronous framework for Telegram Bot API
```


### 1. Переменные окружения и данные

Основная информация помещается в файлы **.env** и **user_data.json**.
Файлы структурированы так:
```
.env

API_TOKEN=
STEAM_API_KEY=
USER_DATA_FILE=user_data.json
```

```json
{
    "user_mappings": {
        "tg_ID": "steamID"
        ...
    },
    "special_users": [],
    "boss_user": "",
    "steam_id_toextend": "",
    "ping_list": [
        {
            "id": ,
            "first_name": ""
        }
        ...
    ]
  }
  
```

### 2. dotaBot (venv)

В репозитории содержится папка с уже созданным виртуальным окружением, где установлены все необходимые зависимости.

```
aiofiles==24.1.0
aiogram==3.13.1
aiohappyeyeballs==2.4.3
aiohttp==3.10.9
aiosignal==1.3.1
annotated-types==0.7.0
anyio==4.6.0
attrs==24.2.0
certifi==2024.8.30
charset-normalizer==3.3.2
frozenlist==1.4.1
h11==0.14.0
httpcore==1.0.6
httpx==0.27.2
idna==3.10
magic-filter==1.0.12
multidict==6.1.0
pydantic==2.9.2
pydantic_core==2.23.4
python-dotenv==1.0.1
python-telegram-bot==21.6
requests==2.32.3
sniffio==1.3.1
telegram==0.0.1
typing_extensions==4.12.2
urllib3==2.2.3
yarl==1.13.1
```
### 3. TODO

Много чего...

<div id="header" align="center">
  <img src="https://media.giphy.com/media/M9gbBd9nbDrOTu1Mqx/giphy.gif" width="100"/>
</div>