# DjangoArchitectAPI

> Production-ready Django приложение с оптимизированной архитектурой и enterprise-подходом к разработке

[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![Django 4.2](https://img.shields.io/badge/django-4.2-green.svg)](https://www.djangoproject.com/)
[![PostgreSQL 15](https://img.shields.io/badge/postgresql-15-blue.svg)](https://www.postgresql.org/)
[![Redis 7](https://img.shields.io/badge/redis-7-red.svg)](https://redis.io/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## Технический стек

**Backend:**
- Python 3.11 — современные возможности языка
- Django 4.2 LTS — надёжность и долгосрочная поддержка
- PostgreSQL 15 — производительная реляционная БД
- Redis 7 — кэширование и управление сессиями

**Infrastructure:**
- Docker + Docker Compose — полная контейнеризация
- Gunicorn — production WSGI-сервер
- Nginx-ready — готов к деплою за reverse proxy

**Code Quality:**
- Black, Flake8 — автоматизированный контроль стиля
- Pytest — современное тестирование
- Custom QuerySets — оптимизация запросов к БД
- Settings modules (base/dev/prod) — разделение окружений

## Ключевые особенности

✅ **Query Optimization** — select_related/prefetch_related для устранения N+1  
✅ **Custom Managers** — инкапсуляция бизнес-логики на уровне ORM  
✅ **Database Indexes** — composite indexes для критичных запросов  
✅ **Cache Strategy** — Redis для сессий и частых запросов  
✅ **Settings Management** — модульная структура по окружениям  
✅ **Docker Ready** — полная контейнеризация с health checks  
✅ **Production Config** — security headers, logging, error handling

## Быстрый старт

```bash
git clone https://github.com/d1g-1t/DjangoArchitectAPI.git
cd DjangoArchitectAPI
make setup
```

**Готово.** Приложение доступно на `http://localhost:8000`

> Требования: Docker Desktop

### Создание администратора

```bash
make createsuperuser
```

### Доступные endpoints

- **Главная:** http://localhost:8000
- **Админка:** http://localhost:8000/admin/
- **PostgreSQL:** localhost:5433
- **Redis:** localhost:6380

## Архитектура

```
djangoarchitectapi/
├── apps/
│   ├── posts/          # Модели, views, managers
│   └── pages/          # Статические страницы
├── config/
│   ├── settings/       # base.py, dev.py, prod.py
│   ├── urls.py
│   └── wsgi.py
├── templates/          # Шаблоны с наследованием
├── fixtures/           # Начальные данные
└── docker-compose.yml  # Оркестрация сервисов
```

## Основные команды

```bash
make setup          # Полная установка и запуск
make up             # Запустить сервисы
make down           # Остановить сервисы
make logs           # Просмотр логов
make shell          # Django shell
make dbshell        # PostgreSQL shell
make test           # Запуск тестов
make lint           # Проверка кода
make clean          # Очистка контейнеров
```

## Технические решения

### 1. Оптимизация запросов

```python
# Custom QuerySet с оптимизацией
posts = Post.objects.select_related(
    'author', 'category', 'location'
).published()

# Результат: 1-2 запроса вместо N+1
```

### 2. Кастомные менеджеры

```python
class PostQuerySet(models.QuerySet):
    def published(self):
        return self.filter(
            is_published=True,
            pub_date__lte=timezone.now()
        )
    
    def optimized(self):
        return self.select_related('author', 'category')

class Post(models.Model):
    objects = PostQuerySet.as_manager()
```

### 3. Database Indexes

```python
class Meta:
    indexes = [
        models.Index(fields=['-pub_date', 'is_published']),
        models.Index(fields=['category', '-pub_date']),
    ]
```

### 4. Settings по окружениям

- `base.py` — общие настройки
- `dev.py` — DEBUG=True, SQLite для быстрой разработки
- `prod.py` — security headers, logging, PostgreSQL

## Безопасность

- Environment variables для секретных данных
- CSRF/XSS protection из коробки
- SQL Injection protection через ORM
- Security headers в production
- Отдельный непривилегированный пользователь в Docker

## Демонстрируемые навыки

**Django:** Custom managers, QuerySet optimization, settings modules, template inheritance  
**Database:** Indexes, query optimization, migrations  
**DevOps:** Docker multi-container, environment management, Makefile automation  
**Best Practices:** DRY, separation of concerns, code style enforcement

---

**Автор:** [@d1g-1t](https://github.com/d1g-1t)  
**Лицензия:** MIT
