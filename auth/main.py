from flask_login import login_user, logout_user, current_user, login_required
from app import db, login_manager
from flask import render_template, request, flash, redirect, url_for, make_response, session
from .forms import SignupForm, LoginForm
from .models import User
from flask import Blueprint

auth = Blueprint('auth', __name__, static_folder='static', template_folder='templates')


@login_manager.user_loader
def load_user(user_id):
    if user_id is not None:
        return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    """Redirect unauthorized users to Login page."""
    flash('You must be logged in to view that page.')
    return redirect(url_for('auth.login'))


@auth.route('/signup', methods=['POST', 'GET'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user is None:
            user = User(name=form.name.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect(url_for('index'))

        return make_response('Пользователь с таким email уже зарегистирован')

    return render_template('signup.html', form=form)


@auth.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return make_response('Вход выполнен')
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(name=form.name.data).first()
        if user and user.check_password(password=form.password.data):
            login_user(user)
            return redirect(url_for('index'))
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)


@login_required
@auth.route('/logout', methods=['POST', 'GET'])
def logout():
    if request.method == 'POST':
        logout_user()
        return redirect(url_for('index'))
    return render_template('logout.html')
