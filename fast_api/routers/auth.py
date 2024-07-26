from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_api.database import get_session
from fast_api.models import User
from fast_api.schemas import Token
from fast_api.security import (
    create_access_token,
    get_current_user,
    verify_password,
)

router = APIRouter(prefix='/auth', tags=['auth'])
T_Session = Annotated[Session, Depends(get_session)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/token', response_model=Token)
def login_for_access_token(
    session: T_Session,
    form_data: T_OAuthForm,
):
    user: User | None = session.scalar(
        select(User).where(User.email == form_data.username)
    )
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Incorrect username or passwod',
        )
    accessToken = create_access_token(data={'sub': user.email})
    return {'access_token': accessToken, 'token_type': 'Bearer'}


@router.post('/refresh_token', response_model=Token)
def refresh_acess_token(user: T_CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})
    return {'access_token': new_access_token, 'token_type': 'Bearer'}
