
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

# Capture the initial participants for all activities at import time
_initial_participants = {
    name: list(activity["participants"]) for name, activity in activities.items() if "participants" in activity
}

# Helper to reset activities for test isolation (since in-memory DB)
def reset_activities():
    app.dependency_overrides = {}
    for name, activity in activities.items():
        if "participants" in activity and name in _initial_participants:
            activity["participants"] = _initial_participants[name][:]

@pytest.fixture(autouse=True)
def run_around_tests():
    reset_activities()
    yield
    reset_activities()

def test_list_activities():
    # Arrange
    # (No setup needed, uses default data)
    # Act
    response = client.get("/activities")
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_for_activity():
    # Arrange
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 200
    assert email in client.get("/activities").json()[activity]["participants"]

def test_prevent_duplicate_signup():
    # Arrange
    email = "michael@mergington.edu"  # already signed up
    activity = "Chess Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_unregister_participant():
    # Arrange
    email = "michael@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 200
    assert email not in client.get("/activities").json()[activity]["participants"]

def test_unregister_nonexistent_participant():
    # Arrange
    email = "notfound@mergington.edu"
    activity = "Chess Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not registered" in response.json()["detail"]

def test_signup_nonexistent_activity():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    # Arrange
    email = "someone@mergington.edu"
    activity = "Nonexistent Club"
    # Act
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    # Assert
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]
