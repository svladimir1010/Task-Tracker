from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt         # импорт базы данных и bcrypt для хеширования паролей
from app.models import Task, User  # модели пользователя и задачи
from app.forms import RegisterForm, LoginForm, TaskForm  # формы регистрации, логина и задач

from datetime import datetime



# Создание Blueprint для группировки маршрутов и удобства
bp = Blueprint('main', __name__)

# Главная страница, отображает список задач
@bp.route('/')
@login_required    # доступ только для авторизованных пользователей
def index():
    # Получение параметров фильтрации и сортировки из URL
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    sort_by = request.args.get('sort_by', 'id')      # По умолчанию сортировка по ID

    # Формируем запрос на выборку задач, принадлежащих текущему пользователю
    query = Task.query.filter_by(user_id=current_user.id)
    # Применяем фильтры, если они указаны
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)

    # Сортировка: по дате создания или по ID
    if sort_by == 'created_at':
        tasks = query.order_by(Task.created_at.desc()).all()
    else:
        tasks = query.order_by(Task.id).all()

    # Отправляем данные в шаблон
    return render_template('index.html', tasks=tasks, status_filter=status_filter, category_filter=category_filter, sort_by=sort_by, now=datetime.now())


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
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')

        return redirect(url_for('main.login'))  # перенаправление на страницу логина
    return render_template('register.html', form=form, now=datetime.now())  # Если GET-запрос или ошибки валидации — показать форму


# Страница входа пользователя
@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Проверка пароля
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)  # логиним пользователя
            return redirect(url_for('main.index'))

        flash('Invalid username or password', 'danger')  # сообщение об ошибке
    return render_template('login.html', form=form, now=datetime.now())


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
        # Создание объекта задачи и привязка к текущему пользователю
        task = Task(
            title=form.title.data,
            description=form.description.data,
            category=form.category.data or 'General',
            status=form.status.data,
            user_id=current_user.id
        )
        db.session.add(task)
        db.session.commit()
        flash('Task added successfully!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_task.html', form=form, now=datetime.now())


# Редактирование существующей задачи
@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    # Получаем задачу текущего пользователя или 404
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    form = TaskForm()

    if form.validate_on_submit():
        # Обновляем данные задачи
        task.title = form.title.data
        task.description = form.description.data
        task.category = form.category.data or 'General'
        task.status = form.status.data
        db.session.commit()
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.index'))

    elif request.method == 'GET':
        # Предзаполнение формы текущими данными задачи
        form.title.data = task.title
        form.description.data = task.description
        form.category.data = task.category
        form.status.data = task.status

    return render_template('edit_task.html', form=form, task=task, now=datetime.now())


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
    return render_template('stats.html', stats=stats, now=datetime.now())

