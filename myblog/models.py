from datetime import datetime

from myblog.extensions import db
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash


class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))
    blog_title = db.Column(db.String(60))
    blog_sub_title = db.Column(db.String(100))
    name = db.Column(db.String(30))
    about = db.Column(db.Text)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)


category_post_table = db.Table(
    "category_post",
    db.Column("category_id", db.Integer, db.ForeignKey("category.id")),
    db.Column("post_id", db.Integer, db.ForeignKey("post.id")),
)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    # posts = db.relationship('Post', back_populates='category')
    posts = db.relationship(
        "Post", secondary=category_post_table, back_populates="categories"
    )

    def delete(self):
        default_category = Category.query.get(1)
        for post in self.posts:
            post.category = default_category
        db.session.delete(self)
        db.session.commit()


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.Text)
    private = db.Column(db.Boolean, default=False)
    can_comment = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    # category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    # category = db.relationship('Category', back_populates='posts')
    categories = db.relationship(
        "Category", secondary=category_post_table, back_populates="posts"
    )
    comments = db.relationship(
        "Comment", back_populates="post", cascade="all, delete-orphan"
    )


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(30))
    email = db.Column(db.String(254))
    site = db.Column(db.String(255))
    body = db.Column(db.Text)
    from_admin = db.Column(db.Boolean, default=False)
    reviewed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"))
    post = db.relationship("Post", back_populates="comments")
    replied_id = db.Column(db.Integer, db.ForeignKey("comment.id"))
    replied = db.relationship("Comment", back_populates="replies", remote_side=[id])
    replies = db.relationship("Comment", back_populates="replied", cascade="all")


class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    url = db.Column(db.String(255))
