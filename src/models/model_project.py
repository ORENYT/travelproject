from sqlalchemy import Column, Date, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    start_date = Column(Date, nullable=True)
    is_completed = Column(Boolean, default=False, nullable=False)

    places = relationship("Place", back_populates="project", cascade="all, delete-orphan")