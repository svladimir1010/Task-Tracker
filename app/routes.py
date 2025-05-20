from flask import Blueprint, render_template, redirect, url_for, request, flash
from app import db
from app.models import Task

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)


@bp.route('/add', methods=['GET', 'POST'])
def add_task():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        category = request.form.get('category', 'General')
        task = Task(title=title, description=description, category=category)
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('add_task.html')
