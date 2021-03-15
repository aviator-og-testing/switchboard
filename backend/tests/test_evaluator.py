from app.evaluator import FlagEvaluator, _bucket, _bucket_v1

from .conftest import FakeSession, StubFlag, StubRule


def test_disabled_flag_returns_default():
    flag = StubFlag("checkout.new", enabled=False, default="off")
    result = FlagEvaluator(FakeSession()).evaluate(flag, {"user_id": "u1"})
    assert result == "off"


def test_first_matching_rule_wins():
    flag = StubFlag("checkout.new")
    rules = [
        StubRule("plan", "in", "enterprise", "on", priority=0),
        StubRule("plan", "in", "enterprise", "beta", priority=1),
    ]
    result = FlagEvaluator(FakeSession(rules)).evaluate(flag, {"plan": "enterprise"})
    assert result == "on"


def test_falls_through_to_rollout():
    flag = StubFlag("checkout.new", rollout=100)
    result = FlagEvaluator(FakeSession()).evaluate(flag, {"user_id": "u1"})
    assert result == "on"


def test_rollout_needs_a_user_id():
    flag = StubFlag("checkout.new", rollout=100, default="off")
    result = FlagEvaluator(FakeSession()).evaluate(flag, {"plan": "free"})
    assert result == "off"


def test_bucket_is_stable_for_the_same_user():
    assert _bucket("checkout.new", "u1") == _bucket("checkout.new", "u1")


def test_v1_bucketing_is_preserved():
    flag = StubFlag("legacy.flag", rollout=100, version=1)
    evaluator = FlagEvaluator(FakeSession())
    assert evaluator._rollout_variant(flag, {"user_id": "u1"}) == "on"
    assert _bucket_v1("legacy.flag", "u1") < 100


def test_semver_operator():
    flag = StubFlag("mobile.newnav")
    rules = [StubRule("app_version", "semver_gt", "4.2.0", "on")]
    result = FlagEvaluator(FakeSession(rules)).evaluate(flag, {"app_version": "4.3.1"})
    assert result == "on"


def test_regex_operator():
    flag = StubFlag("internal.tools")
    rules = [StubRule("email", "regex", r".*@switchboard\.internal$", "on")]
    result = FlagEvaluator(FakeSession(rules)).evaluate(
        flag, {"email": "ops@switchboard.internal"}
    )
    assert result == "on"
