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

@bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form.get('description')
        task.category = request.form.get('category', 'General')
        task.status = request.form.get('status', 'Not Started')
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('edit_task.html', task=task)

@bp.route('/delete/<int:id>', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('main.index'))
