from jwt import decode

from fast_api.security import ALGORITHM, SECRET_KEY, create_access_token


def test_jwt():
    data = {"sub": "test@test.com"}
    token = create_access_token(data)

    result = decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])

    assert result["sub"] == data["sub"]
    assert result["exp"]
