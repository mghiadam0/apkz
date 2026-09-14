import pytest
from quicknotes import create_app
from quicknotes.extensions import db
@pytest.fixture
def app(tmp_path):
    a=create_app({'TESTING':True,'WTF_CSRF_ENABLED':False,'SQLALCHEMY_DATABASE_URI':'sqlite:///'+str(tmp_path/'test.db'),'ENABLE_SCHEDULER':False})
    yield a
    with a.app_context():db.drop_all()
@pytest.fixture
def client(app):return app.test_client()
