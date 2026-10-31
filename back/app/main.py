"""Entry point for the Flask backend application.

Responsibilities:
    - Initialize the Flask application.
    - Register API routes using Blueprints.
    - Configure and start the development server.
"""

from flask import Flask, jsonify

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(debug=True)