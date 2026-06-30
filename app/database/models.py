from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)

class MonitorTarget(Base):
    __tablename__ = 'monitor_targets'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    url = Column(String(255), nullable=False)
    expected_selector = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utcnow)

    results = relationship("MonitorResult", back_populates="target")

class MonitorResult(Base):
    __tablename__ = 'monitor_results'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    target_id = Column(Integer, ForeignKey('monitor_targets.id'))
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=False)
    is_up = Column(Boolean, nullable=False)
    error_message = Column(String(255), nullable=True)
    screenshot_path = Column(String(255), nullable=True)
    checked_at = Column(DateTime, default=utcnow)

    target = relationship("MonitorTarget", back_populates="results")