import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from .auth import require_api_key
from .db import SessionLocal
from .evaluator import FlagEvaluator, FlagEvaluatorLegacy
from .models import Flag

log = logging.getLogger(__name__)

bp = Blueprint("api", __name__)


@bp.route("/api/v1/evaluate", methods=["POST"])
@require_api_key
def evaluate():
    payload = request.get_json() or {}
    context = payload.get("context") or {}

    session = SessionLocal()
    try:
        flags = session.execute(select(Flag)).scalars().all()
        evaluator = FlagEvaluator(session)
        result = {f.key: evaluator.evaluate(f, context) for f in flags}
    finally:
        session.close()

    return jsonify({"flags": result})


@bp.route("/api/v1/evaluate/batch", methods=["POST"])
@require_api_key
def evaluate_batch():
    """Evaluate every flag for a list of user contexts in one round trip.

    The SDK calls this on startup to warm its local cache for a whole tenant,
    so a single request routinely carries a few thousand users.
    """
    payload = request.get_json() or {}
    contexts = payload.get("contexts") or []

    session = SessionLocal()
    try:
        flags = session.execute(select(Flag)).scalars().all()
        evaluator = FlagEvaluator(session)
        results = []
        for context in contexts:
            results.append(
                {
                    "user_id": context.get("user_id"),
                    "flags": {f.key: evaluator.evaluate(f, context) for f in flags},
                }
            )
    finally:
        session.close()

    return jsonify({"results": results})


@bp.route("/api/flags/check", methods=["GET"])
def legacy_check():
    # superseded by /api/v1/evaluate, still here for the 3.x mobile clients
    flag_key = request.args.get("flag")
    user_id = request.args.get("user")

    session = SessionLocal()
    try:
        flag = session.execute(
            select(Flag).where(Flag.key == flag_key)
        ).scalar_one_or_none()
        if flag is None:
            return jsonify({"enabled": False})
        enabled = FlagEvaluatorLegacy(session).isEnabledForUser(flag, user_id)
    finally:
        session.close()

    return jsonify({"enabled": enabled})
