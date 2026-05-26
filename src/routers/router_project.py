from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import Place, Project
from src.schemas import ProjectCreate, ProjectOut, ProjectSummary, ProjectUpdate
from src.services.art_chicago_api import validate_and_fetch

router = APIRouter(prefix="/projects", tags=["Projects"])

MAX_PLACES = 10

def get_project_or_404(project_id: int, db: Session) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    places_data = payload.places or []

    if len(places_data) > MAX_PLACES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"A project cannot have more than {MAX_PLACES} places",
        )

    external_ids = [p.external_id for p in places_data]
    if len(external_ids) != len(set(external_ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Duplicate external_id values in places list",
        )

    validated_artworks = []
    for place_import in places_data:
        try:
            artwork = await validate_and_fetch(place_import.external_id)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
        validated_artworks.append((place_import, artwork))

    project = Project(
        name=payload.name,
        description=payload.description,
        start_date=payload.start_date,
    )
    db.add(project)
    db.flush()

    for place_import, artwork in validated_artworks:
        place = Place(
            project_id=project.id,
            external_id=artwork["id"],
            title=artwork["title"],
            notes=place_import.notes,
        )
        db.add(place)

    db.commit()
    db.refresh(project)
    return project


@router.get("/", response_model=list[ProjectSummary])
def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    return get_project_or_404(project_id, db)


@router.patch("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = get_project_or_404(project_id, db)

    if any(p.visited for p in project.places):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete a project that has visited places",
        )

    db.delete(project)
    db.commit()