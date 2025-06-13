# -*- encoding: utf-8 -*-


from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)
from werkzeug.security import generate_password_hash, check_password_hash


from apps import db, login_manager
from apps.authentication import blueprint
from apps.authentication.forms import LoginForm, RegisterForm
from apps.authentication.models import Users

from apps.authentication.util import verify_pass


@blueprint.route('/')
def route_default():
    return redirect(url_for('authentication.login'))

# Login & Registration

    
@blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))

    login_form = LoginForm(request.form)
    if 'login' in request.form:
        
        # read form data
        user_name = request.form['user_name']
        user_pw = request.form['user_pw']

        # Locate user
        user = Users.query.filter_by(user_name=user_name).first()
        
        # Check the password
        if user and check_password_hash(user.user_pw, user_pw):
            login_user(user)
            return redirect(url_for('home_blueprint.index'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html', 
                             msg='Invalid username or password', 
                             form=login_form)

    return render_template('accounts/login.html', form=login_form)

@blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_blueprint.index'))
        
    form = RegisterForm(request.form)
    msg = None
    success = False

    if request.method == 'GET': 
        return render_template('accounts/register.html', form=form, msg=msg)

    try:
        if form.validate_on_submit():
            user = Users.query.filter_by(user_name=form.user_name.data).first()
            if user:
                msg = 'Error: Username exists!'
            else:
                user = Users.query.filter_by(user_email=form.user_email.data).first()
                if user:
                    msg = 'Error: Email already registered!'
                else:
                    # Create new user
                    user = Users(**form.data)
                    user.user_pw = generate_password_hash(form.user_pw.data)
                    db.session.add(user)
                    db.session.commit()

                    msg = 'User created successfully!'
                    success = True
        else:
            print(form.errors)
            msg = 'Input error'
    finally:
        db.session.remove()  # <-- 중요: 세션 반납

    return render_template('accounts/register.html', form=form, msg=msg, success=success)


@blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('authentication.login'))


# Errors

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(403)
def access_forbidden(error):
    return render_template('home/page-403.html'), 403


@blueprint.errorhandler(404)
def not_found_error(error):
    return render_template('home/page-404.html'), 404


@blueprint.errorhandler(500)
def internal_error(error):
    return render_template('home/page-500.html'), 500
