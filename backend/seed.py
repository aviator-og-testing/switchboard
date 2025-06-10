"""Create the tables and put a few flags in them, for local poking."""

from sqlalchemy import select

from app.db import Base, SessionLocal, engine
from app.models import Flag, TargetingRule


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
        session.add_all([checkout, nav, billing])
        session.flush()

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
            ]
        )

        session.commit()
        print("seeded 3 flags")
    finally:
        session.close()


if __name__ == "__main__":
    main()
