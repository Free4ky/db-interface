# routes
import json
from datetime import date, time, datetime
from sqlalchemy import and_
from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import current_user
from . import db, db_tables
from .config import registration_headings, schedule_headings, referral_headings, medical_card_headings, \
    doctor_names_headings, reg_headings, patients_registration_headings

from src.utils import login_required
from . import app, ROLES, Login
from flask import session
from collections import  OrderedDict
views = Blueprint('views', __name__)


@views.route('/')
@login_required(user=current_user, app=app, role=ROLES['user'])
def home():
    return render_template('home.html', user=current_user)


@views.route('/schedule')
@login_required(user=current_user, app=app, role=ROLES['user'])
def schedule():
    return render_template('schedule.html', user=current_user, headings=schedule_headings)


def to_dict(query_result, headings):
    for i in range(len(query_result)):
        query_result[i] = list(query_result[i])
        for j in range(len(query_result[i])):
            if isinstance(query_result[i][j], date) or isinstance(query_result[i][j], time):
                query_result[i][j] = str(query_result[i][j])
    return {'data': [dict(zip(headings, item)) for item in query_result]}


@views.route('/api/data')
def data():
    query_result = db.session.query(
        db_tables['doctors'].id_doctor,
        db_tables['doctors'].name,
        db_tables['doctors'].surname,
        db_tables['doctors'].patronymic,
        db_tables['specializations'].specialization_name,
        db_tables['days'].day,
        db_tables['schedule'].sch_date,
        db_tables['schedule'].start_time,
        db_tables['schedule'].cabinet
    ).select_from(db_tables['schedule']). \
        join(db_tables['doctors']). \
        join(db_tables['specializations']). \
        join(db_tables['days']).all()
    return to_dict(query_result, schedule_headings)


@views.route('/get_row', methods=['GET', 'POST'])
def get_row():
    session['data_dict'] = json.loads(request.data)
    return jsonify({})


@views.route('/confirm', methods=['GET'])
@login_required(user=current_user, app=app, role=ROLES['user'])
def confirm():
    ordered = OrderedDict((k, session['data_dict'][k]) for k in registration_headings)
    headings, values = ordered.keys(), ordered.values()
    headings, values = list(headings), list(values)
    return render_template('confirm.html', user=current_user, headings=headings, data=values)


@views.route('/add-registration', methods=['POST'])
@login_required(user=current_user, app=app, role=ROLES['user'])
def add_registration():
    data = json.loads(request.data)
    # res = db.session.query(db_tables['days'].id_day).where(data['Day'] == db_tables['days'].day).first()
    # print(f'QUEEERY {res}')
    patient_id = db.session.query(
        db_tables['patients'].id_patient
    ).select_from(db_tables['patients']).join(Login).filter(Login.id_login == current_user.get_id()).first()[0]
    if data.get('answer'):
        new_registration = db_tables['registrations'](
            reg_date=session['data_dict']['Date'],
            reg_time=session['data_dict']['Time'],
            id_doctor=session['data_dict']['Id'],
            id_day=db.session.query(db_tables['days'].id_day).where(
                session['data_dict']['Day'] == db_tables['days'].day).first()[0],
            id_patient=patient_id,
            disease_descr='',
            cabinet=session['data_dict']['Cabinet'],
        )

        db.session.add(new_registration)
        db.session.commit()
        flash('Registration is completed!', category='success')
    else:
        flash('Registration canceled!', category='error')
    return jsonify({})


@views.route('/api/reg-query')
def reg_query():
    patient_id = db.session.query(
        db_tables['patients'].id_patient
    ).select_from(db_tables['patients']).join(Login).filter(Login.id_login == current_user.get_id()).first()[0]
    query_result = db.session.query(
        db_tables['registrations'].id_registration,
        db_tables['doctors'].name,
        db_tables['doctors'].surname,
        db_tables['doctors'].patronymic,
        db_tables['specializations'].specialization_name,
        db_tables['registrations'].reg_date,
        db_tables['registrations'].reg_time
    ).select_from(db_tables['registrations']). \
        join(db_tables['doctors']). \
        join(db_tables['specializations']).where(patient_id == db_tables['registrations'].id_patient).all()
    return to_dict(query_result, registration_headings)


