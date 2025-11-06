FROM python:3.9-slim

WORKDIR /app

# Установка зависимостей
RUN pip install --no-cache-dir \
    numpy \
    torch \
    phe

# Копирование всех Python модулей
COPY *.py ./

# Установка переменных окружения
ENV PYTHONUNBUFFERED=1

CMD ["python", "party.py"]
