# Task Tracker

Task Tracker — веб-приложение для управления задачами, построенное с использованием Flask, SQLite, Flask-Login и Bootstrap. Поддерживает CRUD-операции, аутентификацию пользователей, фильтрацию задач, сортировку, визуальную статистику и автоматические напоминания.

## Функционал
- Регистрация и логин пользователей с аутентификацией через Flask-Login.
- Хранение задач в базе данных SQLite с помощью Flask-SQLAlchemy.
- Формы и валидация через Flask-WTF, шифрование паролей с Flask-Bcrypt.
- Адаптивный интерфейс на Bootstrap с переключением темы (светлая/темная).
- Управление задачами: добавление, редактирование, удаление.
- Фильтрация по статусу, категории, приоритету и поиску по заголовкам/описаниям.
- Сортировка по дате создания, сроку выполнения и приоритету.
- Визуальные индикаторы просроченных задач.
- Статистика задач с прогресс-барами.
- Экспорт списка задач в CSV.
- Улучшенный UI/UX:
  - Адаптивное отображение задач колонками на больших экранах.
  - Оптимизированная мобильная навигация с Bootstrap Offcanvas.
  - Доступные формы с правильными метками.
  - Переработанный дизайн карточек с усечением заголовков и улучшенными иконками.
- Новые поля задач:
  - Приоритет (High, Medium, Low).
  - Срок выполнения (due_date).
  - Дата напоминания (reminder_date).
- Фильтрация по приоритету и сроку, кнопка "Сбросить фильтры".
- Иконки в панели фильтров для лучшего восприятия.
- Персонализированные часовые пояса: автоматическое определение и отображение дат в локальном времени.
- Автоматические напоминания:
  - Установка даты и времени напоминаний.
  - Фоновая задача (APScheduler) проверяет задачи каждые 15 минут.
  - Уведомления по email (через Mailtrap для тестирования).
  - Уведомления в Telegram через бота "PowerTaskTracker".
  - Отметка отправленных напоминаний для избежания дублирования.

## Технологии
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Bcrypt, Flask-Mail, Flask-APScheduler.
- **Frontend**: HTML, CSS (Bootstrap), JavaScript.
- **Дополнительно**: python-dateutil (таймзоны), email_validator, python-telegram-bot (Telegram-уведомления).
- **Деплой**: PythonAnywhere.

## Live Demo
[https://protocol777.pythonanywhere.com](https://protocol777.pythonanywhere.com)

## Установка и настройка
1. Клонируйте репозиторий: git clone https://github.com/svladimir1010/Task-Tracker.git
2. Установите зависимости: pip install -r requirements.txt
3. Создайте файл `.env` с переменными окружения:
         TELEGRAM_TOKEN=ваш_токен_от_BotFather
         TELEGRAM_CHAT_ID=ваш_chat_id
         MAIL_SERVER=smtp.mailtrap.io
         MAIL_PORT=2525
         MAIL_USERNAME=ваш_mailtrap_username
         MAIL_PASSWORD=ваш_mailtrap_password
         MAIL_DEFAULT_SENDER=ваш_email

4. Запустите приложение: python run.py

## Скриншоты
![Register dark Page](screenshots/register_dark.png)
![Login light Page](screenshots/login_light.png)
![Main Page](screenshots/main.png)
![Main tablet Page](screenshots/main_tablet.png)
![Main mobile Page](screenshots/main_mobile.png)
![Add light Page](screenshots/add_light.png)
![Edit dark Page](screenshots/edit_dark.png)
![Stats dark Page](screenshots/stats_dark.png)
![404 Error Page](screenshots/error_404.png)

## Будущие улучшения
- Миграция фронтенда на React для динамического интерфейса.
- Добавление подтверждения email для пользователей.
- Интеграция с другими мессенджерами (например, Discord).