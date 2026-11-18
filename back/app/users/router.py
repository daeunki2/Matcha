from flask import Blueprint

users_bp = Blueprint("users", __name__)


@users_bp.route("/users/me/profile", methods=["GET"])
def get_my_profile():
    return {"message": "Profile endpoint reached."}, 200


@users_bp.route("/users/me/profile", methods=["GET"])
@users_bp.route("/users/me/profile", methods=["PATCH"])
@users_bp.route("/interests", methods=["GET"])
@users_bp.route("/interests", methods=["POST"])
@users_bp.route("/users/me/interests", methods=["PUT"])