from flask import render_template
from datetime import datetime # Импортируем datetime


def page_not_found(e):
    return render_template('404.html'), 404

def internal_server_error(e):
    return render_template('500.html'), 500



