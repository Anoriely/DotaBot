# DotaBot — Telegram Bot for Boys 🎮🌈

![DotaBot](https://img.shields.io/badge/DotaBot-v2.0-blue) ![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen)

## Функциональные возможности

- **Команда `/slot`**: Поиграйте в слоты с ботом и попробуйте поймать выигрышную комбинацию! 🎰
- **Команда `/howgay`**: Узнайте, насколько вы гей! 🌈
- **Команда `/pingdota`**: Пригласите своих друзей из группы в Dota 2! 🌈
- **Команда `/time_dota`**: Получите информацию о времени, проведенном в Dota 2, для привязанного аккаунта Steam.
- **Команда `/top_dota`**: Посмотрите список игроков в группе и их общее время в Dota 2 в порядке убывания.
- **Команда `/regsteam`**: Привяжите свой Steam ID к вашему аккаунту Telegram, чтобы бот мог отслеживать ваше время в игре!
- **Команда `/info`**: Ссылка на github.

## 1. Запуск локально через Docker

1. Скачать репозиторий.
2. Создать файл **.env** и **user_data.json** с необходимыми данными.
3. Создать публичный URL на нужном порту:
```
ngrok http $PORT
```
4. Вставить созданный ngrok URL в **WEBHOOK_URL**.
5. Запустить контейнер:
```
docker-compose up --build
```
Все запросы происходят при помощи **WEBHOOK_URL**, поэтому бот готов к деплою на облачный сервис.

### 2. Переменные окружения и данные

Основная информация помещается в файлы **.env** и **user_data.json**.
Файлы структурированы так:
```
.env

API_TOKEN=
STEAM_API_KEY=
USER_DATA_FILE=user_data.json
WEBHOOK_URL=
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

### 3. TODO

Много чего...

<div id="header" align="center">
  <img src="https://media.giphy.com/media/M9gbBd9nbDrOTu1Mqx/giphy.gif" width="100"/>
</div>
