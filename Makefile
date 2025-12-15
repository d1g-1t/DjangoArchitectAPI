.PHONY: help setup build up down restart logs shell migrate makemigrations createsuperuser test clean

BLUE := \033[0;34m
GREEN := \033[0;32m
RED := \033[0;31m
NC := \033[0m

help: ## Показать эту справку
	@echo "${BLUE}DjangoArchitectAPI - Доступные команды:${NC}"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  ${GREEN}%-20s${NC} %s\n", $$1, $$2}'

setup: ## 🚀 Полная установка и запуск проекта (одна команда!)
	@echo "${BLUE}🚀 Запускаем DjangoArchitectAPI...${NC}"
	@echo "${BLUE}⏳ Останавливаем старые контейнеры...${NC}"
	@docker-compose down 2>/dev/null || true
	@if [ ! -f .env ]; then cp .env.example .env; echo "${GREEN}✓${NC} Файл .env создан"; else echo "${GREEN}✓${NC} Файл .env уже существует"; fi
	@echo "${BLUE}⏳ Собираем Docker образы...${NC}"
	@docker-compose build || { echo "${RED}✗${NC} Ошибка сборки образов"; exit 1; }
	@echo "${GREEN}✓${NC} Docker образы собраны"
	@echo "${BLUE}⏳ Запускаем все сервисы (PostgreSQL, Redis, Web)...${NC}"
	@docker-compose up -d || { \
		echo "${RED}✗${NC} Ошибка запуска сервисов"; \
		echo "${BLUE}ℹ${NC}  Проверяем логи..."; \
		docker-compose logs; \
		exit 1; \
	}
	@echo "${GREEN}✓${NC} Сервисы запущены"
	@echo "${BLUE}⏳ Ждем готовности PostgreSQL...${NC}"
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		if docker-compose exec -T db pg_isready -U djangoarchitectapi_user -d djangoarchitectapi >/dev/null 2>&1; then \
			echo "${GREEN}✓${NC} PostgreSQL готов (попытка $$i)"; \
			break; \
		fi; \
		if [ $$i -eq 10 ]; then \
			echo "${RED}✗${NC} PostgreSQL не запустился после 10 попыток"; \
			echo "${BLUE}ℹ${NC}  Логи PostgreSQL:"; \
			docker-compose logs db; \
			exit 1; \
		fi; \
		sleep 3; \
	done
	@echo "${BLUE}⏳ Ждем готовности веб-сервера...${NC}"
	@sleep 5
	@echo "${BLUE}⏳ Применяем миграции...${NC}"
	@docker-compose exec -T web python manage.py migrate --noinput || { \
		echo "${RED}✗${NC} Ошибка миграций"; \
		echo "${BLUE}ℹ${NC}  Логи веб-сервера:"; \
		docker-compose logs web; \
		exit 1; \
	}
	@echo "${GREEN}✓${NC} Миграции применены"
	@echo "${BLUE}⏳ Собираем статику...${NC}"
	@docker-compose exec -T web python manage.py collectstatic --noinput || true
	@echo "${GREEN}✓${NC} Статика собрана"
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
