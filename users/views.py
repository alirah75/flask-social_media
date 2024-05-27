from flask import request, render_template, flash, abort, session, redirect, url_for

from ..app import db
from . import users
from .forms import RegisterForm, LoginForm
from .models import User


@users.route('/')
def index():
    if not session.get('user_id'):
        flash('you are not login.')
        return redirect(url_for('users.login'))
    return render_template('users/index.html', current_user=True)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST':

        if not form.validate_on_submit():
            return render_template('users/register.html', form=form)

        if not form.password.data == form.confirm_password.data:
            flash('password and confirm password must be match')
            return render_template('users/register.html', form=form)

        old_user = User.query.filter(form.username.data == User.username).first()
        if old_user:
            flash('This username is used. Must be unique.')
            return render_template('users/register.html', form=form)

        new_user = User()
        new_user.username = form.username.data
        new_user.set_hash_password(form.password.data)
        new_user.first_name = form.first_name.data
        new_user.last_name = form.last_name.data
        db.session.add(new_user)
        db.session.commit()
        flash('you are registered. successfully.')
        return redirect(url_for('users.login'))

    return render_template('users/register.html', form=form)


@users.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST':
        if not form.validate_on_submit():
            abort(400)
        user = User.query.filter(User.username == form.username.data).first()
        if not user:
            flash('Incorrect username or password', category='error')
            return render_template('users/login.html', form=form)
        if not user.check_password(form.password.data):
            flash('Incorrect username or password', category='error')
            return render_template('users/login.html', form=form)

        session['username'] = user.username
        session['user_id'] = user.id
        return redirect(url_for('posts.index'))

    if session.get('username') is not None:
        return redirect(url_for('users.index'))
    return render_template('users/login.html', form=form)


@users.route('/logout/', methods=['GET'])
def logout():
    session.clear()
    flash('You are logout.')
    return redirect(url_for('users.login'))
