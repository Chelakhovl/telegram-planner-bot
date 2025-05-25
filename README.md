# Telegram Planner Bot

Telegram-бот для планування дня з нагадуваннями, аналітикою, підтримкою імпорту/експорту подій, категоріями та багатомовністю.

---

## ⚡ Основні можливості

- Додавання подій через `/add_event` з FSM
- Підтримка періодичності: `once/daily/weekly/monthly/yearly`
- Нагадування за вказаний час до події (через Celery + Redis)
- Перегляд подій:
  - `/today`
  - `/week`
  - `/month`
- Експорт / імпорт у CSV
- Категорії й теги для подій
- Редагування та видалення подій через інлайн-кнопки
- Аналіз перевантаження розкладу (`/analyze`)
- Мультимовність: українська / англійська
- Очистка всіх подій (`/clear`)

---

## 📅 Інсталяція

### 1. Клонування репозиторію
```bash
git clone https://github.com/your-username/planner-bot.git
cd planner-bot
2. Встановлення залежностей
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
3. Налаштування .env
Створіть файл .env в корені проєкту:

SECRET_KEY=your_django_secret
DEBUG=True
BOT_TOKEN=your_telegram_bot_token
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=our_db_password
DB_HOST=our_db_host
DB_PORT=our_db_port
🚀 Запуск

Django
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
Celery + Beat (в окремих терміналах)
celery -A planner_backend worker --loglevel=info
celery -A planner_backend beat --loglevel=info
Redis
redis-server
🔎 Структура проєкту

planner_backend/
├── bot/                # Aiogram логіка
│   ├── handlers/       # Хендлери команд
│   ├── locale/         # Тексти та переклад
│   └── main.py         # Старт Telegram бота
├── event/              # Логіка подій (моделі, сервіси, Celery tasks)
├── user/               # Користувачі
├── backups/            # Бекап бази
├── logs/               # Логи по модулях
├── manage.py
└── planner_backend/    # Django core

Telegram Bot: @myplanner1996_bot
Автор: Челахов Леонід