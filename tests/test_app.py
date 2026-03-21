import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess = data["Chess Club"]
    assert "description" in chess
    assert "schedule" in chess
    assert "max_participants" in chess
    assert "participants" in chess
    assert isinstance(chess["participants"], list)

def test_signup_valid_activity():
    # Use a copy or reset, but for simplicity, assume initial state
    initial_participants = activities["Chess Club"]["participants"].copy()
    response = client.post("/activities/Chess Club/signup", json={"email": "test@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test@mergington.edu" in data["message"]
    # Check that participant was added
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]
    # Restore
    activities["Chess Club"]["participants"] = initial_participants

def test_signup_invalid_activity():
    response = client.post("/activities/Nonexistent Activity/signup", json={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert "Activity not found" in data["detail"]

def test_static_file_access():
    response = client.get("/static/index.html")
    assert response.status_code == 200
    # Assuming index.html exists and has some content
    assert b"html" in response.content.lower()

# Additional tests for edge cases
def test_signup_duplicate_email():
    # Assuming duplicates are allowed, as code doesn't check
    initial_count = len(activities["Chess Club"]["participants"])
    client.post("/activities/Chess Club/signup", json={"email": "duplicate@mergington.edu"})
    client.post("/activities/Chess Club/signup", json={"email": "duplicate@mergington.edu"})
    assert len(activities["Chess Club"]["participants"]) == initial_count + 2
    # Clean up
    activities["Chess Club"]["participants"] = activities["Chess Club"]["participants"][:initial_count]

def test_activities_structure():
    response = client.get("/activities")
    data = response.json()
    for name, activity in data.items():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
        assert activity["max_participants"] > 0