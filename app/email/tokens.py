from itsdangerous import URLSafeTimedSerializer
from flask import current_app

def generate_confirmation_token(email):
    # Создаём сериализатор с секретным ключом приложения
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    # Генерируем токен, содержащий email пользователя
    return serializer.dumps(email, salt='email-confirm')

def confirm_token(token, expiration=3600):
    # Создаём сериализатор с тем же секретным ключом
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])

    try:
        # Пытаемся расшифровать токен, проверяя срок действия (по умолчанию 1 час)
        email = serializer.loads(token, salt='email-confirm', max_age=expiration)
    except Exception:
        # Возвращаем False, если токен недействителен или просрочен
        return False

    # Возвращаем email, если токен валиден
    return email

# 📌 Используется для подтверждения почты — в текущей учебной версии механизм включён,
# но фактическая проверка подтверждения может быть отключена для удобства тестирования.
