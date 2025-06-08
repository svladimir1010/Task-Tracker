# app/scheduler_jobs.py

from datetime import datetime
from flask import current_app  # current_app нужен для доступа к контексту приложения
from flask_mail import Message  # Для создания почтовых сообщений
from app import db, mail  # Импортируем экземпляры db и mail, которые инициализируются в app/__init__.py
from app.models import Task, User  # Импортируем ваши модели Task и User


def send_task_reminders(app):  # app передается как аргумент из планировщика
    # current_app позволяет получить доступ к объекту Flask-приложения
    # и его конфигурации/расширениям внутри фоновой задачи.
    # Это обязательно, когда работаешь с Flask-SQLAlchemy или Flask-Mail вне контекста запроса.
    with app.app_context():
        print(f"[{datetime.utcnow()}] Running send_task_reminders job...")  # Логирование для отладки

        # Получаем задачи, которые подходят для напоминания:
        # 1. reminder_date наступила или уже прошла
        # 2. Статус задачи не 'Completed'
        # 3. Напоминание по этой задаче еще не было отправлено (reminder_sent = False)
        tasks_to_remind = Task.query.filter(
            Task.reminder_date <= datetime.utcnow(),
            Task.status != 'Completed',
            Task.reminder_sent == False
        ).all()

        print(f"Found {len(tasks_to_remind)} tasks needing reminders.")

        for task in tasks_to_remind:
            try:
                # Получаем email пользователя, которому принадлежит задача
                # Предполагаем, что у Task есть связь `user` с моделью `User`
                # и у `User` есть поле `email`.
                user_email = task.user.email
                if not user_email:
                    print(f"Warning: No email found for user associated with task {task.id}. Skipping.")
                    continue

                msg = Message(
                    subject=f'Task Reminder: "{task.title}" is due soon!',
                    recipients=[user_email],
                    sender=current_app.config.get('MAIL_DEFAULT_SENDER')  # Используем настроенный отправитель
                )
                msg.body = (
                    f'Hello,\n\n'
                    f'Just a friendly reminder that your task "{task.title}" is due on {task.due_date.strftime("%d %b %Y %H:%M")}.\n\n'
                    f'Details:\n'
                    f'  Description: {task.description or "N/A"}\n'
                    f'  Category: {task.category or "N/A"}\n'
                    f'  Priority: {task.priority}\n'
                    f'  Status: {task.status}\n\n'
                    f'Best regards,\nYour Task Tracker'
                )

                mail.send(msg)
                print(f"Sent reminder for task ID {task.id} to {user_email}")

                # Отмечаем, что напоминание было отправлено
                task.reminder_sent = True
                task.reminder_sent_at = datetime.utcnow()  # Записываем время отправки
                db.session.add(task)  # Добавляем измененный объект в сессию
                db.session.commit()  # Сохраняем изменения в базе данных

            except Exception as e:
                # В случае ошибки откатываем изменения для текущей задачи, чтобы она снова попала в выборку
                db.session.rollback()
                print(f"Error sending reminder for task {task.id}: {e}")