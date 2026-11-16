from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from .database import Base

class Click(Base):
    __tablename__ = "clicks"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())