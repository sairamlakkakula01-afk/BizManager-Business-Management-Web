from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app.models.user import User, Role


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[DataRequired(), Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UserCreateForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    role = SelectField('User Role', choices=Role.CHOICES, default=Role.STAFF)
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message="Password must be at least 8 characters.")])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message="Passwords must match.")])
    submit = SubmitField('Create User')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('Username is already taken.')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.strip().lower()).first():
            raise ValidationError('Email address is already registered.')


class UserEditForm(FlaskForm):
    email = StringField('Email Address', validators=[DataRequired(), Email(), Length(max=120)])
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    role = SelectField('User Role', choices=Role.CHOICES)
    is_active = BooleanField('Active Account')
    submit = SubmitField('Update User')

    def __init__(self, original_user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_email(self, field):
        if self.original_user and field.data.strip().lower() != self.original_user.email:
            if User.query.filter_by(email=field.data.strip().lower()).first():
                raise ValidationError('Email address is already registered.')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_new_password = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message="Passwords must match.")])
    submit = SubmitField('Change Password')
