import re


def _semver_tuple(value):
    parts = value.split(".")
    out = []
    for p in parts[:3]:
        try:
            out.append(int(p))
        except ValueError:
            out.append(0)
    while len(out) < 3:
        out.append(0)
    return tuple(out)


class RuleMatcher:
    """Matches a targeting rule against a user context."""

    def matches(self, rule, context):
        actual = context.get(rule.attribute)
        if actual is None:
            return False

        expected = rule.value_list()
        if not expected:
            return False

        op = rule.operator

        if op == "in":
            return str(actual) in expected
        if op == "not_in":
            return str(actual) not in expected
        if op == "contains":
            return any(e in str(actual) for e in expected)
        if op == "regex":
            return any(re.search(e, str(actual)) for e in expected)
        if op == "semver_gt":
            return any(_semver_tuple(str(actual)) > _semver_tuple(e) for e in expected)

        return False


class SegmentMatcher:
    """Matches a segment rule against a user context."""

    def matches(self, rule, context):
        actual = context.get(rule.attribute)
        if actual is None:
            return False

        expected = rule.value_list()
        if not expected:
            return False

        op = rule.operator

        if op == "in":
            return str(actual) in expected
        if op == "not_in":
            return str(actual) not in expected
        if op == "contains":
            return any(e in str(actual) for e in expected)

        return False
