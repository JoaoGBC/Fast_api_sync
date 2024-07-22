from datetime import datetime, timedelta
from http import HTTPStatus

from fastapi.testclient import TestClient
from freezegun import freeze_time

from fast_api.models import User
from fast_api.settings import Settings


def test_token_expired_after_time(client: TestClient, user: User):
    data = datetime.now()
    with freeze_time():
        response = client.post(
            "/auth/token",
            data={
                "username": user.email,
                "password": user.clean_password,
            },
        )
        assert response.status_code == HTTPStatus.OK
        token = response.json()["access_token"]

    with freeze_time(
        data + timedelta(Settings().ACESS_TOKEN_EXPIRE_MINUTES + 1)
    ):
        response = client.put(
            f"/users/{user.id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "username": "wrongwrong",
                "email": "wrong@wrong.com",
                "password": "wrong",
            },
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validade credentials"}


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


def test_login_wrong_password(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": user.email, "password": "incorrect_password"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect username or passwod"


def test_login_wrong_email(client: TestClient, user: User):
    response = client.post(
        "/auth/token",
        data={"username": "wrongpassword", "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect username or passwod"


def test_refresh_token(client: TestClient, token):
    response = client.post(
        "/auth/refresh_token",
        headers={"Authorization": f"Bearer {token['access_token']}"},
    )

    data = response.json()
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in data
    assert "token_type" in data
    assert data["token_type"] == "Bearer"


def test_refresh_token_expired_token(client: TestClient, user: User):
    date = datetime.now()
    with freeze_time(date):
        response = client.post(
            "/auth/token",
            data={"username": user.email, "password": user.clean_password},
        )
        token = response.json()

        assert response.status_code == HTTPStatus.OK
        assert "access_token" in token
        assert "token_type" in token
        assert token["token_type"] == "Bearer"

    with freeze_time(
        date + timedelta(minutes=Settings().ACESS_TOKEN_EXPIRE_MINUTES + 1)
    ):
        response = client.post(
            "/auth/refresh_token",
            headers={"Authorization": f"Bearer {token['access_token']}"},
        )
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.json() == {"detail": "Could not validade credentials"}
