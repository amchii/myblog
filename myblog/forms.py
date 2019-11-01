from flask_ckeditor import CKEditorField
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, SelectField, TextAreaField, ValidationError, \
    HiddenField, SelectMultipleField
from wtforms.validators import DataRequired, Length, Email, URL, Optional
from myblog.models import Category


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(8, 128)])
    remember = BooleanField('Remember me')
    submit = SubmitField('Log in')


class SettingForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    blog_title = StringField('Blog Title', validators=[DataRequired(), Length(1, 60)])
    blog_sub_title = StringField('Blog Sub Title', validators=[DataRequired(), Length(1, 100)])
    about = CKEditorField('About Page', validators=[DataRequired()])
    submit = SubmitField()


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(1, 60)])
    # category = SelectField('Categories', coerce=int, default=1)
    categories = SelectMultipleField('Categories', coerce=int, default=1)
    body = CKEditorField('Body', validators=[DataRequired(), Length(max=10000)])
    private = BooleanField('Private')
    submit = SubmitField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.category.choices = [(category.id, category.name) for category in
        #                          Category.query.order_by(Category.name).all()]
        self.categories.choices = [(category.id, category.name) for category in
                                   Category.query.order_by(Category.name).all()]


class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    submit = SubmitField()

    def validate_name(self, field):
        if Category.query.filter_by(name=field.data).first():
            raise ValidationError('Name already in use.')


class CommentForm(FlaskForm):
    author = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(1, 254)])
    site = StringField('Site', validators=[Optional(), URL(), Length(0, 255)])
    body = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField()


class AdminCommentForm(CommentForm):
    author = HiddenField()
    email = HiddenField()
    site = HiddenField()


class LinkForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(1, 30)])
    url = StringField('URL', validators=[DataRequired(), URL(), Length(1, 255)])
    submit = SubmitField()
