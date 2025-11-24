FROM python:3.11-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Создаем пользователя для запуска приложения
RUN useradd -m -u 1000 appuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем зависимости
COPY requirements/base.txt requirements/prod.txt /app/requirements/

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements/prod.txt

# Копируем проект
COPY --chown=appuser:appuser . /app/

# Создаем директории для статики и медиа
RUN mkdir -p /app/staticfiles /app/media && \
    chown -R appuser:appuser /app

# Переключаемся на пользователя appuser
USER appuser

# Собираем статику
RUN python manage.py collectstatic --noinput || true

# Expose порт
EXPOSE 8000

# Запуск приложения
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
