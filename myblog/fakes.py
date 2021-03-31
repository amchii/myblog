import random

from faker import Faker
from sqlalchemy.exc import IntegrityError

from myblog.models import Admin, Category, Post, Comment, Link
from myblog.extensions import db

fake = Faker()


def fake_admin():
    admin = Admin(
        username="admin",
        blog_title="Blog",
        blog_sub_title="No,I'm the real thing.",
        name="Mima kirigoe",
        about="Hi,I am Mima",
    )
    admin.set_password("helloflask")
    db.session.add(admin)
    db.session.commit()


def fake_categories(count=10):
    category = Category(name="Default")
    db.session.add(category)

    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_posts(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            # category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year(),
        )
        post.categories.extend(
            set(
                random.choices(
                    Category.query.all(),
                    k=random.randint(1, Category.query.count() // 3),
                )
            )
        )
        db.session.add(post)
    db.session.commit()


def fake_comments(count=500):
    for i in range(count):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)

    salt = int(count * 0.1)
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=False,
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)

        # 管理员发表的评论
        comment = Comment(
            author="Mima Kirigoe",
            email="Mima@example.com",
            site="example.com",
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            from_admin=True,
            reviewed=True,
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)
    db.session.commit()

    # 回复
    for i in range(salt):
        comment = Comment(
            author=fake.name(),
            email=fake.email(),
            site=fake.url(),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            reviewed=True,
            replied=Comment.query.get(random.randint(1, Comment.query.count())),
            post=Post.query.get(random.randint(1, Post.query.count())),
        )
        db.session.add(comment)
    db.session.commit()


def fake_links():
    twitter = Link(name="Twitter", url="#")
    facebook = Link(name="Facebook", url="#")
    linkedin = Link(name="LinkedIn", url="#")
    google = Link(name="Google+", url="#")
    db.session.add_all([twitter, facebook, linkedin, google])
    db.session.commit()
