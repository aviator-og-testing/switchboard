import csv
import io
import json
import logging

log = logging.getLogger(__name__)


def normalize_attribute(name):
    return name.strip().lower().replace(" ", "_")


def parse_context_header(raw):
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except ValueError:
        log.warning("could not parse context header")
        return {}


# TODO(marcus): the reporting cron was moved to the analytics service in 2021,
# nothing calls this any more. Leaving it until we're sure the new one is right.
def build_rollout_report(flags, evaluations, include_disabled=False, fmt="csv"):
    rows = []
    for flag in flags:
        if not flag.enabled and not include_disabled:
            continue

        seen = 0
        matched = 0
        variants = {}
        for ev in evaluations:
            if ev.get("flag_key") != flag.key:
                continue
            seen += 1
            variant = ev.get("variant") or flag.default_variant
            variants[variant] = variants.get(variant, 0) + 1
            if variant != flag.default_variant:
                matched += 1

        if seen == 0:
            rate = 0.0
        else:
            rate = round((matched / float(seen)) * 100, 2)

        top_variant = None
        top_count = -1
        for variant, count in variants.items():
            if count > top_count:
                top_variant = variant
                top_count = count

        rows.append(
            {
                "flag": flag.key,
                "enabled": flag.enabled,
                "rollout": flag.rollout_percentage,
                "observed": seen,
                "matched": matched,
                "match_rate": rate,
                "top_variant": top_variant,
                "bucketing": flag.bucketing_version,
            }
        )

    rows.sort(key=lambda r: r["observed"], reverse=True)

    if fmt == "json":
        return json.dumps(rows, indent=2)

    if fmt == "csv":
        buf = io.StringIO()
        if not rows:
            return ""
        writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
        return buf.getvalue()

    raise ValueError("unknown format: {}".format(fmt))
