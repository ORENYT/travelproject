from typing import Optional
from pydantic import BaseModel

# POST /projects/{id}/places
class PlaceImport(BaseModel):
    external_id: int
    notes: Optional[str] = None

#
class PlaceCreate(BaseModel):
    external_id: int
    notes: Optional[str] = None

# PATCH /projects/{id}/places/{place_id}
class PlaceUpdate(BaseModel):
    notes: Optional[str] = None
    visited: Optional[bool] = None

# GET /projects/{id}/places
# GET /projects/{id}/places/{place_id}
class PlaceOut(BaseModel):
    id: int
    project_id: int
    external_id: int
    title: str
    notes: Optional[str]
    visited: bool

    model_config = {"from_attributes": True}