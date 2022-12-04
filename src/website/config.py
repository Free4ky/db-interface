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
