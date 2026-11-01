from zxcvbn import zxcvbn


def is_password_acceptable(password):
    if zxcvbn(password)["score"] < 2:
        return False
    return True