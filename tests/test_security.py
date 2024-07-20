from http import HTTPStatus

from fastapi.testclient import TestClient
from jwt import decode

from fast_api.security import create_access_token, settings


def test_jwt():
    data = {"sub": "test@test.com"}
    token = create_access_token(data)

    result = decode(
        token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert result["sub"] == data["sub"]
    assert result["exp"]


def test_jwt_invalid_token(client: TestClient):
    response = client.delete(
        "users/1", headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validade credentials"}


def test_jwt_payload_invalid(client: TestClient):
    data = {"sub": "email@invalido.com"}
    token = create_access_token(data)
    response = client.delete(
        "users/1", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {"detail": "Could not validade credentials"}
