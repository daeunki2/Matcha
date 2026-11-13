"""Entry point for the Flask backend application."""

from flask import Flask, jsonify
from flasgger import Swagger
from pathlib import Path
from flask import send_from_directory, render_template_string
from app.auth.router import auth_bp

app = Flask(__name__)
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

app.register_blueprint(auth_bp, url_prefix="/api/auth")


@app.get("/health")
def health():
    """Check whether the Flask server is running."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)