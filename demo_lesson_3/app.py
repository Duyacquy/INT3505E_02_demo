from flask import Flask
from soa_lib.extensions import db
from werkzeug.security import generate_password_hash
import os

def create_app():
    app = Flask(__name__, static_folder="static", template_folder="templates")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///library.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from soa_lib.controllers.auth import auth_bp
    from soa_lib.controllers.admin import admin_bp
    from soa_lib.controllers.api import api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    with app.app_context():
        from soa_lib import models  
        db.create_all()
        seed_admin()

    return app

def seed_admin(): 
    from soa_lib.models import User 
    if not User.query.filter_by(username="admin").first():
        from soa_lib.extensions import db
        admin = User(
            username="admin",
            full_name="Duy Trần",
            password_hash=generate_password_hash("admin123")
        )
        db.session.add(admin)
        db.session.commit()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)