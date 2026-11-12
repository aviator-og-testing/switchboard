"""Create the tables and put a few flags in them, for local poking."""

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Flag, Segment, SegmentRule, TargetingRule


def main():
    Base.metadata.create_all(engine)

    session = SessionLocal()
    try:
        if session.execute(select(Flag)).scalars().first():
            print("already seeded")
            return

        checkout = Flag(
            key="checkout.new",
            description="Rewritten checkout flow",
            enabled=True,
            default_variant="off",
            rollout_percentage=25,
        )
        nav = Flag(
            key="mobile.newnav",
            description="Bottom nav on mobile web",
            enabled=True,
            default_variant="off",
            rollout_percentage=0,
        )
        billing = Flag(
            key="billing.usage_based",
            description="Usage based billing, enterprise only",
            enabled=False,
            default_variant="off",
            rollout_percentage=0,
        )
        reports = Flag(
            key="reports.export",
            description="CSV export, gated on the beta segment",
            enabled=True,
            default_variant="off",
            rollout_percentage=0,
        )
        session.add_all([checkout, nav, billing, reports])
        session.flush()

        beta = Segment(
            key="beta-users",
            name="Beta users",
            description="Enterprise accounts who opted into the beta",
            rollout_percentage=0,
        )
        eu = Segment(
            key="eu-accounts",
            name="EU accounts",
            description="Anything hosted in an EU region",
            rollout_percentage=0,
        )
        session.add_all([beta, eu])
        session.flush()

        session.add_all(
            [
                SegmentRule(
                    segment_id=beta.id,
                    priority=0,
                    attribute="beta_optin",
                    operator="in",
                    values="true",
                ),
                SegmentRule(
                    segment_id=beta.id,
                    priority=1,
                    attribute="plan",
                    operator="in",
                    values="enterprise",
                ),
                SegmentRule(
                    segment_id=eu.id,
                    priority=0,
                    attribute="region",
                    operator="in",
                    values="eu-west,eu-central",
                ),
            ]
        )

        session.add_all(
            [
                TargetingRule(
                    flag_id=checkout.id,
                    priority=0,
                    attribute="plan",
                    operator="in",
                    values="enterprise",
                    variant="on",
                ),
                TargetingRule(
                    flag_id=checkout.id,
                    priority=1,
                    attribute="email",
                    operator="regex",
                    values=r".*@switchboard\.internal$",
                    variant="on",
                ),
                TargetingRule(
                    flag_id=nav.id,
                    priority=0,
                    attribute="app_version",
                    operator="semver_gt",
                    values="4.2.0",
                    variant="on",
                ),
                TargetingRule(
                    flag_id=billing.id,
                    priority=0,
                    attribute="account_id",
                    operator="in",
                    values="acct_1041,acct_2277",
                    variant="on",
                ),
                TargetingRule(
                    flag_id=reports.id,
                    priority=0,
                    attribute="",
                    operator="in",
                    values="",
                    variant="on",
                    segment_id=beta.id,
                ),
            ]
        )

        session.commit()
        print("seeded 4 flags and 2 segments")
    finally:
        session.close()


if __name__ == "__main__":
    main()
