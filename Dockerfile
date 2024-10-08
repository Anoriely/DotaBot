FROM python

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

ENV TELEGRAM_API_KEY=${TELEGRAM_API_KEY}
ENV ANOTHER_API_KEY=${ANOTHER_API_KEY}

EXPOSE 8080

CMD ["python3", "dotaBot.py"]
