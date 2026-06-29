"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from datetime import date
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, validator
import os
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing, creating, updating, and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# In-memory activity database
activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "date": "2026-09-01",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "date": "2026-09-02",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "date": "2026-09-03",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Soccer Team": {
        "description": "Join the school soccer team and compete in matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "date": "2026-09-04",
        "max_participants": 22,
        "participants": ["liam@mergington.edu", "noah@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and play basketball with the school team",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "date": "2026-09-05",
        "max_participants": 15,
        "participants": ["ava@mergington.edu", "mia@mergington.edu"]
    },
    "Art Club": {
        "description": "Explore your creativity through painting and drawing",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "date": "2026-09-06",
        "max_participants": 15,
        "participants": ["amelia@mergington.edu", "harper@mergington.edu"]
    },
    "Drama Club": {
        "description": "Act, direct, and produce plays and performances",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "date": "2026-09-07",
        "max_participants": 20,
        "participants": ["ella@mergington.edu", "scarlett@mergington.edu"]
    },
    "Math Club": {
        "description": "Solve challenging problems and participate in math competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "date": "2026-09-08",
        "max_participants": 10,
        "participants": ["james@mergington.edu", "benjamin@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop public speaking and argumentation skills",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "date": "2026-09-09",
        "max_participants": 12,
        "participants": ["charlotte@mergington.edu", "henry@mergington.edu"]
    }
}


class ActivityBase(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: str = Field(..., min_length=5, max_length=300)
    schedule: str = Field(..., min_length=3, max_length=100)
    date: date
    max_participants: int = Field(..., gt=0)
    participants: List[str] = Field(default_factory=list)

    @validator("name")
    def name_not_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Activity name must not be blank")
        return value

    @validator("description")
    def description_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Description must not be blank")
        return value

    @validator("schedule")
    def schedule_not_blank(cls, value):
        if not value.strip():
            raise ValueError("Schedule must not be blank")
        return value

    @validator("date")
    def date_must_be_future(cls, value):
        if value <= date.today():
            raise ValueError("Event date must be in the future")
        return value


class ActivityCreate(ActivityBase):
    name: str = Field(..., min_length=3, max_length=100)


class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = Field(None, min_length=5, max_length=300)
    schedule: Optional[str] = Field(None, min_length=3, max_length=100)
    date: Optional[date] = None
    max_participants: Optional[int] = Field(None, gt=0)

    @validator("name")
    def update_name_not_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Activity name must not be blank")
        return value

    @validator("description")
    def update_description_not_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Description must not be blank")
        return value

    @validator("schedule")
    def update_schedule_not_blank(cls, value):
        if value is not None and not value.strip():
            raise ValueError("Schedule must not be blank")
        return value

    @validator("date")
    def update_date_must_be_future(cls, value):
        if value is not None and value <= date.today():
            raise ValueError("Event date must be in the future")
        return value


@app.get("/activities/{activity_name}")
def get_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activities[activity_name]


@app.post("/activities")
def create_activity(activity: ActivityCreate):
    if activity.name in activities:
        raise HTTPException(status_code=400, detail="Activity name already exists")

    activities[activity.name] = activity.dict()
    return {"message": f"Created activity {activity.name}", "activity": activities[activity.name]}


@app.put("/activities/{activity_name}")
def update_activity(activity_name: str, update: ActivityUpdate):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    existing = activities[activity_name].copy()
    new_name = update.name or activity_name

    if new_name != activity_name and new_name in activities:
        raise HTTPException(status_code=400, detail="Activity name already exists")

    if update.description is not None:
        existing["description"] = update.description
    if update.schedule is not None:
        existing["schedule"] = update.schedule
    if update.date is not None:
        existing["date"] = update.date.isoformat()
    if update.max_participants is not None:
        if len(existing["participants"]) > update.max_participants:
            raise HTTPException(
                status_code=400,
                detail="Max participants cannot be less than current participant count"
            )
        existing["max_participants"] = update.max_participants

    if new_name != activity_name:
        del activities[activity_name]
        activities[new_name] = existing
    else:
        activities[activity_name] = existing

    return {"message": f"Updated activity {new_name}", "activity": existing}


@app.delete("/activities/{activity_name}")
def delete_activity(activity_name: str):
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    del activities[activity_name]
    return {"message": f"Deleted activity {activity_name}"}


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return activities


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is not already signed up
    if email in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )

    # Add student
    activity["participants"].append(email)
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    # Validate activity exists
    if activity_name not in activities:
        raise HTTPException(status_code=404, detail="Activity not found")

    # Get the specific activity
    activity = activities[activity_name]

    # Validate student is signed up
    if email not in activity["participants"]:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )

    # Remove student
    activity["participants"].remove(email)
    return {"message": f"Unregistered {email} from {activity_name}"}
