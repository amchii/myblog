from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_wtf import CSRFProtect
from flask_migrate import Migrate

db = SQLAlchemy()
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
ckeditor = CKEditor()
login_manager = LoginManager()
csrf = CSRFProtect()
migrate = Migrate()


@login_manager.user_loader
def load_user(user_id):
    from myblog.models import Admin
    user = Admin.query.get(int(user_id))
    return user


login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'
login_manager.login_message = 'You need to log in.'
