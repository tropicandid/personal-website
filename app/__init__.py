from app.config import Config
from app.extensions import db, flask_app, login_manager
from flask_ckeditor import CKEditor
from app.forms import RegisterForm, LoginForm, BlogForm, CategoryForm, ContactForm, PortfolioEntryForm
from flask_bootstrap import Bootstrap
from app.email_client import EmailClientInterface
from app.models import User

def init_app(config_class=Config):
    flask_app.config.from_object(config_class)
    Bootstrap(flask_app)
    db.init_app(flask_app)
    login_manager.init_app(flask_app)
    ckeditor = CKEditor(flask_app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    with flask_app.app_context():
        db.create_all()

    # Load Routes
    import app.routes

    return flask_app