.PHONY: help setup build up down restart logs shell migrate makemigrations createsuperuser test clean

# Цвета для вывода
BLUE := \033[0;34m
GREEN := \033[0;32m
NC := \033[0m # No Color

help: ## Показать эту справку
	@echo "${BLUE}DjangoArchitectAPI - Доступные команды:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}'

setup: ## 🚀 Полная установка и запуск проекта (одна команда!)
	@echo "${BLUE}🚀 Запускаем DjangoArchitectAPI...${NC}"
	@echo "${BLUE}⏳ Проверяем занятые порты...${NC}"
	@docker-compose down 2>/dev/null || true
	@cp -n .env.example .env 2>/dev/null || true
	@echo "${GREEN}✓${NC} Файл .env создан"
	@docker-compose build --quiet
	@echo "${GREEN}✓${NC} Docker образы собраны"
	@echo "${BLUE}⏳ Запускаем PostgreSQL и Redis...${NC}"
	@docker-compose up -d db redis
	@echo "${BLUE}⏳ Ждем запуска баз данных (15 сек)...${NC}"
	@sleep 15
	@echo "${BLUE}⏳ Запускаем веб-сервер...${NC}"
	@docker-compose up -d web
	@sleep 5
	@echo "${BLUE}⏳ Применяем миграции...${NC}"
	@docker-compose exec -T web python manage.py migrate --noinput
	@echo "${BLUE}⏳ Загружаем начальные данные...${NC}"
	@docker-compose exec -T web python manage.py loaddata initial_data 2>/dev/null || echo "${BLUE}ℹ${NC}  Фикстуры не загружены (возможно, уже существуют)"
	@echo ""
	@echo "${GREEN}✅ Проект успешно запущен!${NC}"
	@echo ""
	@echo "${BLUE}📍 Доступные адреса:${NC}"
	@echo "   🌐 Сайт:     ${GREEN}http://localhost:8000${NC}"
	@echo "   👤 Админка:  ${GREEN}http://localhost:8000/admin/${NC}"
	@echo "   💾 PostgreSQL: ${GREEN}localhost:5433${NC} (внешний порт)"
	@echo "   🔴 Redis:      ${GREEN}localhost:6380${NC} (внешний порт)"
	@echo ""
	@echo "${BLUE}💡 Следующие шаги:${NC}"
	@echo "   1. Создайте суперпользователя: ${GREEN}make createsuperuser${NC}"
	@echo "   2. Откройте сайт: ${GREEN}http://localhost:8000${NC}"
	@echo "   3. Войдите в админку: ${GREEN}http://localhost:8000/admin/${NC}"
	@echo ""
	@echo "${BLUE}📋 Полезные команды:${NC}"
	@echo "   ${GREEN}make logs${NC}       - просмотр логов"
	@echo "   ${GREEN}make shell${NC}      - Django shell"
	@echo "   ${GREEN}make down${NC}       - остановить все"
	@echo "   ${GREEN}make help${NC}       - все команды"
	@echo ""

build: ## 🔨 Собрать Docker образы
	@echo "${BLUE}🔨 Собираем Docker образы...${NC}"
	@docker-compose build

up: ## ▶️  Запустить все сервисы
	@echo "${BLUE}▶️  Запускаем сервисы...${NC}"
	@docker-compose up -d
	@echo "${GREEN}✓${NC} Сервисы запущены"

down: ## ⏸️  Остановить все сервисы
	@echo "${BLUE}⏸️  Останавливаем сервисы...${NC}"
	@docker-compose down
	@echo "${GREEN}✓${NC} Сервисы остановлены"

restart: down up ## 🔄 Перезапустить сервисы

logs: ## 📋 Показать логи
	@docker-compose logs -f web

logs-all: ## 📋 Показать логи всех сервисов
	@docker-compose logs -f

shell: ## 🐚 Открыть Django shell
	@docker-compose exec web python manage.py shell

bash: ## 💻 Открыть bash в контейнере
	@docker-compose exec web bash

migrate: ## 🗄️  Применить миграции
	@docker-compose exec web python manage.py migrate

makemigrations: ## 📝 Создать миграции
	@docker-compose exec web python manage.py makemigrations

createsuperuser: ## 👤 Создать суперпользователя
	@docker-compose exec web python manage.py createsuperuser

loaddata: ## 📊 Загрузить тестовые данные
	@docker-compose exec web python manage.py loaddata initial_data

test: ## 🧪 Запустить тесты
	@docker-compose exec web pytest -v

test-cov: ## 📊 Запустить тесты с покрытием
	@docker-compose exec web pytest --cov=. --cov-report=html --cov-report=term

lint: ## 🔍 Проверить код (flake8)
	@docker-compose exec web flake8 .

format: ## ✨ Форматировать код (black)
	@docker-compose exec web black .

clean: ## 🧹 Очистить проект (удалить контейнеры и volumes)
	@echo "${BLUE}🧹 Очищаем проект...${NC}"
	@docker-compose down -v
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "${GREEN}✓${NC} Проект очищен"

db-reset: ## 🔄 Сбросить базу данных
	@echo "${BLUE}🔄 Сбрасываем базу данных...${NC}"
	@docker-compose down
	@docker volume rm minimalistic_django_blog_postgres_data 2>/dev/null || true
	@docker-compose up -d db
	@sleep 5
	@docker-compose up -d web
	@sleep 3
	@docker-compose exec web python manage.py migrate
	@docker-compose exec web python manage.py loaddata initial_data
	@echo "${GREEN}✓${NC} База данных сброшена"

prod-build: ## 🏭 Собрать production образ
	@docker-compose -f docker-compose.prod.yml build

prod-up: ## 🏭 Запустить production
	@docker-compose -f docker-compose.prod.yml up -d
