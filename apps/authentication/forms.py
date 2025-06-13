# -*- encoding: utf-8 -*-


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from apps.authentication.models import Users

# login and registration


class LoginForm(FlaskForm):
    user_name = StringField('Username', validators=[DataRequired()])
    user_pw = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    user_name = StringField('Username', validators=[
        DataRequired(),
        Length(min=3, max=64, message='Username must be between 3 and 64 characters')
    ])
    user_email = StringField('Email', validators=[
        DataRequired(),
        Email(message='Please enter a valid email address')
    ])
    user_pw = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('user_pw', message='Passwords must match')
    ])
    submit = SubmitField('Register')

    def validate_user_name(self, user_name):
        user = Users.query.filter_by(user_name=user_name.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')

    def validate_user_email(self, user_email):
        user = Users.query.filter_by(user_email=user_email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')
