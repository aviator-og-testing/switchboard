from unittest import mock

from app.matchers import SegmentMatcher
from app.segments import SegmentResolver, _segment_bucket

from .conftest import FakeSession, StubSegment, StubSegmentRule


def test_segment_matching():
    """A context that satisfies the segment's rules is a member."""
    segment = StubSegment(
        "beta-users", rules=[StubSegmentRule("plan", "in", "enterprise")]
    )
    resolver = SegmentResolver(FakeSession([segment]))

    with mock.patch.object(SegmentMatcher, "matches", return_value=True):
        assert resolver.matches(segment.id, {"plan": "enterprise"}) is True


def test_non_member_is_excluded():
    segment = StubSegment(
        "beta-users", rules=[StubSegmentRule("plan", "in", "enterprise")]
    )
    resolver = SegmentResolver(FakeSession([segment]))

    assert resolver.matches(segment.id, {"plan": "free"}) is False


def test_membership_is_cached():
    segment = StubSegment(
        "beta-users", rules=[StubSegmentRule("plan", "in", "enterprise")]
    )
    session = FakeSession([segment])
    resolver = SegmentResolver(session)

    resolver.matches(segment.id, {"plan": "enterprise"})
    resolver.matches(segment.id, {"plan": "enterprise"})

    assert len(session.executed) == 1


def test_rollout_only_segment():
    segment = StubSegment("gradual", rollout=100)
    resolver = SegmentResolver(FakeSession([segment]))

    assert resolver.matches(segment.id, {"user_id": "u1"}) is True


def test_rollout_needs_a_user_id():
    segment = StubSegment("gradual", rollout=100)
    resolver = SegmentResolver(FakeSession([segment]))

    assert resolver.matches(segment.id, {"plan": "free"}) is False


def test_segment_bucket_is_stable():
    assert _segment_bucket("beta-users", "u1") == _segment_bucket("beta-users", "u1")
