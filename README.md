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

## 📦 Встановлення та запуск

### 1. 🧬 Клонування репозиторію
```bash
git clone https://github.com/Chelakhovl/telegram-planner-bot.git
cd planner_backend
```

---

### 2. 🔧 Встановлення залежностей
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

### 3. ⚙️ Налаштування `.env`

Створи файл `.env` у корені проєкту та додай:
```env
SECRET_KEY=your_django_secret
DEBUG=True

BOT_TOKEN=your_telegram_bot_token

DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host
DB_PORT=your_db_port
```

---

## 🚀 Запуск проєкту

### 🛠️ Django (бекенд)
```bash
python manage.py migrate
python manage.py createsuperuser   # тільки один раз
python manage.py runserver
```

---

### ⏳ Celery + Beat (у **двох** окремих терміналах)

**Celery Worker:**
```bash
celery -A planner_backend worker --loglevel=info
```

**Celery Beat:**
```bash
celery -A planner_backend beat --loglevel=info
```

---

### 🧠 Redis (у ще одному терміналі)
```bash
redis-server
```

---

### 🤖 Telegram-бот (Aiogram)
```bash
cd bot
python main.py
```

> Успішний запуск → `MAIN STARTED ✅`
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