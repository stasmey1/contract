from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Length,
)


class SignupForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=3)])
    email = StringField('Email', validators=[Email(message='invalid email')])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   Length(min=8, message='Минимум 8 символов')])
    password_confirmation = PasswordField('Пароль повторно',
                                          validators=[DataRequired(),
                                                      Length(min=8, message='Минимум 8 символов'),
                                                      EqualTo('password', message='Пароли должны совпадать')])
    submit = SubmitField('Регистрация')


class LoginForm(FlaskForm):
    name = StringField('Имя', validators=[DataRequired(), Length(min=5)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')
