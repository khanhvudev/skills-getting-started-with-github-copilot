from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)
original_activities = deepcopy(activities)


def reset_activities() -> None:
    activities.clear()
    activities.update(deepcopy(original_activities))


def setup_function() -> None:
    reset_activities()


def test_root_redirects_to_static_page() -> None:
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seed_data() -> None:
    # Arrange
    expected_activity_names = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert expected_activity_names.issubset(data.keys())


def test_signup_adds_participant_and_rejects_duplicates() -> None:
    # Arrange
    email = "new.student@mergington.edu"

    # Act
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities["Chess Club"]["participants"]

    # Act
    duplicate_response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_participant() -> None:
    # Arrange
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_returns_404_when_participant_is_missing() -> None:
    # Arrange
    missing_email = "missing@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Chess Club/unregister",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"