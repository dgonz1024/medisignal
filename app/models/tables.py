from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, Date, DateTime, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class StudyRecord(Base):
    __tablename__ = "study_records"
    __table_args__ = (
        UniqueConstraint("nct_id", "source_hash", name="uq_raw_study_records_nct_id_source_hash"),
        {"schema": "raw"},
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    nct_id = Column(String(32), index=True, nullable=False)
    fetched_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    source_hash = Column(String(64), nullable=False)
    payload_jsonb = Column(JSON, nullable=False)


class StagingStudy(Base):
    __tablename__ = "studies"
    __table_args__ = {"schema": "staging"}

    nct_id = Column(String(32), primary_key=True)
    brief_title = Column(Text)
    official_title = Column(Text)
    study_type = Column(String(100))
    phase = Column(String(50))
    overall_status = Column(String(100))
    start_date = Column(Date)
    completion_date = Column(Date)
    enrollment_count = Column(Integer)
    healthy_volunteers = Column(Boolean)
    sex = Column(String(50))
    minimum_age = Column(String(50))
    maximum_age = Column(String(50))
    sponsor_name = Column(String(255))
    last_update_posted = Column(Date)


class StagingCondition(Base):
    __tablename__ = "conditions"
    __table_args__ = {"schema": "staging"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nct_id = Column(String(32), index=True, nullable=False)
    condition_name = Column(String(255), nullable=False)


class StagingIntervention(Base):
    __tablename__ = "interventions"
    __table_args__ = {"schema": "staging"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nct_id = Column(String(32), index=True, nullable=False)
    intervention_type = Column(String(100))
    intervention_name = Column(String(255), nullable=False)


class StagingLocation(Base):
    __tablename__ = "locations"
    __table_args__ = {"schema": "staging"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nct_id = Column(String(32), index=True, nullable=False)
    facility = Column(String(255))
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100))


class TrialSummary(Base):
    __tablename__ = "trial_summary"
    __table_args__ = {"schema": "analytics"}

    nct_id = Column(String(32), primary_key=True)
    phase = Column(String(50))
    status = Column(String(100))
    enrollment_count = Column(Integer)
    location_count = Column(Integer)
    condition_count = Column(Integer)
    sponsor_type = Column(String(100))


class ConditionStats(Base):
    __tablename__ = "condition_stats"
    __table_args__ = {"schema": "analytics"}

    condition_name = Column(String(255), primary_key=True)
    trial_count = Column(Integer, nullable=False)
    avg_enrollment = Column(Numeric(10, 2))


class SponsorStats(Base):
    __tablename__ = "sponsor_stats"
    __table_args__ = {"schema": "analytics"}

    sponsor_name = Column(String(255), primary_key=True)
    trial_count = Column(Integer, nullable=False)
    completion_rate = Column(Numeric(5, 2))


class QualityIssue(Base):
    __tablename__ = "quality_issues"
    __table_args__ = {"schema": "analytics"}

    id = Column(Integer, primary_key=True, autoincrement=True)
    nct_id = Column(String(32), index=True, nullable=False)
    issue_type = Column(String(100), nullable=False)
    issue_description = Column(Text, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
