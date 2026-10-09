"""Small shared response helpers used by every API module.

Keeps JSON shapes consistent: {"success": ..., "message": ..., ...extra}
"""
from flask import jsonify


def api_success(message=None, status=200, **fields):
    """Return a success JSON response, optionally with extra top-level fields."""
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    payload.update(fields)
    return jsonify(payload), status


def api_error(message, status=400, **fields):
    """Return an error JSON response with the correct HTTP status code."""
    payload = {"success": False, "message": message}
    payload.update(fields)
    return jsonify(payload), status


def first_present(mapping, *keys, default=None):
    """Return the first non-empty value among the given keys (alias support)."""
    for key in keys:
        value = mapping.get(key)
        if value is not None and value != "":
            return value
    return default
