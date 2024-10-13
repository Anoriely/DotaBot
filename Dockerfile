# syntax=docker/dockerfile:1.4
# Устанавливаем платформу для сборки образа
FROM --platform=linux/amd64 python:3.9-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install flask pytelegrambotapi gunicorn


# Запуск приложения
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "main:app"]
