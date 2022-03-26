from app import app, db
from flask import render_template, redirect, url_for, request, flash, g, session, make_response
import os
from werkzeug.utils import secure_filename
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from .models import User
from .forms import LoginForm, RegisterForm
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import random


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# check session
@app.before_request
def before_request():
    g.user = None

    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()
        g.user = user


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)


# home page
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in, please log out to register another account', 'warning')
        return redirect(url_for('dashboard'))
    form = RegisterForm()

    if form.validate_on_submit():
        user1 = User.query.filter_by(username=form.username.data).first()
        if user1 is not None:
            message = 'Username already exists'
            flash(message, 'warning')
            app.logger.error('Registeration failed: %s' % message)
            return redirect(url_for('register'))
        # unique email
        user2 = User.query.filter_by(email=form.email.data).first()
        if user2 is not None:
            message = 'Email has been already registered'
            flash(message, 'warning')
            app.logger.error('Registeration failed: %s' % message)
            return redirect(url_for('register'))
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password, code=form.code.data)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user, remember=False)
        g.user = new_user
        session['user_id'] = new_user.id
        message = 'Successfully registeration'
        app.logger.info('%s: %s' % (message, new_user.username))
        return redirect(url_for('dashboard'))
        # return render_template('dashboard.html')
    for error in form.errors:
        if error == 'username':
            message = 'At least 4 letters for username'
            flash(message, 'warning')
        if error == 'password':
            message = 'At least 8 letters for password'
            flash(message, 'warning')
        if error == 'code':
            message = 'At least 4 letters for code'
            flash(message, 'warning')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('You are already logged in, please log out to login another account', 'warning')
        return redirect(url_for('dashboard'))
    session.pop('user_id', None)
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                g.user = user
                session['user_id'] = user.id
                message = 'Successfully login'
                app.logger.info('%s: %s' %(message, user.username))
                return render_template('dashboard.html', user=current_user)

            message = 'Wrong password!'
            flash(message, 'warning')
            app.logger.warning('Login failed: %s', message)
            return render_template('login.html', form=form)

        message = "Invalid username!"
        flash(message, 'warning')
        app.logger.warning('Login failed: %s', message)
        return render_template('login.html', form=form)

    for error in form.errors:
        if error == 'username':
            message = 'At least 4 letters for username'
            flash(message, 'warning')
        if error == 'password':
            message = 'At least 8 letters for password'
            flash(message, 'warning')
    return render_template('login.html', form=form)


# load user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/logout')
@login_required
def logout():
    app.logger.info('Log out user: %s' %current_user.username)
    logout_user()
    return redirect(url_for('home'))


@app.route('/changePassword')
@login_required
def changePassword():
    return render_template('changePass.html')


@app.route('/changePass', methods=['GET', 'POST'])
@login_required
def changePass():
    username = request.form.get('username')
    if username and len(username) < 4:
        flash('At least 4 letters for username', 'warning')
        return redirect(url_for('changePassword'))
    oldpass = request.form.get('oldpass')
    if oldpass and len(oldpass) < 8:
        flash('At least 8 letters for password', 'warning')
        return redirect(url_for('changePassword'))
    newPass = request.form.get('newPass')
    if newPass and len(newPass) < 8:
        flash('At least 8 letters for password', 'warning')
        return redirect(url_for('changePassword'))
    if username == current_user.username:
        if check_password_hash(current_user.password, oldpass):
            hashed_password = generate_password_hash(newPass, method='sha256')
            current_user.password = hashed_password
            db.session.commit()
            app.logger.info('Successfully change password: %s' %current_user.username)
            return redirect(url_for('dashboard'))
       
        message = "Wrong password"
        flash(message, 'warning')
        app.logger.warning('Change password failed: %s' %message)
        return redirect(url_for('changePassword'))
    
    message = "Wrong username"
    flash(message, 'warning')
    app.logger.warning('Change password failed: %s' %message)
    return redirect(url_for('changePassword'))