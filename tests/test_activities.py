import copy

from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def reset_activities():
    original = {
        name: {
            "description": details["description"],
            "schedule": details["schedule"],
            "max_participants": details["max_participants"],
            "participants": list(details["participants"]),
        }
        for name, details in activities.items()
    }
    activities.clear()
    activities.update(original)


def test_get_activities_returns_activity_list():
    # Arrange
    reset_activities()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_participant():
    # Arrange
    reset_activities()
    email = "newstudent@mergington.edu"
    activity_name = "Chess Club"
    original_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert len(activities[activity_name]["participants"]) == original_count + 1
    assert email in activities[activity_name]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    reset_activities()
    email = "michael@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"].lower()


def test_signup_unknown_activity_returns_404():
    # Arrange
    reset_activities()
    activity_name = "Not Real"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant():
    # Arrange
    reset_activities()
    email = "daniel@mergington.edu"
    activity_name = "Chess Club"
    original_count = len(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert len(activities[activity_name]["participants"]) == original_count - 1
    assert email not in activities[activity_name]["participants"]


def test_unregister_missing_participant_returns_404():
    # Arrange
    reset_activities()
    email = "missingstudent@mergington.edu"
    activity_name = "Chess Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants?email={email}")

    # Assert
    assert response.status_code == 404
    assert "not signed up" in response.json()["detail"].lower()
