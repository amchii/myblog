import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

WIN = sys.platform.startswith("win")
if WIN:
    prefix = "sqlite:///"
else:
    prefix = "sqlite:////"


class BaseConfig(object):
    SECRET_KEY = os.getenv("SECRET_KEY", "a secret string")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_RECORD_QUERIES = True

    CKEDITOR_ENABLE_CSRF = True
    CKEDITOR_FILE_UPLOADER = "admin.upload_image"

    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = ("Blog Admin", MAIL_USERNAME)

    BLOG_EMAIL = os.getenv("BLOG_EMAIL")
    BLOG_POST_PER_PAGE = 10
    BLOG_MANAGE_POST_PER_PAGE = 15
    BLOG_COMMENT_PER_PAGE = 15
    # ('theme name', 'display name')
    BLOG_THEMES = {
        "sketchy": "Sketchy",
        "lux": "LUX",
        "meteria": "Meteria",
        "flatly": "Flatly",
        "black_swan": "Black Swan",
    }
    BLOG_SLOW_QUERY_THRESHOLD = 1

    BLOG_UPLOAD_PATH = os.path.join(basedir, "uploads")
    BLOG_ALLOWED_IMAGE_EXTENSIONS = ["png", "jpg", "jpeg", "gif"]


class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = prefix + os.path.join(basedir, "data-dev.db")
    # EXPLAIN_TEMPLATE_LOADING = True


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", prefix + os.path.join(basedir, "data.db")
    )


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"  # in-memory database


config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
