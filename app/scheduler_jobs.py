import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv
from flask import current_app
from flask_mail import Message
from telegram import Bot

from app import db, mail
from app.models import Task, User

# Загрузка переменных окружения
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=TELEGRAM_TOKEN)


# Асинхронная отправка сообщений Telegram
async def send_telegram_batch_messages(messages):
    for chat_id, message in messages:
        try:
            await bot.send_message(chat_id=chat_id, text=message)
            print(f"📨 Telegram message sent: {message}")
        except Exception as e:
            print(f"❌ Failed to send Telegram message: {e}")


# Основная задача напоминаний
def send_task_reminders(app):
    with app.app_context():
        now = datetime.utcnow()
        tasks = Task.query.filter(
            Task.reminder_date <= now,
            Task.reminder_sent == False,
            Task.status != 'Completed'
        ).all()

        print(f"[{now}] Running send_task_reminders job...")
        print(f"Found {len(tasks)} tasks needing reminders.")

        telegram_messages = []

        for task in tasks:
            try:
                user = task.user
                user_email = user.email

                # ----- Email -----
                if user_email:
                    msg = Message(
                        subject=f'Task Reminder: "{task.title}" is due soon!',
                        recipients=[user_email],
                        sender=current_app.config.get('MAIL_DEFAULT_SENDER')
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
                    print(f"📧 Email sent to {user_email} for task ID {task.id}")
                else:
                    print(f"⚠️ No email found for user with task {task.id}. Skipping email.")

                # ----- Telegram -----
                if TELEGRAM_TOKEN and CHAT_ID:
                    tg_message = (
                        f'🔔 Напоминание!\n'
                        f'Задача: {task.title}\n'
                        f'Описание: {task.description or "—"}\n'
                        f'Приоритет: {task.priority}\n'
                        f'До: {task.due_date.strftime("%d %b %Y %H:%M")}\n'
                        f'Статус: {task.status}'
                    )
                    telegram_messages.append((CHAT_ID, tg_message))

                # ----- Обновление задачи -----
                task.reminder_sent = True
                task.reminder_sent_at = datetime.utcnow()
                db.session.add(task)
                db.session.commit()

            except Exception as e:
                db.session.rollback()
                print(f"❌ Error sending reminder for task {task.id}: {e}")

        # Отправка всех Telegram-сообщений одной пачкой
        if telegram_messages:
            try:
                asyncio.run(send_telegram_batch_messages(telegram_messages))
            except Exception as e:
                print(f"❌ Failed to send batch Telegram messages: {e}")
