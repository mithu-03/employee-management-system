
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from app.config import Config
from flask_migrate import Migrate

db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()



def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.models import Employee, Department, User
    from app.routes.employees import employee_bp
    from app.routes.departments import department_bp
    from app.routes.auth import auth_bp


    app.register_blueprint(
        employee_bp,
        url_prefix="/api/employees"
    )

    app.register_blueprint(
        department_bp,
        url_prefix="/api/departments"
    )

    app.register_blueprint(
        auth_bp,
        url_prefix="/api/auth"
    )


    return app

