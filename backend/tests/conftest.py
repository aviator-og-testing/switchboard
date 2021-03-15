import pytest


class FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def scalars(self):
        return self

    def all(self):
        return self._rows

    def scalar_one_or_none(self):
        return self._rows[0] if self._rows else None


class FakeSession:
    """Stands in for a SQLAlchemy session. Returns whatever it was primed with."""

    def __init__(self, rows=None):
        self.rows = rows or []
        self.executed = []

    def execute(self, stmt):
        self.executed.append(stmt)
        return FakeResult(self.rows)

    def close(self):
        pass


class StubRule:
    def __init__(self, attribute, operator, values, variant, priority=0):
        self.attribute = attribute
        self.operator = operator
        self.values = values
        self.variant = variant
        self.priority = priority

    def value_list(self):
        return [v for v in self.values.split(",") if v]


class StubFlag:
    def __init__(self, key, enabled=True, rollout=0, default="off", version=2):
        self.id = 1
        self.key = key
        self.enabled = enabled
        self.rollout_percentage = rollout
        self.default_variant = default
        self.bucketing_version = version
        self.rules = []


@pytest.fixture
def session():
    return FakeSession()