@views.route('/registrations')
@login_required(user=current_user, app=app, role=ROLES['user'])
def registrations():
    return render_template('registrations.html', user=current_user, headings=registration_headings)


@views.route('/delete-registration', methods=['POST'])
def delete_registration():
    data = json.loads(request.data)
    obj_to_delete = db.session.query(db_tables['registrations']).filter(
        db_tables['registrations'].id_registration == data['Id']).first()
    db.session.delete(obj_to_delete)
    db.session.commit()
    return jsonify({})


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/referral')
def referral():
    return render_template('referral.html', user=current_user, headings=referral_headings)


@views.route('/api/ref-query')
def referral_query():
    query_result = db.session.query(
        db_tables['referral'].id_referral,
        db_tables['referral'].name,
        db_tables['referral'].start_time,
        db_tables['referral'].end_time,
        db_tables['doctors'].name,
        db_tables['doctors'].surname,
        db_tables['doctors'].patronymic,
    ).select_from(db_tables['referral']).join(db_tables['doctors']).where(
        current_user.get_id() == db_tables['referral'].id_patient).all()
    return to_dict(query_result, referral_headings)


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/medical-card')
def medical_card():
    return render_template('medical_card.html', user=current_user, headings=medical_card_headings)


@views.route('/api/med-query')
def medical_card_query():
    query_result = db.session.query(
        db_tables['referral'].id_referral,
        db_tables['referral'].name,
        db_tables['results'].result_date,
        db_tables['results'].result_info
    ).select_from(db_tables['results']).join(db_tables['referral']).where(
        current_user.get_id() == db_tables['referral'].id_patient).all()
    return to_dict(query_result, medical_card_headings)


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/specializations')
def specializations():
    result_query = db.session.query(
        db_tables['specializations'].specialization_name
    ).select_from(db_tables['specializations']).all()
    result_query = list(map(lambda x: x[0], result_query))
    return render_template('specializations.html', user=current_user, specializations=result_query)


@views.route('/fetch-specialization', methods=['POST'])
def fetch_specialization():
    data = json.loads(request.data)
    print(data)
    session['specialization_name'] = data.get('specialization_name')
    return jsonify({})


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/doctor-names', methods=['GET', 'POST'])
def doctor_names():
    query_result = db.session.query(
        db_tables['doctors'].id_doctor,
        db_tables['doctors'].name,
        db_tables['doctors'].surname,
        db_tables['doctors'].patronymic,
        db_tables['specializations'].specialization_name,
        db_tables['schedule'].cabinet
    ).select_from(db_tables['doctors']). \
        join(db_tables['specializations']). \
        join(db_tables['schedule']). \
        where(session['specialization_name'] == db_tables['specializations'].specialization_name).all()
    query_result = list(set(query_result))
    print(query_result)
    print('IM HERE', [dict(zip(doctor_names_headings, x)) for x in query_result])
    return render_template("doctor_names.html", user=current_user,
                           doctors=[dict(zip(doctor_names_headings, x)) for x in query_result])


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/fetch-doctors', methods=['POST'])
def fetch_doctors():
    data = json.loads(request.data)
    session['doctor_id'] = data.get('id_doctor')
    return jsonify({})


@views.route('/date-picker')
def date_picker():
    query_result = db.session.query(
        db_tables['schedule'].sch_date
    ).where(db_tables['schedule'].id_doctor == session['doctor_id']).all()
    return render_template(
        'date.html',
        user=current_user,
        available_dates=list(set(map(lambda x: str(x[0]), query_result)))
    )


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/fetch-date', methods=['POST'])
def fetch_date():
    data = json.loads(request.data)
    current_date = data.get('date')
    session['current_date'] = datetime.strptime(current_date, "%m/%d/%Y").strftime("%Y-%m-%d")
    return jsonify({})


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/time-picker')
def time_picker():
    test_query = db.session.query(
        db_tables['schedule'].start_time
    ).all()
    print(test_query)
    query_result = db.session.query(
        db_tables['schedule'].start_time
    ).filter(
        and_(db_tables['schedule'].sch_date == date.fromisoformat(session['current_date']),
             db_tables['schedule'].id_doctor == session['doctor_id'])
    ).all()
    print(query_result)
    print(list(set(map(lambda x: str(x[0]), query_result))))
    return render_template(
        'time.html',
        user=current_user,
        available_time=list(set(map(lambda x: str(x[0]), query_result)))
    )


