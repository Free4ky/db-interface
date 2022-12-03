# routes
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db, db_tables

views = Blueprint('views', __name__)


@views.route('/')
@login_required
def home():
    query_result = db.session.query(
        db_tables['doctors'].name,
        db_tables['doctors'].surname,
        db_tables['doctors'].patronymic,
        db_tables['specializations'].specialization_name,
        db_tables['days'].day,
        db_tables['schedule'].sch_date,
        db_tables['schedule'].start_time
    ).select_from(db_tables['schedule']). \
        join(db_tables['doctors']). \
        join(db_tables['specializations']). \
        join(db_tables['days']).all()
    print(query_result)
    headings = ('Name',
                'Surname',
                'Patronymic',
                'Specialization',
                'Day',
                'Date',
                'Time'
                )
    return render_template('home.html', user=current_user, headings=headings, data=query_result)
