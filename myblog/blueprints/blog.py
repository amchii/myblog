from flask import (
    render_template,
    Blueprint,
    request,
    current_app,
    url_for,
    flash,
    redirect,
    abort,
    make_response,
)

from myblog.extensions import db, csrf
from myblog.emails import send_new_comment_email, send_new_reply_email
from myblog.models import Post, Category, Comment
from myblog.forms import CommentForm, AdminCommentForm
from myblog.utils import redirect_back
from flask_login import current_user, login_required

blog_bp = Blueprint("blog", __name__)


@blog_bp.route("/", defaults={"page": 1})
@blog_bp.route("/page/<int:page>")
def index(page):
    per_page = current_app.config["BLOG_POST_PER_PAGE"]
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, per_page=per_page
    )
    posts = pagination.items
    return render_template("blog/index.html", pagination=pagination, posts=posts)


@blog_bp.route("/about")
def about():
    return render_template("blog/about.html")


@blog_bp.route("/category/<int:category_id>")
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("BLOG_POST_PER_PAGE", 10)
    pagination = (
        Post.query.with_parent(category)
        .order_by(Post.timestamp.desc())
        .paginate(page, per_page=per_page)
    )
    posts = pagination.items
    return render_template(
        "blog/category.html", category=category, posts=posts, pagination=pagination
    )


@blog_bp.route("/post/<int:post_id>", methods=["GET", "POST"])
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.private and not current_user.is_authenticated:
        flash("你没有权限访问该文章！", "warning")
        return redirect(url_for(".index"))
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("BLOG_COMMENT_PER_PAGE", 15)
    pagination = (
        Comment.query.with_parent(post)
        .filter_by(reviewed=True)
        .order_by(Comment.timestamp.asc())
        .paginate(page, per_page=per_page)
    )
    comments = pagination.items

    if current_user.is_authenticated:
        form = AdminCommentForm()
        form.author.data = current_user.name
        form.email.data = current_app.config["BLOG_EMAIL"]
        form.site.data = url_for(".index")
        from_admin = True
        reviewed = True
    else:
        form = CommentForm()
        from_admin = False
        reviewed = False

    if form.validate_on_submit():
        author = form.author.data
        email = form.email.data
        site = form.site.data
        body = form.body.data
        comment = Comment(
            author=author,
            email=email,
            site=site,
            body=body,
            from_admin=from_admin,
            post=post,
            reviewed=reviewed,
        )
        replied_id = request.args.get("reply")
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
            send_new_reply_email(replied_comment)

        db.session.add(comment)
        db.session.commit()
        if current_user.is_authenticated:
            flash("Comment published.", "success")
        else:
            flash("Thanks, your comment will be published after reviewed.", "info")
            send_new_comment_email(post)
        return redirect(url_for(".show_post", post_id=post_id))
    return render_template(
        "blog/post.html", post=post, pagination=pagination, comments=comments, form=form
    )


@blog_bp.route("/reply/comment/<int:comment_id>")
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash("Comment is disbale.", "warning")
        return redirect(url_for(".show_post", post_id=comment.post_id))
    return redirect(
        url_for(
            ".show_post",
            post_id=comment.post_id,
            reply=comment_id,
            author=comment.author,
        )
        + "#comment-form"
    )


@blog_bp.route("/change-theme/<theme_name>")
def change_theme(theme_name):
    if theme_name not in current_app.config["BLOG_THEMES"].keys():
        abort(404)
    response = make_response(redirect_back())
    response.set_cookie("theme", theme_name, max_age=60 * 60 * 24 * 30)
    return response


@blog_bp.route("/email")
def send_email():
    post = Post.query.get(1)
    send_new_comment_email(post)
    return "email is sending..."


@blog_bp.route("/mytext", methods=["GET", "POST"])
@login_required
@csrf.exempt
def mytext():
    if request.method == "POST":
        text = request.json["text"]
        with open("mytext", "w", encoding="utf-8") as f:
            f.write(text)
        return "提交成功"
    with open("mytext", "r", encoding="utf-8") as f:
        text = f.read()
    return render_template("blog/text.html", text=text)
