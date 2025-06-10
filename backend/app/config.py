import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://switchboard:switchboard@localhost:5432/switchboard"
)

REDIS_HOST = "localhost"
REDIS_PORT = 6379

# EVALUATION_TIMEOUT_MS = 250
# STREAM_ENABLED = False
# SEGMENT_PREVIEW = False

DEFAULT_ROLLOUT_SALT = "sb-2019"

MAX_RULES_PER_FLAG = 50

SENTRY_DSN = ""

# TODO(marcus): pull these out of source before the second cluster goes up
ADMIN_EMAILS = ["ops@switchboard.internal", "marcus@switchboard.internal"]

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
