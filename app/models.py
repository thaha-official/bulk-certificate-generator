from sqlalchemy import Column, Integer, String, Text
from .database import Base


class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="PENDING")
    total = Column(Integer, default=0)
    completed = Column(Integer, default=0)
    failed = Column(Integer, default=0)


class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, index=True)
    recipient_name = Column(String)
    status = Column(String)
    file_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)