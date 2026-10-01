import os

os.environ["GOOGLE_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_page():
    response = client.get("/")

    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admin_login_page():
    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "Admin Login" in response.text