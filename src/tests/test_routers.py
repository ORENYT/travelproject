import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from src.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def mock_artwork():
    with patch("src.services.art_chicago_api.fetch_artwork") as mock:
        mock.return_value = {"id": 27992, "title": "A Sunday on La Grande Jatte"}
        yield mock


def test_create_project(client):
    response = client.post("/projects/", json={"name": "My Trip"})
    assert response.status_code == 201
    assert response.json()["name"] == "My Trip"


def test_create_project_with_places(client, mock_artwork):
    response = client.post("/projects/", json={
        "name": "Art Trip",
        "places": [{"external_id": 27992}]
    })
    assert response.status_code == 201
    assert len(response.json()["places"]) == 1
    assert response.json()["places"][0]["title"] == "A Sunday on La Grande Jatte"


def test_get_project(client):
    created = client.post("/projects/", json={"name": "My Trip"})
    project_id = created.json()["id"]

    response = client.get(f"/projects/{project_id}")
    assert response.status_code == 200
    assert response.json()["id"] == project_id


def test_delete_project(client):
    created = client.post("/projects/", json={"name": "My Trip"})
    project_id = created.json()["id"]

    response = client.delete(f"/projects/{project_id}")
    assert response.status_code == 204