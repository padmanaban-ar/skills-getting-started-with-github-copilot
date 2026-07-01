import copy
import urllib.parse

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_data = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original_data)


def test_get_activities_returns_activity_list():
    # Arrange
    url = "/activities"

    # Act
    response = client.get(url)

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "new.student@mergington.edu"
    url = f"/activities/{urllib.parse.quote(activity_name, safe='')}/signup?email={urllib.parse.quote(email, safe='')}"

    # Act
    response = client.post(url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Programming Class"
    email = "duplicate.student@mergington.edu"
    signup_url = f"/activities/{urllib.parse.quote(activity_name, safe='')}/signup?email={urllib.parse.quote(email, safe='')}"

    # Act
    first_response = client.post(signup_url)
    second_response = client.post(signup_url)

    # Assert
    assert first_response.status_code == 200
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Student is already signed up for this activity"


def test_remove_participant_unregisters_student():
    # Arrange
    activity_name = "Gym Class"
    email = "remove.student@mergington.edu"
    signup_url = f"/activities/{urllib.parse.quote(activity_name, safe='')}/signup?email={urllib.parse.quote(email, safe='')}"
    client.post(signup_url)
    delete_url = f"/activities/{urllib.parse.quote(activity_name, safe='')}/participants?email={urllib.parse.quote(email, safe='')}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_remove_missing_participant_returns_404():
    # Arrange
    activity_name = "Art Club"
    email = "missing.student@mergington.edu"
    delete_url = f"/activities/{urllib.parse.quote(activity_name, safe='')}/participants?email={urllib.parse.quote(email, safe='')}"

    # Act
    response = client.delete(delete_url)

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
