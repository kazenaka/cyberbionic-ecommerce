# CyberShop - E-Commerce Platform
Учебный курсовой проект интернет-магазина (Single Page Application), построенный на раздельной (Decoupled) архитектуре. 
🌐 **Посмотреть живой проект - https://kazenaka.github.io/cyberbionic-ecommerce/frontend/ **

## 🏗 Архитектура и Стек технологий
Проект разделен на две независимые части: Backend (REST API) и Frontend (SPA-клиент).

**Backend (Серверная часть):**
* Python 3.12 + Django 5.x
* Django REST Framework (DRF)** — построение API.
* SimpleJWT** — безопасная токеновая авторизация.
* PostgreSQL** — боевая база данных (на платформе Render).
* SQLite** — база данных для локальной разработки.
* Gunicorn & WhiteNoise** — веб-сервер и раздача статики в production.

**Frontend (Клиентская часть):**
* HTML5 / CSS3
* Vanilla JavaScript (ES6+) — логика, роутинг и API-запросы.
* Tailwind CSS — стилизация интерфейса (через CDN).

## ✨ Ключевой функционал

* Автоматическое переключение API-эндпоинтов (localhost для разработки, onrender.com для продакшена).
* Поиск товаров по названию и фильтрация по цене (через django-filter).
* Регистрация и логин через JWT-токены с сохранением сессии в localStorage.
* Добавление товаров в корзину, оформление заказа с указанием адреса доставки.
* Просмотр данных пользователя, истории заказов и статусов.
* Управление товарами, категориями, пользователями и заказами через стандартную админку Django.

## 🚀 Запуск проекта для локальной разработки

### 1. Клонирование репозитория
```bash
git clone https://github.com/kazenaka/cyberbionic-ecommerce.git
cd cyberbionic-ecommerce
```
### 2. Настройка Backend
Создайте и активируйте виртуальное окружение:
```bash

# Для Windows
python -m venv venv
venv\Scripts\activate

# Для Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Установите зависимости:
```bash
pip install -r requirements.txt
```

Примените миграции (создастся локальная база db.sqlite3):
```bash
python manage.py migrate
```

Создайте суперпользователя для доступа в админку:
```bash
python manage.py createsuperuser
```

Запустите локальный сервер разработки:
```bash
python manage.py runserver
```

*Backend будет доступен по адресу: http://127.0.0.1:8000/*

### 3. Настройка Frontend
Для запуска клиентской части установите расширение **Live Server** для VS Code.
1. Откройте файл frontend/index.html.
2. Нажмите кнопку **"Go Live"**.
3. Сайт откроется по адресу `http://127.0.0.1:5500/frontend/`.

*Примечание: Frontend автоматически определит, что запущен на `127.0.0.1`, и будет отправлять запросы к вашему локальному серверу Django.*

## ☁️ Деплой (Production)
* **API** развернуто на бесплатном тарифе сервиса **[Render](https://render.com/)**. При долгом отсутствии запросов сервер может "засыпать" (первый ответ занимает ~30+ секунд).
* **Frontend** хостится через **GitHub Pages**.
