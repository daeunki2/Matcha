from flask import Flask
from app.auth.router import auth_bp


def create_app():
    app = Flask(__name__)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    return app