from http import HTTPStatus

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from fast_api.schemas import Message, UserDb, UserList, UserPublic, UserSchema

app = FastAPI()

mock_database = []


@app.get("/", status_code=HTTPStatus.OK, response_model=Message)
def read_root():
    return {"message": "Olá Mundo!"}


@app.get("/ola_mundo", status_code=HTTPStatus.OK, response_class=HTMLResponse)
def hello_world():
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
    return html_content


@app.post("/users/", status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    print(user.model_dump())
    user_with_id = UserDb(**user.model_dump(), id=len(mock_database) + 1)
    mock_database.append(user_with_id)
    return user_with_id


@app.get("/users", status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {"users": mock_database}


@app.put("/users/{user_id}", response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(mock_database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )
    user_with_id = UserDb(**user.model_dump(), id=user_id)
    mock_database[user_id - 1] = user_with_id
    return mock_database[user_id - 1]


@app.delete("/users/{user_id}", response_model=Message)
def delete_user(user_id: int):
    if user_id > len(mock_database) or user_id < 1:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="User not found"
        )

    del mock_database[user_id - 1]

    return {"message": "User deleted"}
