# Импорт базового класса формы из Flask-WTF
from flask_wtf import FlaskForm
# Импорт полей формы
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
# Импорт валидаторов для проверки корректности данных
from wtforms.validators import DataRequired, Length, Email, ValidationError  # Email пока не используется, но пригодится, если добавишь поле e-mail
# Импорт модели User для проверки уникальности username/email
from app.models import User


class RegisterForm(FlaskForm):
    # Поле для ввода имени пользователя, обязательно для заполнения,
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    # поле для ввода email, обязательно, должно быть корректным и не длиннее 120 символов
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    # Поле для ввода пароля, также обязательно, от 6 символов
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    # Кнопка отправки формы
    submit = SubmitField('Register')

    # Дополнительная валидация для username — проверка уникальности
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already taken')

    # Дополнительная валидация для email — проверка уникальности
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered')


class LoginForm(FlaskForm):
    # Те же поля, (без подтверждения пароля)
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Login')


class TaskForm(FlaskForm):
    # Название задачи — обязательно, от 1 до 100 символов
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    # Описание задачи — не обязательно, максимум 500 символов
    description = TextAreaField('Description', validators=[Length(max=500)])
    # Статус задачи — выпадающий список с 3 вариантами. Обязателен.
    status = SelectField(
        'Status',
        choices=[
            ('Not Started', 'Not Started'),
            ('In Progress', 'In Progress'),
            ('Completed', 'Completed')
        ],
        validators=[DataRequired()]
    )
    # Категория задачи — не обязательна, максимум 50 символов
    category = StringField('Category', validators=[Length(max=50)])
    # Кнопка сохранения
    submit = SubmitField('Save Task')



