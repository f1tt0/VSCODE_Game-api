# Використовуємо офіційний образ Python
FROM python:3.11-slim

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файл залежностей для кешування
COPY ./requirements.txt .

# Встановлюємо залежності
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проєкту
COPY . .

# --- Виконання вимоги А2 (AppVersion) ---
# Оголошуємо аргумент, який ми передамо при збірці
ARG AppVersion="1.0.0"
# Записуємо його у змінні середовища контейнера
ENV APP_VERSION=$AppVersion

# Відкриваємо порт
EXPOSE 8000

# Команда для запуску сервера
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]