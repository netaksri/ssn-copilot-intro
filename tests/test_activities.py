from urllib.parse import quote


def activity_signup_path(activity_name: str) -> str:
    return f"/activities/{quote(activity_name, safe='')}/signup"


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_current_activity_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_adds_new_participant(client):
    email = "new.student@mergington.edu"
    response = client.post(activity_signup_path("Tennis Club"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Tennis Club"}

    activities_response = client.get("/activities")
    assert email in activities_response.json()["Tennis Club"]["participants"]


def test_signup_returns_404_for_unknown_activity(client):
    response = client.post(activity_signup_path("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_returns_400_when_student_already_registered(client):
    response = client.post(
        activity_signup_path("Chess Club"),
        params={"email": "michael@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Already signed up for this activity"}


def test_signup_returns_400_when_activity_is_full(client):
    from src.app import activities

    max_participants = activities["Basketball Team"]["max_participants"]
    activities["Basketball Team"]["participants"] = [
        f"player{index}@mergington.edu" for index in range(max_participants)
    ]

    response = client.post(
        activity_signup_path("Basketball Team"),
        params={"email": "late.player@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Activity is full"}


def test_unregister_removes_existing_participant(client):
    email = "alex@mergington.edu"
    response = client.delete(activity_signup_path("Basketball Team"), params={"email": email})

    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from Basketball Team"}

    activities_response = client.get("/activities")
    assert email not in activities_response.json()["Basketball Team"]["participants"]


def test_unregister_returns_404_for_unknown_activity(client):
    response = client.delete(activity_signup_path("Unknown Club"), params={"email": "student@mergington.edu"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_returns_404_for_missing_participant(client):
    response = client.delete(
        activity_signup_path("Tennis Club"),
        params={"email": "missing.student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found for this activity"}