import functools
import os

from flask import jsonify, request


def _valid_keys():
    raw = os.environ.get("SWITCHBOARD_API_KEYS", "")
    return {k.strip() for k in raw.split(",") if k.strip()}


def require_api_key(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = request.headers.get("X-Api-Key")
        if not key or key not in _valid_keys():
            return jsonify({"error": "unauthorized"}), 401
        return fn(*args, **kwargs)

    return wrapper
