from flask import url_for, current_app, render_template
from flask_mail import Message
from bluelog.extensions import mail
from threading import Thread


def _send_async_email(app, message):
    with app.app_context():
        mail.send(message)


def send_email(subject, to, html):
    app = current_app._get_current_object()
    message = Message(subject=subject, recipients=[to], html=html)
    # mail.send(message)
    thr = Thread(target=_send_async_email, args=(app, message))
    thr.start()
    return thr


def send_new_comment_email(post):
    post_url = url_for('blog.show_post', post_id=post.id, _external=True) + '#comments'
    send_email(subject='New comment', to=current_app.config['BLUELOG_EMAIL'],
               html=render_template('email/new_comment.html', post_title=post.title, post_url=post_url))


def send_new_reply_email(comment):
    post_url = url_for('blog.show_post', post_id=comment.post_id, _external=True) + '#comments'
    send_email(subject='New reply', to=comment.email,
               html=render_template('email/new_reply.html', post_title=comment.post.title, post_url=post_url))
