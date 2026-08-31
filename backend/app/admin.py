import logging

from flask import Blueprint, jsonify, request
from sqlalchemy import select

from .auth import require_api_key
from .db import SessionLocal
from .models import Flag, Segment, SegmentRule, TargetingRule

log = logging.getLogger(__name__)

bp = Blueprint("admin", __name__)

FLAG_FIELDS = ("description", "enabled", "default_variant", "rollout_percentage")
SEGMENT_FIELDS = ("name", "description", "rollout_percentage")


def serialize_rule(rule):
    return {
        "id": rule.id,
        "priority": rule.priority,
        "attribute": rule.attribute,
        "operator": rule.operator,
        "values": rule.values,
        "variant": rule.variant,
        "segment_id": rule.segment_id,
    }


def serialize_segment_rule(rule):
    return {
        "id": rule.id,
        "priority": rule.priority,
        "attribute": rule.attribute,
        "operator": rule.operator,
        "values": rule.values,
    }


def serialize_segment(segment):
    return {
        "id": segment.id,
        "key": segment.key,
        "name": segment.name,
        "description": segment.description,
        "rollout_percentage": segment.rollout_percentage,
        "rules": [serialize_segment_rule(r) for r in segment.rules],
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
        rule.segment_id = payload.get("segment_id")

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


@bp.route("/api/v1/segments", methods=["GET"])
@require_api_key
def list_segments():
    session = SessionLocal()
    try:
        segments = (
            session.execute(select(Segment).order_by(Segment.name)).scalars().all()
        )
        return jsonify([serialize_segment(s) for s in segments])
    finally:
        session.close()


@bp.route("/api/v1/segments", methods=["POST"])
@require_api_key
def create_segment():
    payload = request.get_json() or {}
    rules = payload.get("rules") or []

    if len(rules) > 50:
        return jsonify({"error": "a segment can have at most 50 rules"}), 400

    session = SessionLocal()
    try:
        segment = Segment(
            key=payload.get("key", ""),
            name=payload.get("name", ""),
            description=payload.get("description", ""),
            rollout_percentage=payload.get("rollout_percentage", 0),
        )
        session.add(segment)
        session.flush()

        for i, rule in enumerate(rules):
            session.add(
                SegmentRule(
                    segment_id=segment.id,
                    priority=i,
                    attribute=rule.get("attribute", ""),
                    operator=rule.get("operator", "in"),
                    values=rule.get("values", ""),
                )
            )

        session.commit()
        return jsonify(serialize_segment(segment)), 201
    finally:
        session.close()


@bp.route("/api/v1/segments/<int:segmentId>", methods=["PATCH"])
@require_api_key
def update_segment(segmentId):
    payload = request.get_json() or {}

    session = SessionLocal()
    try:
        segment = session.get(Segment, segmentId)
        if segment is None:
            return jsonify({"error": "not found"}), 404

        for field in SEGMENT_FIELDS:
            if field in payload:
                setattr(segment, field, payload[field])

        session.commit()
        return jsonify(serialize_segment(segment))
    finally:
        session.close()


@bp.route("/api/v1/segments/<int:segment_id>", methods=["DELETE"])
@require_api_key
def delete_segment(segment_id):
    session = SessionLocal()
    try:
        segment = session.get(Segment, segment_id)
        if segment is not None:
            session.delete(segment)
            session.commit()
        return jsonify({}), 204
    finally:
        session.close()
