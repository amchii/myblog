from datetime import datetime, timedelta

from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_required, current_user

from myblog.extensions import db, csrf
from myblog.forms import SettingForm, PostForm, CategoryForm, LinkForm
from myblog.models import Post, Category, Comment, Link
from myblog.utils import redirect_back

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    form = SettingForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.blog_title = form.blog_title.data
        current_user.blog_sub_title = form.blog_sub_title.data
        current_user.about = form.about.data
        db.session.commit()
        flash('Setting updated.', 'success')
        return redirect(url_for('blog.index'))
    form.name.data = current_user.name
    form.blog_title.data = current_user.blog_title
    form.blog_sub_title.data = current_user.blog_sub_title
    form.about.data = current_user.about
    return render_template('admin/settings.html', form=form)


@admin_bp.route('/post/manage')
@login_required
def manage_post():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=current_app.config.get(
        'BLUELOG_MANAGE_POST_PER_PAGE', 30))
    posts = pagination.items
    return render_template('admin/manage_post.html', pagination=pagination, posts=posts)


@admin_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        private = form.private.data
        # category = Category.query.get(form.category.data)
        categories = [Category.query.get(i) for i in form.categories.data]
        post = Post(title=title, body=body, private=private, categories=categories)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    return render_template('admin/new_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.private = form.private.data
        # post.category = Category.query.get(form.category.data)
        categories = [Category.query.get(i) for i in form.categories.data]
        post.categories = categories
        db.session.commit()
        flash('Post <%s> updated.' % post.title, 'success')
        return redirect(url_for('blog.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.private.data = post.private
    form.categories.data = [category.id for category in post.categories]
    return render_template('admin/edit_post.html', form=form)


@admin_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash('Post <%s> deleted.' % post.title, 'success')
    return redirect_back()


@admin_bp.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        # 可以对name再做一个防重复验证
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category created.', 'success')
        return redirect(url_for('.manage_category'))

    return render_template('admin/new_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    if category_id == 1:
        flash('You can not edit the default category.', 'warning')
        return redirect(url_for('blog.index'))
    form = CategoryForm()
    category = Category.query.get_or_404(category_id)
    form.name.data = category.name
    if form.validate_on_submit():
        # 可以对name再做一个防重复验证
        category.name = form.name.data
        db.session.commit()
        flash('Category updated.', 'success')
        return redirect(url_for('.manage_category'))

    return render_template('admin/edit_category.html', form=form)


@admin_bp.route('/category/<int:category_id>/delete', methods=['POST'])
@login_required
def delete_category(category_id):
    if category_id == 1:
        flash('You can not delete the default category.', 'warning')
        return redirect(url_for('blog.index'))
    category = Category.query.get_or_404(category_id)
    category.delete()
    flash('Category deleted.', 'success')
    return redirect(url_for('.manage_category'))


@admin_bp.route('/category/manage', methods=['GET', 'POST'])
@login_required
def manage_category():
    categories = Category.query.all()
    return render_template('admin/manage_category.html', categories=categories)


@admin_bp.route('/link/new', methods=['GET', 'POST'])
@login_required
def new_link():
    form = LinkForm()
    if form.validate_on_submit():
        link = Link(name=form.name.data, url=form.url.data)
        db.session.add(link)
        db.session.commit()
        flash('Link created.', 'success')
        return redirect(url_for('.manage_link'))
    return render_template('admin/new_link.html', form=form)


@admin_bp.route('/link/manage', methods=['GET', 'POST'])
@login_required
def manage_link():
    links = Link.query.all()
    return render_template('admin/manage_link.html', links=links)


@admin_bp.route('/set-comment/<int:post_id>', methods=['POST'])
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    post.can_comment = (not post.can_comment)
    flash('Comment %s' % ('Enabled' if post.can_comment else 'Disabled'))
    db.session.commit()
    return redirect_back()


@admin_bp.route('/comment/manage', methods=['GET'])
@login_required
def manage_comment():
    filter_rule = request.args.get('filter', 'all')

    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLUELOG_COMMENT_PER_PAGE']
    if filter_rule == 'unread':
        filtered_comments = Comment.query.filter_by(reviewed=False)
    elif filter_rule == 'admin':
        filtered_comments = Comment.query.filter_by(from_admin=True)
    else:
        filtered_comments = Comment.query

    pagination = filtered_comments.order_by(Comment.timestamp.desc()).paginate(page, per_page=per_page)
    comments = pagination.items
    return render_template('admin/manage_comment.html', comments=comments, pagination=pagination)


@admin_bp.route('/comment/<int:comment_id>/approve', methods=['POST'])
@login_required
def approve_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    comment.reviewed = True
    db.session.commit()
    flash('Comment published.', 'success')
    return redirect_back()


@admin_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()


@admin_bp.route('/timemachine', methods=['GET', 'POST'])
@login_required
@csrf.exempt
def timemachine():
    posts = Post.query.order_by(Post.timestamp.desc()).all()
    if request.method == 'POST':
        for post_id, post_time in request.form.items():
            if post_time:
                utc_time = datetime.strptime(post_time, '%Y-%m-%dT%H:%M') - timedelta(hours=8)
                post = Post.query.get_or_404(int(post_id))
                post.timestamp = utc_time
                db.session.commit()
    return render_template('admin/timemachine.html', posts=posts)
