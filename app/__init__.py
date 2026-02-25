import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


db = SQLAlchemy()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-secret"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///shornbee.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        MAIL_FROM=os.getenv("MAIL_FROM", "noreply@shornbee.local"),
        APPROVAL_BASE_URL=os.getenv("APPROVAL_BASE_URL", "http://localhost:5000"),
    )

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "login"
    limiter.init_app(app)

    from . import models  # noqa
    from .routes import register_routes
    from .services import I18N

    @app.context_processor
    def inject_i18n():
        from flask_login import current_user
        locale = 'en-US'
        if getattr(current_user, 'is_authenticated', False) and getattr(current_user, 'locale', None):
            locale = current_user.locale
        strings = I18N.get(locale, I18N['en-US'])
        return {'t': strings}

    register_routes(app)

    with app.app_context():
        db.create_all()

    return app
