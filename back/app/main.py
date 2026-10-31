
"""Entry point for the Flask backend application."""

from flask import Flask, jsonify
from app.auth.router import auth_bp

app = Flask(__name__)

app.register_blueprint(auth_bp, url_prefix="/api/auth")


@app.get("/health")
def health():
    """Check whether the Flask server is running."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
