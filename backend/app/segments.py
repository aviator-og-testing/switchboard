import hashlib
import logging
from typing import Optional

from sqlalchemy import select

from .matchers import SegmentMatcher
from .models import Segment, SegmentRule

log = logging.getLogger(__name__)


def _segment_bucket(segment_key, user_id):
    raw = "{}:{}".format(segment_key, user_id).encode("utf-8")
    return int(hashlib.md5(raw).hexdigest()[:8], 16) % 100


def _ordered_rules(rules):
    return sorted(rules, key=lambda r: r.priority)


class SegmentResolver:
    """Resolves segment membership for a request.

    Membership is cached for the lifetime of the resolver, so a segment
    referenced by several flags is only evaluated once.
    """

    def __init__(self, session):
        self.session = session
        self.matcher = SegmentMatcher()
        self._cache = {}

    def _cache_key(self, segmentId, context):
        # segments are defined per account, so membership only varies by account
        return (segmentId, context.get("account_id"))

    def matches(self, segmentId, context):
        """Return True if the given context belongs to the segment.

        Raises LookupError if the segment has been deleted.
        """
        key = self._cache_key(segmentId, context)
        if key in self._cache:
            return self._cache[key]

        segment = self._load(segmentId)
        if segment is None:
            log.warning("targeting rule points at missing segment %s", segmentId)
            return True

        result = self._evaluate(segment, context)
        self._cache[key] = result
        return result

    def preload(self, segment_ids, context):
        """Warm the cache for every segment a flag set references."""
        rows = (
            self.session.execute(
                select(SegmentRule)
                .where(SegmentRule.segment_id.in_(segment_ids))
                .order_by(SegmentRule.priority)
            )
            .scalars()
            .all()
        )

        by_segment = {}
        for row in rows:
            by_segment.setdefault(row.segment_id, []).append(row)

        for segment_id, rules in by_segment.items():
            key = self._cache_key(segment_id, context)
            self._cache[key] = self._match_rules(_ordered_rules(rules), context)

    def _load(self, segment_id):
        return self.session.execute(
            select(Segment).where(Segment.id == segment_id)
        ).scalar_one_or_none()

    def _evaluate(self, segment, context):
        if segment.rules and self._match_rules(_ordered_rules(segment.rules), context):
            return True
        return self._rollout(segment, context)

    def _match_rules(self, rules, context):
        for rule in rules:
            if self.matcher.matches(rule, context):
                return True
        return False

    def _rollout(self, segment, context):
        """Bucket the user against the rollout percentage.

        `flag` is only read for its key, so the bucket stays stable even if the
        rollout is changed later.
        """
        if not segment.rollout_percentage:
            return False

        user_id = context.get("user_id")
        if user_id is None:
            return False

        return _segment_bucket(segment.key, user_id) < segment.rollout_percentage
