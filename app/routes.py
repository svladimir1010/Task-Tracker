from flask import Blueprint, render_template, redirect, url_for, request, flash, Response
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt  # импорт базы данных и bcrypt для хеширования паролей
from app.models import Task, User  # модели пользователя и задачи
from app.forms import RegisterForm, LoginForm, TaskForm  # формы регистрации, логина и задач
from app.email.sender import send_confirmation_email
from flask_mail import Mail, Message
from app.email.tokens import confirm_token
from io import StringIO
from datetime import datetime, timezone # Убедитесь, что datetime и timezone импортированы
from dateutil import tz
from datetime import datetime
import csv

# Создание Blueprint для группировки маршрутов и удобства
bp = Blueprint('main', __name__)
mail = Mail()


# Функция для получения часового пояса пользователя
def get_user_local_timezone():
    # timezone хранится в модели User
    user_timezone_str = current_user.timezone if current_user.is_authenticated else 'UTC'

    local_tz = tz.gettz(user_timezone_str)
    if not local_tz:
        # Если часовой пояс недействителен, используем UTC как запасной вариант
        local_tz = tz.gettz('UTC')
    return local_tz


# Главная страница, отображает список задач
@bp.route('/')
@bp.route('/index')  # Добавил, если у вас есть и так
@login_required
def index():
    # Получаем параметры фильтрации и сортировки из запроса
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    priority_filter = request.args.get('priority')  # получение фильтра по приоритету
    sort_by = request.args.get('sort_by', 'id')  # По умолчанию сортировка по ID
    sort_order = request.args.get('sort_order', 'asc')  # По умолчанию возрастающий порядок
    search_filter = request.args.get('search')
    page = request.args.get('page', 1, type=int)  # Добавил пагинацию, если она у вас есть, если нет - можно убрать.

    # Формируем базовый запрос для задач текущего пользователя
    query = Task.query.filter_by(user_id=current_user.id)

    # Если есть фильтр по поиску, применяем его
    if search_filter:
        query = query.filter(
            (Task.title.ilike(f'%{search_filter}%')) |
            (Task.description.ilike(f'%{search_filter}%'))
        )

    # Применяем фильтр по статусу, если он указан
    if status_filter:
        query = query.filter_by(status=status_filter)

    # Применяем фильтр по категории, если она указана
    if category_filter:
        query = query.filter_by(category=category_filter)

    # Применяем фильтр по приоритету, если он указан
    if priority_filter:
        query = query.filter_by(priority=priority_filter)

    # Логика сортировки в зависимости от выбранного критерия
    if sort_by == 'priority':
        # Сортировка по приоритету с использованием CASE для кастомного порядка
        query = query.order_by(
            db.case(
                (Task.priority == 'High', 1),
                (Task.priority == 'Medium', 2),
                (Task.priority == 'Low', 3),
                else_=4  # Для любых других значений, если есть
            )
        )
    elif sort_by == 'due_date':
        # Сортировка по дате выполнения с учётом направления
        order = Task.due_date.asc() if sort_order == 'asc' else Task.due_date.desc()
        query = query.order_by(order, Task.id)  # Добавляем ID для стабильности
    elif sort_by == 'created_at':
        # Сортировка по дате создания
        order = Task.created_at.asc() if sort_order == 'asc' else Task.created_at.desc()
        query = query.order_by(order)
    else:  # По умолчанию или 'id'
        # Сортировка по ID
        order = Task.id.asc() if sort_order == 'asc' else Task.id.desc()
        query = query.order_by(order)

    # Выполняем запрос и получаем список задач с пагинацией
    tasks = query.paginate(page=page, per_page=5,
                           error_out=False)  # Используем paginate, если не используете, то .all()

    # Получаем часовой пояс текущего пользователя для отображения дат и проверки просроченных задач
    local_tz_for_display = get_user_local_timezone()

    # Текущее время в UTC для сравнения с датами из БД
    now_utc = datetime.now(timezone.utc)  # Это тот now_utc, который вам нужен

    # Передаём данные в шаблон
    return render_template('index.html',
                           title='Home',  # Добавил, если у вас есть в шаблоне
                           tasks=tasks,  # Передаем объект пагинации, если используете
                           status_filter=status_filter,
                           category_filter=category_filter,
                           sort_by=sort_by,
                           priority_filter=priority_filter,
                           sort_order=sort_order,
                           local_tz=local_tz_for_display,  # <--- ПЕРЕДАЕМ ОБЪЕКТ ЧАСОВОГО ПОЯСА
                           now_utc=now_utc)  # <--- ПЕРЕДАЕМ ТЕКУЩЕЕ UTC ВРЕМЯ


