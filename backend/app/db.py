from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from . import config

Base = declarative_base()

engine = create_engine(config.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
