from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from . import db_tables, db
from . import Login
from flask_login import login_user, logout_user, current_user
from src.utils import login_required, check_role
from . import app, ROLES

auth = Blueprint('auth', __name__)


def check_existence(email):
    # res = db.session.query(table).where(table.email == email)
    # return len(list(res)) > 0
    user = db.session.query(Login).filter_by(email=email).first()
    # user = Login.query.filter_by(email=email).first()
    return user


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = check_existence(email)
        if user:
            if check_password_hash(user.password, password):
                flash('Вход произведен!', category='success')
                login_user(user, remember=True)
                if user.role == ROLES['user']:
                    return redirect(url_for('views.home'))
                elif user.role == ROLES['doctor']:
                    return redirect(url_for('views.doctor_home'))
            else:
                flash('Неверный пароль!', category='error')
        else:
            flash('Учетная запись не существует!', category='error')
    return render_template('login.html', user=current_user)


@auth.route('/logout')
@login_required(user=current_user, app=app, role='ANY')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('firstName')
        surname = request.form.get('surname')
        patronymic = request.form.get('patronymic')
        insurance_policy = request.form.get('insurance')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        role = check_role(email)

        user = check_existence(email)
        if user:
            flash('Учетная запись уже существует!', category='error')
        elif len(email) < 4:
            flash('Почта должна быть длиннее четырех символов', category='error')
        elif len(name) < 2:
            flash('Имя должно быть длиннее одного символа', category='error')
        elif password1 != password2:
            flash('Пароли не совпадают', category='error')
        elif len(password1) < 7:
            flash('Пароль должен содержать более 7 символов', category='error')
        elif len(insurance_policy) != 16:
            flash('Ошибка в полисе страхования!', category='error')
        else:
            # add user
            new_login = Login(
                email=email,
                role=role,
                password=generate_password_hash(
                    password1,
                    method='sha256'
                )
            )
            db.session.add(new_login)
            db.session.commit()
            if email[email.find('@') + 1:] != 'hosp.ru':
                new_patient = db_tables['patients'](
                    name=name,
                    surname=surname,
                    patronymic=patronymic,
                    insurance_policy=insurance_policy,
                    login_id=new_login.id_login
                )
                db.session.add(new_patient)
                db.session.commit()
            # if user:
            #     login_user(user, remember=True)
            flash('Учетная запись создана!', category='success')
            return redirect(url_for('views.home'))
    return render_template('sign_up.html', user=current_user)
