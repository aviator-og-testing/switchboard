import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from .auth import require_api_key
from .db import SessionLocal
from .models import Flag, TargetingRule

log = logging.getLogger(__name__)

bp = Blueprint("admin", __name__)

FLAG_FIELDS = ("description", "enabled", "default_variant", "rollout_percentage")


def serialize_rule(rule):
    return {
        "id": rule.id,
        "priority": rule.priority,
        "attribute": rule.attribute,
        "operator": rule.operator,
        "values": rule.values,
        "variant": rule.variant,
    }


def serialize_flag(flag):
    return {
        "id": flag.id,
        "key": flag.key,
        "description": flag.description,
        "enabled": flag.enabled,
        "default_variant": flag.default_variant,
        "rollout_percentage": flag.rollout_percentage,
        "rules": [serialize_rule(r) for r in flag.rules],
    }


@bp.route("/api/v1/flags", methods=["GET"])
@require_api_key
def list_flags():
    session = SessionLocal()
    try:
        flags = session.execute(select(Flag).order_by(Flag.key)).scalars().all()
        return jsonify([serialize_flag(f) for f in flags])
    finally:
        session.close()


@bp.route("/api/v1/flags/<int:flag_id>", methods=["GET"])
@require_api_key
def get_flag(flag_id):
    session = SessionLocal()
    try:
        flag = session.get(Flag, flag_id)
        if flag is None:
            return jsonify({"error": "not found"}), 404
        return jsonify(serialize_flag(flag))
    finally:
        session.close()


@bp.route("/api/v1/flags/<int:flag_id>", methods=["PATCH"])
@require_api_key
def update_flag(flag_id):
    payload = request.get_json() or {}

    session = SessionLocal()
    try:
        flag = session.get(Flag, flag_id)
        if flag is None:
            return jsonify({"error": "not found"}), 404

        for field in FLAG_FIELDS:
            if field in payload:
                setattr(flag, field, payload[field])

        session.commit()
        return jsonify(serialize_flag(flag))
    finally:
        session.close()


@bp.route("/api/v1/flags/<int:flag_id>/rules", methods=["POST"])
@require_api_key
def upsert_rule(flag_id):
    payload = request.get_json() or {}

    session = SessionLocal()
    try:
        flag = session.get(Flag, flag_id)
        if flag is None:
            return jsonify({"error": "not found"}), 404

        rule_id = payload.get("id")
        if rule_id:
            rule = session.get(TargetingRule, rule_id)
        else:
            rule = TargetingRule(flag_id=flag.id, priority=len(flag.rules))
            session.add(rule)

        rule.attribute = payload.get("attribute", "")
        rule.operator = payload.get("operator", "in")
        rule.values = payload.get("values", "")
        rule.variant = payload.get("variant", "on")

        session.commit()
        return jsonify(serialize_rule(rule))
    finally:
        session.close()


@bp.route("/api/v1/flags/<int:flag_id>/rules/<int:rule_id>", methods=["DELETE"])
@require_api_key
def remove_rule(flag_id, rule_id):
    session = SessionLocal()
    try:
        rule = session.get(TargetingRule, rule_id)
        if rule is not None:
            session.delete(rule)
            session.commit()
        return jsonify({}), 204
    finally:
        session.close()
