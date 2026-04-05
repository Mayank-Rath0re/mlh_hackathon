import pytest
from app import create_app
from app.database import db
from app.models import User, Url, Event

@pytest.fixture
def app():
    # Use an in-memory SQLite database for blazing fast, isolated tests
    db.init(':memory:')
    db.create_tables([User, Url, Event])
    
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    
    yield app
    
    db.drop_tables([User, Url, Event])
    db.close()

@pytest.fixture
def client(app):
    return app.test_client()