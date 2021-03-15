import hashlib
import logging

from sqlalchemy import select

from . import config
from .matchers import RuleMatcher
from .models import TargetingRule

log = logging.getLogger(__name__)


def _bucket(flag_key, user_id, salt=None):
    salt = salt or config.DEFAULT_ROLLOUT_SALT
    raw = "{}:{}:{}".format(salt, flag_key, user_id).encode("utf-8")
    return int(hashlib.md5(raw).hexdigest()[:8], 16) % 100


def _bucket_v1(flag_key, user_id):
    # flags created before the salt change stay here so their buckets don't move
    raw = "{}{}".format(flag_key, user_id).encode("utf-8")
    return sum(raw) % 100


class FlagEvaluator:
    def __init__(self, session):
        self.session = session
        self.matcher = RuleMatcher()

    def evaluate(self, flag, context):
        if not flag.enabled:
            return flag.default_variant

        rules = (
            self.session.execute(
                select(TargetingRule)
                .where(TargetingRule.flag_id == flag.id)
                .order_by(TargetingRule.priority)
            )
            .scalars()
            .all()
        )

        for rule in rules:
            if self.matcher.matches(rule, context):
                return rule.variant

        return self._rollout_variant(flag, context)

    def _rollout_variant(self, flag, context):
        user_id = context.get("user_id")
        if user_id is None:
            return flag.default_variant

        if flag.bucketing_version == 1:
            bucket = _bucket_v1(flag.key, user_id)
        else:
            bucket = _bucket(flag.key, user_id)

        if bucket < flag.rollout_percentage:
            return "on"
        return flag.default_variant


class FlagEvaluatorLegacy:
    """The original evaluator. Still behind /api/flags/check."""

    def __init__(self, session):
        self.session = session

    def isEnabledForUser(self, flag, userId):
        if not flag.enabled:
            return False
        return self.getUserBucket(flag, userId) < flag.rollout_percentage

    def getUserBucket(self, flag, userId):
        return _bucket_v1(flag.key, userId)

    def matchesRule(self, rule, userContext):
        actualValue = userContext.get(rule.attribute)
        if actualValue is None:
            return False
        return str(actualValue) in rule.value_list()
