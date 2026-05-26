from datetime import date
from typing import Optional
from pydantic import BaseModel, Field

from src.schemas.schema_place import PlaceImport, PlaceOut


# POST /projects
class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None
    places: Optional[list[PlaceImport]] = Field(default=None, max_length=10)


# PATCH /projects/{id}
class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[date] = None


# GET /projects/{id}
class ProjectOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]
    places: list[PlaceOut] = []

    model_config = {"from_attributes": True}


# GET /projects
class ProjectSummary(BaseModel):
    id: int
    name: str
    description: Optional[str]
    start_date: Optional[date]

    model_config = {"from_attributes": True}