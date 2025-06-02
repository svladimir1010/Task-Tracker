# Импорт основных библиотек Flask и расширений
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy  # ORM для работы с БД
from flask_login import LoginManager    # Управление сессиями пользователей
from flask_bcrypt import Bcrypt         # Хэширование паролей
import os
from dotenv import load_dotenv          # Загрузка переменных окружения из .env
from flask_mail import Mail
from config import Config



# Загружаем переменные окружения из файла .env
load_dotenv()

# Инициализация расширений, пока без привязки к приложению
moment = Moment()
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()  # Инициализация Flask-Mail для отправки писем


def create_app():
    """
    Фабричная функция для создания экземпляра Flask-приложения.
    Настраивает конфигурации, инициализирует расширения и регистрирует Blueprints.
    """
    app = Flask(__name__)

    # # Конфигурация ключа безопасности (используется для сессий и CSRF)
    # app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-only-key')
    # # Конфигурация подключения к базе данных (используется SQLite)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
    migrate = Migrate(app, db)
    app.config.from_object(Config)

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Отключаем предупреждение

    # Инициализация расширений с привязкой к текущему приложению
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)  # Инициализация Flask-Mail
    moment.init_app(app)  # Инициализация Flask-Moment

    # Указываем, куда перенаправлять неавторизованных пользователей
    login_manager.login_view = 'main.login'

    # Импорт модели пользователя для Flask-Login
    from app.models import User

    # Функция загрузки пользователя по ID для Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Импорт и регистрация Blueprint с маршрутами приложения
    from app.routes import bp
    app.register_blueprint(bp)

    # Создание таблиц в базе данных, если их ещё нет
    with app.app_context():
        db.create_all()


    from app import errors  # Импорт обработчиков ошибок приложения
    # Регистрация глобальных обработчиков ошибок
    app.register_error_handler(404, errors.page_not_found)
    app.register_error_handler(500, errors.internal_server_error)

    return app


