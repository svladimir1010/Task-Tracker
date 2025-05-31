from flask_mail import Message
from flask import url_for
from app import mail

def send_confirmation_email(user):
    # Генерация токена для подтверждения почты
    token = user.get_confirmation_token()

    # Построение URL для подтверждения (маршрут 'main.confirm_email')
    confirm_url = url_for('main.confirm_email', token=token, _external=True)

    # Создание email-сообщения
    msg = Message('Подтверждение почты', recipients=[user.email])
    msg.body = f'Привет, {user.username}!\nПерейди по ссылке: {confirm_url}'

    # Временный отладочный вывод токена и ссылки в консоль (для тестов без настоящей почты)
    print(f'[DEBUG] Токен подтверждения: {token}')
    print(f'[DEBUG] Ссылка подтверждения: {confirm_url}')

    # Отправка email через Flask-Mail
    # ⚠️ В учебной версии письмо отправляется, но подтверждение email программно отключено
    mail.send(msg)
