import pytest
from app import create_app, db
from app.models import User
from app.services import hash_password


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test',
    })
    with app.app_context():
        db.create_all()
        user = User(first_name='A', last_name='B', full_address='Addr', email='ok@example.com', password_hash=hash_password('pass'), status='APPROVED', locale='en-US')
        db.session.add(user)
        db.session.commit()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()
