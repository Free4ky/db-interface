from functools import wraps

DOCTOR_DOMAIN = 'hosp.ru'


def role_required(user, role='ANY', ):
    def _wrapper(func):
        @wraps(func)
        def _wrap():
            if user.get_role() == role:
                func()
            else:
                print('PERMISSION DENIED!')

    return _wrapper


def login_required(user, app, role="ANY"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not user.is_authenticated:
                return app.login_manager.unauthorized()
            urole = user.get_role()
            if ((urole != role) and (role != "ANY")):
                return app.login_manager.unauthorized()
            return fn(*args, **kwargs)

        return decorated_view

    return wrapper


def check_role(email):
    i = email.find('@') + 1
    if email[i:] == DOCTOR_DOMAIN:
        return 1
    else:
        return 0
