from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    from app.routes import bp
    app.register_blueprint(bp)

    return app
