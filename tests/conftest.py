import pytest
from peewee import SqliteDatabase
from app import create_app
from app.models import User, Url, Event

# 1. Create the isolated in-memory database
test_db = SqliteDatabase(':memory:')

@pytest.fixture(autouse=True)
def setup_test_database():
    """
    This fixture runs automatically before every test.
    It forces the models to use SQLite instead of Postgres.
    """
    # Bind the models to our test DB (ignoring the proxy)
    test_db.bind([User, Url, Event], bind_refs=False, bind_backrefs=False)
    test_db.connect()
    test_db.create_tables([User, Url, Event])
    
    yield # Test runs here
    
    # Cleanup
    test_db.drop_tables([User, Url, Event])
    test_db.close()

@pytest.fixture
def app():
    flask_app = create_app()
    flask_app.config.update({
        "TESTING": True,
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()