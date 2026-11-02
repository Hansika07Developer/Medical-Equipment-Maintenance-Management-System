import os
from flask import Flask, redirect, url_for
from config import Config
from .extensions import db, login_manager, csrf, migrate

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    from . import models
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .equipment.routes import equipment_bp
    from .maintenance.routes import maintenance_bp
    from .inventory.routes import inventory_bp
    from .reports.routes import reports_bp
    from .vision.routes import vision_bp

    for bp in (auth_bp, main_bp, equipment_bp, maintenance_bp,
               inventory_bp, reports_bp, vision_bp):
        app.register_blueprint(bp)

    @app.errorhandler(413)
    def too_large(_):
        return "Uploaded file is too large (maximum 10 MB).", 413

    @app.cli.command("init-db")
    def init_db():
        db.create_all()
        print("Database tables created.")

    @app.cli.command("seed-sample-data")
    def seed_sample_data_command():
        from .sample_data import seed_sample_data
        counts = seed_sample_data()
        print("Sample data ready:")
        for key, value in counts.items():
            print(f"- {key}: {value}")

    return app