@login_required(user=current_user, app=app, role=ROLES['user'])
@views.route('/fetch-time', methods=['POST'])
def fetch_time():
    data = json.loads(request.data)
    session['current_time'] = data.get('time')
    query_result = db.session.query(
        db_tables['schedule'].id_doctor,
        db_tables['schedule'].id_day,
        db_tables['schedule'].sch_date,
        db_tables['schedule'].start_time,
        db_tables['schedule'].cabinet,
    ).filter(
        and_(db_tables['schedule'].id_doctor == session['doctor_id'],
             db_tables['schedule'].sch_date == date.fromisoformat(session['current_date']),
             db_tables['schedule'].start_time == time.fromisoformat(session['current_time']))
    ).first()
    query_result = tuple(map(lambda x: str(x), query_result))
    query_result = dict(zip(reg_headings, query_result))
    patient_id = db.session.query(
        db_tables['patients'].id_patient
    ).select_from(db_tables['patients']).join(Login).filter(Login.id_login == current_user.get_id()).first()[0]
    new_registration = db_tables['registrations'](
        reg_date=query_result['date'],
        reg_time=query_result['time'],
        id_doctor=query_result['id_doctor'],
        id_day=query_result['id_day'],
        id_patient=patient_id,
        disease_descr='',
        cabinet=query_result['cabinet']
    )
    db.session.add(new_registration)
    db.session.commit()
    flash('Registration is completed!', category='success')
    return jsonify({})


@views.route('/doctors_home')
@login_required(user=current_user, app=app, role=ROLES['doctor'])
def doctor_home():
    return render_template("doctors_registrations.html", user=current_user, headings=patients_registration_headings)


@views.route('/api/patients-table')
def get_patients_table():
    id_doctor = db.session.query(
        db_tables['doctors'].id_doctor
    ).select_from(db_tables['doctors']). \
        join(Login). \
        where(current_user.get_id() == Login.id_login).first()[0]
    query_result = db.session.query(
        db_tables['registrations'].id_registration,
        db_tables['patients'].name,
        db_tables['patients'].surname,
        db_tables['patients'].patronymic,
        db_tables['patients'].insurance_policy,
        db_tables['registrations'].reg_date,
        db_tables['registrations'].reg_time,
    ).select_from(db_tables['registrations']). \
        join(db_tables['patients']). \
        where(db_tables['registrations'].id_doctor == id_doctor).all()
    return to_dict(query_result, patients_registration_headings)


@login_required(user=current_user, app=app, role='ANY')
@views.route('/profile')
def profile():
    if current_user.get_role() == ROLES['user']:
        query_result = db.session.query(
            db_tables['patients'].name,
            db_tables['patients'].surname,
            db_tables['patients'].patronymic,
            db_tables['patients'].insurance_policy,
            Login.email
        ).select_from(db_tables['patients']).join(Login).where(Login.id_login == current_user.get_id()).first()
        headings = (
            'Name',
            'Surname',
            'Patronymic',
            'Insurance',
            'email'
        )
    elif current_user.get_role() == ROLES['doctor']:
        query_result = db.session.query(
            db_tables['doctors'].id_doctor,
            db_tables['doctors'].name,
            db_tables['doctors'].surname,
            db_tables['doctors'].patronymic,
            db_tables['specializations'].specialization_name,
            Login.email
        ).select_from(db_tables['doctors']). \
            join(Login). \
            join(db_tables['specializations']). \
            where(Login.id_login == current_user.get_id()).first()

        headings = (
            'Id',
            'Name',
            'Surname',
            'Patronymic',
            'Specialization',
            'email'
        )
    query_result = [query_result]
    data = to_dict(query_result, headings=headings)
    data = data['data'][0]
    return render_template('profile.html', user=current_user, data=data)
