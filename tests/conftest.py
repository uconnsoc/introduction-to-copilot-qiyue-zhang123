"""
Pytest configuration and shared fixtures for API tests.
"""
import pytest
from fastapi.testclient import TestClient
from copy import deepcopy
import sys
from pathlib import Path

# Add src directory to path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from src import app as app_module


# Store original activities state
ORIGINAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Practice and compete in basketball games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 15,
        "participants": []
    },
    "Soccer Club": {
        "description": "Train and play soccer matches",
        "schedule": "Wednesdays and Saturdays, 3:00 PM - 5:00 PM",
        "max_participants": 22,
        "participants": []
    },
    "Art Club": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Mondays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": []
    },
    "Drama Club": {
        "description": "Act in plays and learn theater skills",
        "schedule": "Tuesdays, 4:00 PM - 6:00 PM",
        "max_participants": 20,
        "participants": []
    },
    "Debate Club": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Thursdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": []
    },
    "Science Club": {
        "description": "Conduct experiments and learn about scientific concepts",
        "schedule": "Fridays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": []
    }
}


@pytest.fixture
def client():
    """
    Provides a TestClient instance for making requests to the API.
    Resets the activities database before each test to ensure test isolation.
    """
    # Reset activities to original state before each test
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    
    return TestClient(app_module.app)


@pytest.fixture
def sample_email():
    """Provides a sample student email for tests."""
    return "student@mergington.edu"


@pytest.fixture
def sample_activity_name():
    """Provides a sample activity name that exists in the database."""
    return "Chess Club"


@pytest.fixture
def empty_activity_name():
    """Provides an activity name that has no participants."""
    return "Basketball Team"


@pytest.fixture
def nonexistent_activity():
    """Provides an activity name that doesn't exist."""
    return "Nonexistent Activity"