# Страница регистрации нового пользователя
@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()  # создаём объект формы
    if form.validate_on_submit():  # если форма валидна после отправки

        # Проверяем, что имя пользователя и email уникальны
        if User.query.filter_by(username=form.username.data).first():
            form.username.errors.append('Username already taken')
            return render_template('register.html', form=form)
        if User.query.filter_by(email=form.email.data).first():
            form.email.errors.append('Email already registered')
            return render_template('register.html', form=form)


        # Хешируем пароль и создаём пользователя
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        # Получаем часовой пояс из скрытого поля формы
        user_timezone_str = request.form.get('user_timezone', 'UTC')
        print(f"[REGISTER] Timezone from form: {user_timezone_str}")

        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password,
            confirmed=False,
            timezone = user_timezone_str
        )

        db.session.add(user)
        db.session.commit()
        print(f"[DEBUG] AFTER COMMIT, is_authenticated: {current_user.is_authenticated}")

        flash('Registration successful! Please log in.', 'success')

        # Отправляем письмо
        # send_confirmation_email(user)
        # flash('Registration successful! Check your email to confirm.', 'info')

        print(f"[DEBUG] current_user: {current_user.is_authenticated}")

        return redirect(url_for('main.login'))  # перенаправление на страницу логина
    return render_template('register.html', form=form)  # Если GET-запрос или ошибки валидации — показать форму


# 💡 Важно: в этой учебной версии подтверждение может быть отключено на этапе логина.
# Этот маршрут остаётся доступным для демонстрации, но на проде потребуется реальная проверка.


# Страница входа пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        print("[LOGIN] Form submitted")
        user = User.query.filter_by(username=form.username.data).first()

        # Проверка пароля с bcrypt
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):

            if not user.confirmed:
                user.confirmed = True
                flash('Your account has been confirmed! You are now logged in.', 'success')

                db.session.commit()
            # ⛔ Проверка подтверждения email временно отключена (учебный режим / dev-режим)
            # if not user.confirmed:
            #     flash('Пожалуйста, подтвердите свою почту перед входом.', 'warning')
            #     return redirect(url_for('main.login'))

            # Получаем часовой пояс из скрытого поля формы.
            # Если поле отсутствует или JS не сработал, по умолчанию будет 'UTC'.
            user_timezone_str = request.form.get('user_timezone', 'UTC')

            print(f"[LOGIN] Timezone from form: {user_timezone_str}")
            print(f"[LOGIN] Previous timezone: {user.timezone}")

            # Проверяем, изменился ли часовой пояс или он еще не установлен для пользователя.
            if user.timezone != user_timezone_str:
                user.timezone = user_timezone_str

                db.session.commit()  # Сохраняем изменение часового пояса в БД

            login_user(user)  # логиним пользователя

            print(f"[LOGIN] Login user: {user.username}")
            print(f"[LOGIN] Authenticated: {current_user.is_authenticated}")

            return redirect(url_for('main.index'))

        flash('Invalid username or password', 'danger')  # сообщение об ошибке
    return render_template('login.html', form=form)


@bp.route('/confirm/<token>')
def confirm_email(token):
    # ⛓️ Декодируем токен и извлекаем email
    email = confirm_token(token)

    # 🛑 Если токен недействителен или просрочен — сообщаем пользователю
    if not email:
        flash('Ссылка недействительна или устарела.', 'danger')
        return redirect(url_for('main.login'))

    # 🔍 Ищем пользователя с этим email
    user = User.query.filter_by(email=email).first_or_404()

    # ✅ Если уже подтверждён — просто сообщаем
    if user.confirmed:
        flash('Аккаунт уже подтверждён.', 'info')
    else:
        # 📌 Устанавливаем флаг подтверждения и сохраняем в БД
        user.confirmed = True
        db.session.commit()
        flash('Email подтверждён! Теперь можешь войти.', 'success')

    # 🔁 Перенаправляем на страницу входа
    return redirect(url_for('main.login'))


# Выход из аккаунта
@bp.route('/logout')
@login_required
def logout():
    logout_user()  # деавторизуем пользователя
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))  # возвращаем на логин


