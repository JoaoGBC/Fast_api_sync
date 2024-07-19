from http import HTTPStatus

from fastapi.testclient import TestClient

from fast_api.models import User
from fast_api.schemas import UserPublic


def test_root_deve_retornar_ok_e_ola_mundo(client: TestClient):
    response = client.get("/")

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "Olá Mundo!"}


def test_ola_mundo_deve_retornar_html(client: TestClient):
    response = client.get("/ola_mundo")

    html_content = """
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Document</title>
        </head>
        <body>
            <h1> Olá Mundo! </h1>
        </body>
        </html>"""
    assert response.status_code == HTTPStatus.OK
    assert response.text == html_content


def test_create_user(client: TestClient):
    response = client.post(
        "/users/",
        json={
            "username": "testusername",
            "password": "password",
            "email": "test@test.com",
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        "id": 1,
        "username": "testusername",
        "email": "test@test.com",
    }


def test_create_user_fail_with_duplicate_email(client: TestClient, user: User):
    user_schema = UserPublic.model_validate(user).model_dump()
    user_schema["password"] = "testpassword"
    user_schema["username"] = "valid_name"
    response = client.post("/users/", json=user_schema)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Email already exists."


def test_create_user_fail_with_duplicate_username(
    client: TestClient, user: User
):
    user_schema = UserPublic.model_validate(user).model_dump()
    user_schema["password"] = "testpassword"
    user_schema["email"] = "valid@email.com"
    response = client.post("/users/", json=user_schema)
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Username already exists."


def test_read_user_by_id(client: TestClient, user: User):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(f"/users/{user.id}")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == user_schema


def test_read_user_by_id_fail(client: TestClient):
    response = client.get("/users/1")
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json()["detail"] == "User not found"


def test_read_users(client: TestClient):
    response = client.get("/users")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": []}


def test_read_users_with_user(client: TestClient, user: User):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get("/users")
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"users": [user_schema]}


def test_update_user(client: TestClient, user: User, token):
    response = client.put(
        f"/users/{user.id}",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
        headers={"Authorization": f'Bearer {token['access_token']}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {
        "username": "bob",
        "email": "bob@example.com",
        "id": 1,
    }


def test_update_user_fail(client: TestClient, user: User, token):
    response = client.put(
        f"users/{user.id + 1}",
        json={
            "username": "bob",
            "email": "bob@example.com",
            "password": "mynewpassword",
        },
        headers={"Authorization": f'Bearer {token['access_token']}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Not enough permission"


def test_delete_user(client: TestClient, user: User, token):
    response = client.delete(
        "/users/1",
        headers={"Authorization": f'Bearer {token['access_token']}'},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json() == {"message": "User deleted"}


def test_delete_user_fail(client: TestClient, user: User, token):
    response = client.delete(
        f"/users/{user.id + 1}",
        headers={"Authorization": f'Bearer {token['access_token']}'},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Not enough permission"


def test_get_token(client: TestClient, user: User):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json()["token_type"] == "Bearer"
    assert "access_token" in response.json()


def test_login(client: TestClient, user: User):
    response = client.post(
        "/token",
        data={"username": user.email, "password": user.clean_password},
    )
    assert response.status_code == HTTPStatus.OK
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "Bearer"


def test_login_fail(client: TestClient, user: User):
    response = client.post(
        "/token",
        data={"username": user.email, "password": "incorrect_password"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json()["detail"] == "Incorrect username or passwod"
