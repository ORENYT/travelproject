from sqlalchemy import Column, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database import Base

class Place(Base):
    __tablename__ = "places"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    external_id = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    notes = Column(Text, nullable=True)
    visited = Column(Boolean, default=False, nullable=False)

    project = relationship("Project", back_populates="places")

    __table_args__ = (
        UniqueConstraint("project_id", "external_id", name="repeating_place_constraint"),
    )