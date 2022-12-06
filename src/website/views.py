# routes
import json
from datetime import date, time

from flask import Blueprint, render_template, request, jsonify, flash
from flask_login import login_required, current_user

from . import db, db_tables
from .config import registration_headings, schedule_headings, referral_headings, medical_card_headings, \
    doctor_names_headings, reg_headings

from datetime import datetime

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

@views.route('/schedule')
@login_required
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


data_dict = {}


@views.route('/get_row', methods=['GET', 'POST'])
def get_row():
    global data_dict
    data_dict = json.loads(request.data)
    return jsonify({})


@views.route('/confirm', methods=['GET'])
@login_required
def confirm():
    headings, values = data_dict.keys(), data_dict.values()
    headings, values = list(headings), list(values)
    print(headings, values)
    return render_template('confirm.html', user=current_user, headings=headings, data=values)


@views.route('/add-registration', methods=['POST'])
@login_required
def add_registration():
    data = json.loads(request.data)
    # res = db.session.query(db_tables['days'].id_day).where(data['Day'] == db_tables['days'].day).first()
    # print(f'QUEEERY {res}')
    if data.get('answer'):
        new_registration = db_tables['registrations'](
            reg_date=data_dict['Date'],
            reg_time=data_dict['Time'],
            id_doctor=data_dict['Id'],
            id_day=db.session.query(db_tables['days'].id_day).where(data_dict['Day'] == db_tables['days'].day).first()[
                0],
            id_patient=current_user.get_id(),
            disease_descr='',
            cabinet=data_dict['Cabinet'],
        )
        db.session.add(new_registration)
        db.session.commit()
        flash('Registration is completed!', category='success')
    else:
        flash('Registration canceled!', category='error')
    return jsonify({})


@views.route('/api/reg-query')
def reg_query():
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
        join(db_tables['specializations']).where(current_user.get_id() == db_tables['registrations'].id_patient).all()
    return to_dict(query_result, registration_headings)


@views.route('/registrations')
@login_required
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


@login_required
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


@login_required
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


@login_required
@views.route('/specializations')
def specializations():
    result_query = db.session.query(
        db_tables['specializations'].specialization_name
    ).select_from(db_tables['specializations']).all()
    result_query = list(map(lambda x: x[0], result_query))
    return render_template('specializations.html', user=current_user, specializations=result_query)


specialization_name = None


@views.route('/fetch-specialization', methods=['POST'])
def fetch_specialization():
    global specialization_name
    data = json.loads(request.data)
    print(data)
    specialization_name = data.get('specialization_name')
    return jsonify({})


@login_required
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
        where(specialization_name == db_tables['specializations'].specialization_name).all()
    query_result = list(set(query_result))
    print([dict(zip(doctor_names_headings, x)) for x in query_result])
    return render_template("doctor_names.html", user=current_user,
                           doctors=[dict(zip(doctor_names_headings, x)) for x in query_result])


doctor_id = None


@login_required
@views.route('/fetch-doctors', methods=['POST'])
def fetch_doctors():
    global doctor_id
    data = json.loads(request.data)
    doctor_id = data.get('id_doctor')
    return jsonify({})


@views.route('/date-picker')
def date_picker():
    query_result = db.session.query(
        db_tables['schedule'].sch_date
    ).where(db_tables['schedule'].id_doctor == doctor_id).all()
    return render_template(
        'date.html',
        user=current_user,
        available_dates=list(set(map(lambda x: str(x[0]), query_result)))
    )


current_date = None


@login_required
@views.route('/fetch-date', methods=['POST'])
def fetch_date():
    global current_date
    data = json.loads(request.data)
    current_date = data.get('date')
    current_date = datetime.strptime(current_date, "%d/%m/%Y").strftime("%Y-%m-%d")
    print(current_date)
    return jsonify({})


@login_required
@views.route('/time-picker')
def time_picker():
    query_result = db.session.query(
        db_tables['schedule'].start_time
    ).where(
        db_tables['schedule'].id_doctor == doctor_id and db_tables['schedule'].sch_date == current_date
    ).all()
    print(list(set(map(lambda x: str(x[0]), query_result))))
    return render_template(
        'time.html',
        user=current_user,
        available_time=list(set(map(lambda x: str(x[0]), query_result)))
    )


current_time = None


@login_required
@views.route('/fetch-time', methods=['POST'])
def fetch_time():
    global current_time
    data = json.loads(request.data)
    current_time = data.get('time')
    query_result = db.session.query(
        db_tables['schedule'].id_doctor,
        db_tables['schedule'].id_day,
        db_tables['schedule'].sch_date,
        db_tables['schedule'].start_time,
        db_tables['schedule'].cabinet,
    ).where(
        db_tables['schedule'].id_doctor == doctor_id and
        db_tables['schedule'].sch_date == current_date and
        db_tables['schedule'].start_time == current_time
    ).first()
    query_result = tuple(map(lambda x: str(x), query_result))
    query_result = dict(zip(reg_headings, query_result))
    new_registration = db_tables['registrations'](
        reg_date=query_result['date'],
        reg_time=query_result['time'],
        id_doctor=query_result['id_doctor'],
        id_day=query_result['id_day'],
        id_patient=current_user.get_id(),
        disease_descr='',
        cabinet=query_result['cabinet']
    )
    db.session.add(new_registration)
    db.session.commit()
    flash('Registration is completed!', category='success')
    return jsonify({})
