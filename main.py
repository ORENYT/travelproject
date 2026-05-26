from fastapi import FastAPI
from src.database import Base, engine
from src.routers import projects_router, places_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Travel Projects API", version="1.0.0")

app.include_router(projects_router)
app.include_router(places_router)