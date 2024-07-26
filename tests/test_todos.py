import datetime
from http import HTTPStatus
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy.orm.session import Session

from fast_api.models import TodoState, User
from tests.conftest import TodoFactory


def test_create_todo(
    client: TestClient, session: Session, user: User, token: Any
):
    response = client.post(
        '/todos',
        json={
            'title': 'teste',
            'description': 'teste todo description',
            'state': 'draft',
        },
        headers={'Authorization': f"Bearer {token['access_token']}"},
    )

    assert response.status_code == HTTPStatus.CREATED
    assert 'created_at' in response.json()

    data = datetime.datetime.strptime(
        response.json()['created_at'], '%Y-%m-%dT%H:%M:%S'
    )

    assert response.json() == {
        'id': 1,
        'title': 'teste',
        'description': 'teste todo description',
        'state': 'draft',
        'user_id': user.id,
        'created_at': data.strftime('%Y-%m-%dT%H:%M:%S'),
        'updated_at': None,
    }


def test_list_todos_should_return_5_todos(
    client: TestClient, session: Session, user: User, token: Any
):
    expected_todos = 5
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos',
        headers={'Authorization': f"Bearer {token['access_token']}"},
    )

    assert response.status_code == HTTPStatus.OK
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_pagination_should_return_2_todos(
    client: TestClient, user: User, session: Session, token: dict
):
    expected_todos = 2
    session.bulk_save_objects(TodoFactory.create_batch(5, user_id=user.id))
    session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token["access_token"]}'},
    )

    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_title_should_return_5_todos(
    client: TestClient,
    user: User,
    session: Session,
    token: dict,
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, title='Test todo 1', user_id=user.id)
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test todo 1',
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_description_should_return_5_todos(
    client: TestClient, user: User, session: Session, token: dict
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5, user_id=user.id, description='Todo description 1'
        )
    )
    session.commit()

    response = client.get(
        '/todos/?description=Todo description 1',
        headers={'Authorization': f'Bearer {token["access_token"]}'},
    )
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_state_should_return_5_todos(
    client: TestClient, user: User, session: Session, token: dict
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(5, user_id=user.id, state=TodoState.done)
    )
    session.commit()

    response = client.get(
        '/todos/?state=done',
        headers={'Authorization': f'Bearer {token["access_token"]}'},
    )
    assert len(response.json()['todos']) == expected_todos


def test_list_todos_filter_combined_should_return_5_todos(
    session: Session, user: User, client: TestClient, token: dict
):
    expected_todos = 5
    session.bulk_save_objects(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title='Test todo combined',
            description='combined description',
            state=TodoState.done,
        )
    )
    session.bulk_save_objects(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='Other description',
            state=TodoState.todo,
        )
    )
    session.commit()

    response = client.get(
        '/todos/?title=Test todo combined&description=combined&state=done',
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )
    assert len(response.json()['todos']) == expected_todos


def test_delete_todo(
    session: Session, client: TestClient, user: User, token: dict
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )

    assert response.json() == {'message': 'Task has been deleted sucessfully'}


def test_patch_todo(
    client: TestClient, session: Session, user: User, token: dict
):
    todo = TodoFactory(user_id=user.id)
    session.add(todo)
    session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json()['title'] == 'teste!'


def test_patch_todo_error(
    client: TestClient, session: Session, user: User, token: dict
):
    response = client.patch(
        f'/todos/{10}',
        json={'title': 'teste!'},
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}


def test_delete_todo_error(client: TestClient, token: dict):
    response = client.delete(
        f'/todos/{10}',
        headers={'Authorization': f'Bearer {token['access_token']}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Task not found.'}
