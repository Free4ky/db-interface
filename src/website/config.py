TABLES = [
    'schedule',
    'days',
    'doctors',
    'specializations',
    'registrations',
    'visits',
    'patients',
    'results',
    'referral'
]

schedule_join = [
    'schedule',
    'days',
    'doctors',
    'specializations'
]

registration_headings = (
    'Id',
    'Name',
    'Surname',
    'Patronymic',
    'Specialization',
    'Date',
    'Time'
)

schedule_headings = (
    'Id',
    'Name',
    'Surname',
    'Patronymic',
    'Specialization',
    'Day',
    'Date',
    'Time',
    'Cabinet'
)

referral_headings = (
    'Id',
    'Referral name',
    'Start time',
    'End time',
    'Name',
    'Surname',
    'Patronymic',
)

medical_card_headings = (
    'Id',
    'Name',
    'Date',
    'Description'
)

doctor_names_headings = (
    'Id',
    'Name',
    'Surname',
    'Patronymic',
    'Specialization',
    'Cabinet',
)

reg_headings = (
    'id_doctor',
    'id_day',
    'date',
    'time',
    'cabinet'
)

patients_registration_headings = (
    'Id',
    'Name',
    'Surname',
    'Patronymic',
    'Insurance',
    'Date',
    'Time'
)
