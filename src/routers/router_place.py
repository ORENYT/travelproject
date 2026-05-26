from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Place, Project
from src.schemas import PlaceCreate, PlaceOut, PlaceUpdate
from src.services.art_chicago_api import validate_and_fetch

router = APIRouter(prefix="/projects/{project_id}/places", tags=["Places"])

MAX_PLACES = 10


def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


def get_place_or_404(place_id: int, project_id: int, db: Session) -> Place:
    place = db.query(Place).filter(Place.id == place_id, Place.project_id == project_id).first()
    if not place:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Place not found")
    return place


@router.post("/", response_model=PlaceOut, status_code=status.HTTP_201_CREATED)
async def add_place(project_id: int, payload: PlaceCreate, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)

    if len(project.places) >= MAX_PLACES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Project already has the maximum of {MAX_PLACES} places",
        )

    existing = db.query(Place).filter(
        Place.project_id == project_id,
        Place.external_id == payload.external_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This place is already in the project",
        )

    try:
        artwork = await validate_and_fetch(payload.external_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))

    place = Place(
        project_id=project_id,
        external_id=artwork["id"],
        title=artwork["title"],
        notes=payload.notes,
    )
    db.add(place)
    db.commit()
    db.refresh(place)
    return place


@router.get("/", response_model=list[PlaceOut])
def list_places(project_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return db.query(Place).filter(Place.project_id == project_id).all()


@router.get("/{place_id}", response_model=PlaceOut)
def get_place(project_id: int, place_id: int, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    return get_place_or_404(place_id, project_id, db)


@router.patch("/{place_id}", response_model=PlaceOut)
def update_place(project_id: int, place_id: int, payload: PlaceUpdate, db: Session = Depends(get_db)):
    get_project_or_404(project_id, db)
    place = get_place_or_404(place_id, project_id, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(place, field, value)

    db.commit()
    db.refresh(place)
    return place