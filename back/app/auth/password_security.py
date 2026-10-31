import hashlib


def get_hash_parts(password):
    hashed = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()

    return prefix, suffix