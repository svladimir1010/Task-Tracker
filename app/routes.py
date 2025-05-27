from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user, login_required
from app import db, bcrypt
from app.models import Task, User

bp = Blueprint('main', __name__)


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.index'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))


@bp.route('/', methods=['GET'])
@login_required
def index():
    status_filter = request.args.get('status')
    category_filter = request.args.get('category')
    sort_by = request.args.get('sort_by', 'id')
    query = Task.query.filter_by(user_id=current_user.id)
    if status_filter:
        query = query.filter_by(status=status_filter)
    if category_filter:
        query = query.filter_by(category=category_filter)
    if sort_by == 'created_at':
        tasks = query.order_by(Task.created_at.desc()).all()
    else:
        tasks = query.order_by(Task.id).all()
    return render_template('index.html', tasks=tasks, status_filter=status_filter, category_filter=category_filter, sort_by=sort_by)


@bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        category = request.form.get('category', 'General')
        status = request.form.get('status')
        task = Task(title=title, description=description, category=category, status=status, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_task.html')


@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description')
        task.category = request.form.get('category', 'General')
        task.status = request.form.get('status', 'Not Started')
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('edit_task.html', task=task)


@bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete_task(id):
    task = Task.query.filter_by(id=id, user_id=current_user.id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))

@bp.route('/stats')
@login_required
def stats():
    tasks = Task.query.filter_by(user_id=current_user.id).all()
    stats = {
        'Not Started': len([t for t in tasks if t.status == 'Not Started' ]),
        'In Progress': len([t for t in tasks if t.status == 'In Progress' ]),
        'Completed': len([t for t in tasks if t.status == 'Completed' ])
    }
    return render_template('stats.html', stats=stats)

