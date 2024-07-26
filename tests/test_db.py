from sqlalchemy import select
from sqlalchemy.orm.session import Session

from fast_api.models import User


def test_create_user(session: Session):
    new_user = User(
        username='alice', password='secret', email='teste@test.com'
    )
    session.add(new_user)
    session.commit()

    user = session.scalar(select(User).where(User.username == 'alice'))
    assert user.username == 'alice'
