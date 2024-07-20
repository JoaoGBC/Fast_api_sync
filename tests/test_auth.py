from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_api.models import User


def test_get_token(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["token_type"] == "Bearer"
    assert "access_token" in response.json()


def test_login(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"


def test_login_fail(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": "incorrect_password"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect username or passwod"
