from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_api.database import get_session
from fast_api.models import Todo, TodoState, User
from fast_api.schemas import (
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)
from fast_api.security import get_current_user

router = APIRouter(prefix='/todos', tags=['todos'])

T_Current_User = Annotated[User, Depends(get_current_user)]
T_Session = Annotated[Session, Depends(get_session)]


@router.post('/', response_model=TodoPublic, status_code=HTTPStatus.CREATED)
def create_todo(
    todo: TodoSchema,
    current_user: T_Current_User,
    session: T_Session,
):
    db_todo = Todo(**todo.model_dump(), user_id=current_user.id)
    session.add(db_todo)
    session.commit()
    return db_todo


@router.get('/', response_model=TodoList)
def list_todos(  # noqa
    session: T_Session,
    current_user: T_Current_User,
    title: str | None = None,
    description: str | None = None,
    state: Annotated[TodoState, Query()] = None,
    offset: int | None = None,
    limit: int | None = None,
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if title:
        query = query.filter(Todo.title.contains(title))

    if description:
        query = query.filter(Todo.description.contains(description))

    if state:
        query = query.filter(Todo.state == state)

    todos = session.scalars(query.offset(offset).limit(limit)).all()

    return {'todos': todos}


@router.patch('/{todo_id}', response_model=TodoUpdate)
def patch_todo(
    todo_id: int,
    session: T_Session,
    current_user: T_Current_User,
    todo: TodoUpdate,
):
    db_todo = session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)  # essa linha não é obrigatoria.
    session.commit()
    session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
def delete_todo(
    todo_id: int, session: T_Session, current_user: T_Current_User
):
    todo = session.scalar(
        select(Todo).where(Todo.user_id == current_user.id, Todo.id == todo_id)
    )
    if not todo:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='Task not found.'
        )

    session.delete(todo)
    session.commit()
    return {'message': 'Task has been deleted sucessfully'}
