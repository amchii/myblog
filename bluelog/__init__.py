# !/usr/bin/env python
# -*- coding: utf-8 -*-
# DateTime: 2019/5/8 9:23
import os

import click
from flask import Flask, render_template
from flask_login import current_user
from flask_wtf.csrf import CSRFError

from bluelog.blueprints.admin import admin_bp
from bluelog.blueprints.blog import blog_bp
from bluelog.blueprints.auth import auth_bp
from bluelog.models import Admin, Category, Comment, Link
from bluelog.settings import config
from bluelog.extensions import bootstrap, db, moment, ckeditor, mail, login_manager, csrf, migrate

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'development')

    app = Flask('bluelog')
    print('in app: ' + __name__)
    app.config.from_object(config[config_name])
    register_logging(app)
    register_extensions(app)
    register_blueprints(app)
    register_errors(app)
    register_commands(app)
    register_shell_context(app)
    register_template_context(app)

    return app


def register_logging(app):
    pass


def register_extensions(app):
    bootstrap.init_app(app)
    db.init_app(app)
    moment.init_app(app)
    ckeditor.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    app.register_blueprint(blog_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')


def register_shell_context(app: Flask):
    @app.shell_context_processor
    def make_shell_context():
        return dict(db=db, mail=mail)


def register_template_context(app: Flask):
    @app.context_processor
    def make_template_context():
        admin = Admin.query.first()
        categories = Category.query.order_by(Category.name).all()
        links = Link.query.order_by(Link.name).all()
        if current_user.is_authenticated:
            unread_comments = Comment.query.filter_by(reviewed=False).count()
        else:
            unread_comments = None
        return dict(admin=admin, categories=categories, links=links, unread_comments=unread_comments)


def register_errors(app: Flask):
    @app.errorhandler(400)
    def bad_request(e):
        return render_template('errors/400.html'), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return render_template('errors/400.html', description=e.description), 400


def register_commands(app: Flask):
    # flask forge
    @app.cli.command()
    @click.option('--category', default=10, help='Quantity of categories, default is 10.')
    @click.option('--post', default=50, help='Quantity of posts, default is 50.')
    @click.option('--comment', default=500, help='Quantity of comments, default is 500.')
    def forge(category, post, comment):
        """Generates the fake categories, posts, comments and links."""
        from bluelog.fakes import fake_admin, fake_categories, fake_posts, fake_comments, fake_links

        db.drop_all()
        db.create_all()

        click.echo('Generating the administrator...')
        fake_admin()

        click.echo('Generating %d categories...' % category)
        fake_categories(category)

        click.echo('Generating %d posts...' % post)
        fake_posts(post)

        click.echo('Generating %d comments...' % comment)
        fake_comments(comment)

        click.echo('Generating links...')
        fake_links()

        click.echo('Done.')

    # flask init
    @app.cli.command()
    @click.option('--username', prompt=True, help='The username used to login.')
    # 可以使用@click.password_option()
    @click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True,
                  help='The password used to login.')
    def init(username, password):
        """Building Bluelog, just for you."""
        click.echo('Initializing the database...')
        db.create_all()

        admin = Admin.query.first()
        if admin:
            click.echo('The administrator already exists, updating... ')
            admin.username = username
            admin.set_password(password)
        else:
            click.echo('Creating the temporary administrator account...')
            admin = Admin(
                username=username,
                blog_title='Bluelog',
                blog_sub_title="No, I'm the real thing.",
                name='Admin',
                about='Anything about you.'
            )
            admin.set_password(password)
            db.session.add(admin)

        category = Category.query.first()
        if not category:
            click.echo('Creating the default category... ')
            category = Category(name='Default')
            db.session.add(category)

        db.session.commit()
        click.echo('Done.')
