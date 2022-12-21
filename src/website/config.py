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
    'Имя',
    'Фамилия',
    'Отчество',
    'Специализация',
    'Дата',
    'Время'
)

schedule_headings = (
    'Id',
    'Имя',
    'Фамилия',
    'Отчество',
    'Специализация',
    'День',
    'Дата',
    'Время',
    'Кабинет'
)

referral_headings = (
    'Id',
    'Название',
    'Дата начала',
    'Дата окончания',
    'Имя',
    'Фамилия',
    'Отчество',
)

medical_card_headings = (
    'Id',
    'Название',
    'Дата',
    'Описание'
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
    'Имя',
    'Фамилия',
    'Отчество',
    'Полис страхования',
    'Дата',
    'Время'
)
