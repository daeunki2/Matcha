"""Entry point for the Flask backend application."""

from flask import Flask, jsonify, request
from flasgger import Swagger
from pathlib import Path
from flask import send_from_directory, render_template_string
from app.auth.router import auth_bp
import os
from app.auth.google_oauth import oauth
from app.auth.google_router import google_bp
from app.auth.oauth_router import oauth_bp
from app.auth.ft_router import ft_bp
from app.users.router import users_bp


app = Flask(__name__)

ALLOWED_ORIGINS = {
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
}
if os.environ.get("APP_ENV", "production") == "development":
    ALLOWED_ORIGINS.update({
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5001",
        "http://127.0.0.1:5001",
    })

@app.before_request
def validate_origin():
    if request.method not in {"POST", "PUT", "PATCH", "DELETE"}:
        return None

    origin = request.headers.get("Origin")

    if origin not in ALLOWED_ORIGINS:
        return jsonify({"message": "Forbidden origin."}), 403

    return None


app.secret_key = os.environ["SECRET_KEY"]
oauth.init_app(app)

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"
@app.get("/docs/spec/<path:filename>")
def openapi_spec(filename):
    return send_from_directory(DOCS_DIR, filename)
@app.get("/docs")
def swagger_ui():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Matcha API</title>
      <link rel="stylesheet"
        href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css">
    </head>
    <body>
      <div id="swagger-ui"></div>
      <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
      <script>
        SwaggerUIBundle({
          url: "/docs/spec/openapi.yaml",
          dom_id: "#swagger-ui"
        });
      </script>
    </body>
    </html>
    """)
Swagger(app)

#Blue Print
app.register_blueprint(auth_bp, url_prefix="/api/auth")
app.register_blueprint(google_bp, url_prefix="/api/auth")
app.register_blueprint(oauth_bp, url_prefix="/api/auth")
app.register_blueprint(ft_bp, url_prefix="/api/auth")
app.register_blueprint(users_bp, url_prefix="/api")

@app.get("/health")
def health():
    """Check whether the Flask server is running."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)