# Добавление новой задачи
@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    form = TaskForm()
    if form.validate_on_submit():
        # Получаем часовой пояс пользователя из скрытого поля формы
        local_tz = get_user_local_timezone() # <--- Используем функцию

        # Обработка due_date: преобразование из локального времени формы в UTC для сохранения
        utc_due_datetime = None
        if form.due_date.data:
            local_due_datetime = form.due_date.data.replace(tzinfo=local_tz)
            utc_due_datetime = local_due_datetime.astimezone(tz.tzutc()).replace(tzinfo=None)

        # Обработка reminder_date: преобразование из локального времени формы в UTC для сохранения
        utc_reminder_datetime = None
        if form.reminder_date.data:
            local_reminder_datetime = form.reminder_date.data.replace(tzinfo=local_tz)
            utc_reminder_datetime = local_reminder_datetime.astimezone(tz.tzutc()).replace(tzinfo=None)

        # Создание объекта задачи и привязка к текущему пользователю
        task = Task(
            title=form.title.data,
            description=form.description.data,
            priority=form.priority.data,
            due_date=utc_due_datetime,
            category=form.category.data or 'General',
            status=form.status.data,
            reminder_date=utc_reminder_datetime,
            user_id=current_user.id,
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_task.html', form=form)


# Редактирование существующей задачи
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    # Получаем задачу текущего пользователя или 404
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TaskForm(obj=task)

    # Получаем часовой пояс текущего пользователя
    local_tz = get_user_local_timezone()

    # В случае GET-запроса, obj=task уже заполнил form.data, но в UTC,
    # поэтому мы преобразуем их для отображения
    if request.method == 'GET':
        # Преобразуем due_date из UTC (из БД) в локальное время для отображения в форме
        if task.due_date:
            utc_due_datetime = task.due_date.replace(tzinfo=tz.tzutc())  # Делаем naive UTC aware
            form.due_date.data = utc_due_datetime.astimezone(local_tz).replace(
                tzinfo=None)  # Преобразуем в локальное и делаем naive

        # Преобразуем reminder_date из UTC (из БД) в локальное время для отображения в форме
        if task.reminder_date:
            utc_reminder_datetime = task.reminder_date.replace(tzinfo=tz.tzutc())  # Делаем naive UTC aware
            form.reminder_date.data = utc_reminder_datetime.astimezone(local_tz).replace(
                tzinfo=None)  # Преобразуем в локальное и делаем naive

    if form.validate_on_submit():
        # Обновляем данные задачи
        task.title = form.title.data
        task.description = form.description.data
        task.category = form.category.data or 'General'
        task.status = form.status.data
        task.priority = form.priority.data

        # Обработка due_date: из локального времени формы (user input) в UTC для сохранения
        if form.due_date.data:
            local_due_datetime = form.due_date.data.replace(tzinfo=local_tz)
            task.due_date = local_due_datetime.astimezone(tz.tzutc()).replace(tzinfo=None)
        else:
            task.due_date = None  # Если поле пустое, сохраняем как None

        # Обработка reminder_date: из локального времени формы (user input) в UTC для сохранения
        if form.reminder_date.data:
            local_reminder_datetime = form.reminder_date.data.replace(tzinfo=local_tz)
            task.reminder_date = local_reminder_datetime.astimezone(tz.tzutc()).replace(tzinfo=None)
        else:
            task.reminder_date = None  # Если поле пустое, сохраняем как None

        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('edit_task.html', form=form, task=task)


# Удаление задачи
@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))


# Статистика по задачам
@bp.route('/stats')
@login_required
def stats():
    # Получаем все задачи текущего пользователя
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    # Считаем количество задач по статусу
    stats = {
        'Not Started': len([t for t in tasks if t.status == 'Not Started']),
        'In Progress': len([t for t in tasks if t.status == 'In Progress']),
        'Completed': len([t for t in tasks if t.status == 'Completed'])
    }
    # Отправляем данные в шаблон
    return render_template('stats.html', stats=stats)


@bp.route('/export')
@login_required
def export_tasks():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['ID', 'Title', 'Description', 'Status', 'Category', 'Created At'])
    for task in tasks:
        writer.writerow([
            task.id, task.title, task.description or '', task.status, task.category or 'General',
            task.created_at.strftime('%Y-%m-%d %H:%M')
        ])
    output.seek(0)
    return Response(output, mimetype='text/csv', headers={'Content-Disposition': 'attachment;filename=tasks.csv'})
