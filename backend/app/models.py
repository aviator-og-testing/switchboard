import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .db import Base


class Flag(Base):
    __tablename__ = "flags"

    id = Column(Integer, primary_key=True)
    key = Column(String(128), unique=True, nullable=False)
    description = Column(Text, default="")
    enabled = Column(Boolean, default=False, nullable=False)
    default_variant = Column(String(64), default="off", nullable=False)
    rollout_percentage = Column(Integer, default=0, nullable=False)

    # flags created before the hash change stay on 1 so their buckets don't move
    bucketing_version = Column(Integer, default=2, nullable=False)

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

    rules = relationship("TargetingRule", back_populates="flag")


class TargetingRule(Base):
    __tablename__ = "targeting_rules"

    id = Column(Integer, primary_key=True)
    flag_id = Column(Integer, ForeignKey("flags.id"), nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    attribute = Column(String(64), nullable=False)
    operator = Column(String(32), nullable=False)
    values = Column(Text, nullable=False)
    variant = Column(String(64), nullable=False)

    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=True)

    flag = relationship("Flag", back_populates="rules")

    def value_list(self):
        return [v for v in self.values.split(",") if v]


class Segment(Base):
    __tablename__ = "segments"

    id = Column(Integer, primary_key=True)
    key = Column(String(128), unique=True, nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, default="")
    rollout_percentage = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    rules = relationship("SegmentRule", back_populates="segment")


class SegmentRule(Base):
    __tablename__ = "segment_rules"

    id = Column(Integer, primary_key=True)
    segment_id = Column(Integer, ForeignKey("segments.id"), nullable=False)
    priority = Column(Integer, default=0, nullable=False)
    attribute = Column(String(64), nullable=False)
    operator = Column(String(32), nullable=False)
    values = Column(Text, nullable=False)

    segment = relationship("Segment", back_populates="rules")

    def value_list(self):
        return [v for v in self.values.split(",") if v]
