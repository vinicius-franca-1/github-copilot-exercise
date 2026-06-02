import copy
import urllib.parse as parse

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities_returns_all(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success(client):
    activity = parse.quote("Chess Club")
    resp = client.post(f"/activities/{activity}/signup", params={"email": "newstudent@mergington.edu"})
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_duplicate_email(client):
    activity = parse.quote("Chess Club")
    resp = client.post(f"/activities/{activity}/signup", params={"email": "michael@mergington.edu"})
    assert resp.status_code == 400
    assert "already signed up" in resp.json().get("detail", "").lower()


def test_signup_activity_not_found(client):
    activity = parse.quote("Nonexistent")
    resp = client.post(f"/activities/{activity}/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404


def test_unregister_success(client):
    activity = parse.quote("Chess Club")
    resp = client.delete(f"/activities/{activity}/signup", params={"email": "michael@mergington.edu"})
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]


def test_unregister_participant_not_found(client):
    activity = parse.quote("Chess Club")
    resp = client.delete(f"/activities/{activity}/signup", params={"email": "notfound@x.com"})
    assert resp.status_code == 404
    assert "participant not found" in resp.json().get("detail", "").lower()


def test_unregister_activity_not_found(client):
    activity = parse.quote("Nope")
    resp = client.delete(f"/activities/{activity}/signup", params={"email": "x@x.com"})
    assert resp.status_code == 404
