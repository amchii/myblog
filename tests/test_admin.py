from flask import url_for

from myblog.models import Post, Category, Link, Comment
from myblog.extensions import db

from tests.base import BaseTestCase


class AdminTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.login()

        category = Category(name="Default")
        post = Post(title="Hello", category=category, body="Blah...")
        comment = Comment(body="A comment", post=post, from_admin=True)
        link = Link(name="GitHub", url="https://github.com/greyli")
        db.session.add_all([category, post, comment, link])
        db.session.commit()

    def test_new_post(self):
        response = self.client.get(url_for("admin.new_post"))
        data = response.get_data(as_text=True)
        self.assertIn("New Post", data)

        response = self.client.post(
            url_for("admin.new_post"),
            data=dict(
                title="Something",
                category=1,
                body="Hello, world.",
            ),
            follow_redirects=True,
        )
        data = response.get_data(as_text=True)
        self.assertIn("Post created.", data)
        self.assertIn("Something", data)
        self.assertIn("Hello, world.", data)
