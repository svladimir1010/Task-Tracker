# Импорт миксина для поддержки авторизации пользователя
from flask_login import UserMixin
# Импорт объекта базы данных из твоего приложения (SQLAlchemy)
from app import db
from app.email.tokens import generate_confirmation_token


class User(UserMixin, db.Model):
    # Наследуемся от UserMixin для поддержки Flask-Login (login_user, current_user и т.д.)
    # Наследуемся от db.Model — это модель SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    # Уникальный идентификатор пользователя (автоматически увеличивается)
    username = db.Column(db.String(20), unique=True, nullable=False)
    # Имя пользователя — обязательно и уникально, максимум 20 символов
    email = db.Column(db.String(120), unique=True, nullable=False)  # Новое поле
    # Email — тоже обязательный и уникальный (можно будет использовать для подтверждения или восстановления доступа)
    password = db.Column(db.String(60), nullable=False)
    # Хеш пароля (а не сам пароль!)
    tasks = db.relationship('Task', backref='user', lazy=True)
    # Связь один-ко-многим: один пользователь → много задач
    # backref='user' создаёт у задачи ссылку на пользователя (`task.user`)
    # lazy=True означает, что задачи будут загружаться при обращении, а не сразу

    # Новое поле для подтверждения email
    confirmed = db.Column(db.Boolean, default=True) # По умолчанию пользователь считается подтверждённым
    def get_confirmation_token(self):
        return generate_confirmation_token(self.email) # Генерация токена для подтверждения email


class Task(db.Model):
    # Наследуемся от db.Model — это отдельная таблица задач
    id = db.Column(db.Integer, primary_key=True)
    # Уникальный идентификатор задачи
    title = db.Column(db.String(100), nullable=False)
    # Название задачи — обязательно, до 100 символов
    description = db.Column(db.Text, nullable=True)
    # Описание задачи — можно оставить пустым (nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Not Started')
    # Статус задачи — обязательно, по умолчанию "Not Started"
    category = db.Column(db.String(50), nullable=True, default='General')
    # Категория задачи — не обязательная, по умолчанию "General"
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    # Время создания — по умолчанию текущее (функция базы данных)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # Внешний ключ: связывает задачу с конкретным пользователем
    # Обязательно указывать, к кому привязана задача
