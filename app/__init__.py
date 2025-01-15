from flask import Flask
from config import Config
from app.db_init import get_db_cursor
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from main import User, Contact

bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    with app.app_context():
        # Создание таблиц при старте приложения
        with get_db_cursor(commit=True) as cursor:
            User.create_table(cursor)
            Contact.create_table(cursor)

    return app