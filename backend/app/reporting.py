import logging

from sqlalchemy import select

from .db import SessionLocal
from .models import Flag
from .utils.helpers import build_rollout_report

log = logging.getLogger(__name__)


def nightly_rollout_report(evaluations):
    session = SessionLocal()
    try:
        flags = session.execute(select(Flag)).scalars().all()
        return build_rollout_report(flags, evaluations, fmt="csv")
    finally:
        session.close()
