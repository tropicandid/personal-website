from app.extensions import flask_app, db
from flask import redirect, render_template, url_for, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.forms import RegisterForm, LoginForm
from app.models import User
import os

SALT_LEN=8 #TODO: MOVE THIS SOMEWHERE ELSE

@flask_app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("get_home"))

    if request.method == 'POST':
        user_exists = db.session.query(User).filter(User.email == request.form['email']).first()

        if user_exists:
            return redirect(
                url_for("login", error="This email is already is associated with an account. Try logging in."))

        invite_code = os.environ.get('REGISTRATION_KEY', 'r3g!$tr4t!0n') #TODO: Make sure you are pulling this from config
        if request.form['inviteCode'] != invite_code:
            form = RegisterForm()
            return render_template("auth/register.html", form=form,
                                   error="Invalid invitation code. Please contact your administrator if you continue to have difficulty.")

        hashed_and_encrypted = generate_password_hash(request.form['password'], method='pbkdf2:sha256',salt_length=SALT_LEN)
        new_user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=hashed_and_encrypted,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("get_home"))
    form = RegisterForm()
    return render_template("auth/register.html", form=form)

@flask_app.route('/login', methods=["GET", "POST"])
def login():
    error = request.args.get('error')
    if request.method == "POST":
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.query(User).filter(User.email == request.form['email']).first()
            if not user:
                return render_template("login.html", form=form,
                                       error="This email does not appear to have an associated account. Do you need to Register a new user?")

            if check_password_hash(user.password, request.form['password']):
                login_user(user)
                return redirect(url_for('get_home', name=user.name))
            else:
                return render_template("login.html", form=form, error='Incorrect password.')
    form = LoginForm()
    return render_template("auth/login.html", form=form, error=error)

@flask_app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_home'))