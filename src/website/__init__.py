from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .config import TABLES
from sqlalchemy.ext.automap import automap_base
from flask_login import LoginManager, UserMixin

db = SQLAlchemy()
db_tables = {}
app = Flask(__name__)
with app.app_context():
    Base = automap_base()


class Login(Base, UserMixin):
    __tablename__ = 'login'

    def get_id(self):
        return self.id_login


def instantiate_tables():
    global db_tables, Base
    with app.app_context():
        Base.prepare(autoload_with=db.engine, reflect=True)
        for table in TABLES:
            db_tables[table] = getattr(Base.classes, table)


def create_app():
    app.config['SECRET_KEY'] = 'asdfasdgsd421a'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:qwerty@localhost:3306/hospital2'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    instantiate_tables()

    # stmt = select(user_table).where(user_table.c.name == "spongebob")
    # import blueprints
    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return db.session.query(Login).get(int(id))

    # for r in res:
    #     print(r)

    return app
