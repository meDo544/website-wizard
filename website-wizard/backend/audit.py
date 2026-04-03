from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from backend.database import Base

class Audit(Base):
    __tablename__ = "audits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    url = Column(String)
    result = Column(Text)
    status = Column(String, default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
