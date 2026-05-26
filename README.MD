# Travel Planner API

REST API for managing travel projects and places built with FastAPI + SQLite.

## Setup

Required: Python, tested on Python3.12

```bash
git clone https://github.com/ORENYT/travelproject.git
cd travel-planner

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

## Running

```bash
uvicorn main:app --reload
```

API docs available at `http://localhost:8000/docs`

## Testing

```bash
pytest src/tests/ -v
```

## Example Requests

**Create a project with places:**
```json
POST /projects/
{
    "name": "Art Tour Chicago",
    "start_date": "2026-06-01",
    "places": [
        { "external_id": 27992, "notes": "Must see" }
    ]
}
```

**Mark a place as visited:**
```json
PATCH /projects/1/places/1
{
    "visited": true
}
```
