"""Defines fixtures available to all tests.
See: https://pytest-flask.readthedocs.io/en/latest/features.html
"""
import logging
import os

import jwt
import factories
from backend import authorization, create_app
from backend.extensions import db as database
from backend.utils import dockerhub
from pytest import fixture
from pytest_postgresql.janitor import DatabaseJanitor

from tests import db_instances

TEST_DB = 'test_database'
VERSION = 12.2  # postgresql version number


# -------------------------------------------------------------------
# Server Fixtures ---------------------------------------------------

@fixture(scope='session')
def sql_database(postgresql_proc):
    """Create a temp Postgres database for the tests."""
    USER = postgresql_proc.user
    HOST = postgresql_proc.host
    PORT = postgresql_proc.port
    with DatabaseJanitor(USER, HOST, PORT, TEST_DB, VERSION) as db:
        yield db


@fixture(scope='session')
def session_environment(sql_database):
    """Patch fixture to set test env variables."""
    # Flask framework environments
    os.environ['SECRET_KEY'] = 'not-so-secret-for-testing'
    # Database environments
    os.environ['DB_USER'] = str(sql_database.user)
    os.environ['DB_PASSWORD'] = ""
    os.environ['DB_HOST'] = str(sql_database.host)
    os.environ['DB_PORT'] = str(sql_database.port)
    os.environ['DB_NAME'] = str(sql_database.dbname)
    # OIDC environments
    os.environ['EGI_CLIENT_ID'] = "eosc-perf"
    os.environ['EGI_CLIENT_SECRET'] = "not-so-secret-for-testing"
    os.environ['ADMIN_ENTITLEMENTS'] = "admins"
    # Email and notification configuration.
    os.environ['MAIL_SUPPORT'] = "support@example.com"
    os.environ['MAIL_SERVER'] = "localhost"
    os.environ['MAIL_PORT'] = str(5025)
    os.environ['MAIL_FROM'] = "no-reply@example.com"


@fixture(scope="session")
def app(session_environment):
    """Create application for the tests."""
    app = create_app(config_base="backend.settings", TESTING=True)
    app.logger.setLevel(logging.CRITICAL)
    with app.app_context():
        yield app


@fixture(scope='session')
def db(app):
    """Create database for the tests."""
    database.create_all()
    [factories.DBUser(**x) for x in db_instances.users]
    [factories.DBTag(**x) for x in db_instances.tags]
    [factories.DBBenchmark(**x) for x in db_instances.benchmarks]
    [factories.DBSite(**x) for x in db_instances.sites]
    [factories.DBFlavor(**x) for x in db_instances.flavors]
    [factories.DBResult(**x) for x in db_instances.results]
    database.session.commit()
    yield database
    database.drop_all()


@fixture(scope='function', autouse=True)
def session(db):
    """Uploads a new database session for a test."""
    db.session.begin(nested=True)  # Rollback app commits
    yield db.session
    db.session.rollback()   # Discard test changes
    db.session.close()      # Next test gets a new session


# -------------------------------------------------------------------
# Authorization & Authentication Fixtures ---------------------------

@fixture(scope='function')
def token_sub(request):
    """Returns the sub to include on the user token."""
    return request.param if hasattr(request, 'param') else None


@fixture(scope='function')
def token_iss(request):
    """Returns the iss to include on the user token."""
    return request.param if hasattr(request, 'param') else None


@fixture(scope="function")
def access_token(app, token_sub, token_iss):
    """Generates a token encrypted with the app key"""
    return jwt.encode(
        {
            'sub': token_sub, 'iss': token_iss,
            "exp": 9999999999,
            "iat": 0000000000,
            "scope": "openid email groups",
        },
        app.config.get('SECRET_KEY'),
        algorithm='HS256'
    ) if token_sub and token_iss else None


@fixture(scope='function')
def grant_admin(monkeypatch):
    """Patch fixture to test function as admin user."""
    monkeypatch.setattr(authorization, "is_admin", lambda: True)


@fixture(scope='function')
def mock_docker_registry(monkeypatch):
    """Patch fixture to test function with valid oidc token."""
    def always_true(*arg, **kwarg): return True
    monkeypatch.setattr(dockerhub, "valid_image", always_true)


# -------------------------------------------------------------------
# Request Fixtures --------------------------------------------------

@fixture(scope='function')
def endpoint(request):
    """Fixture that return the endpoint for the request."""
    return request.param


@fixture(scope='function')
def query(request):
    """Fixture that return the query for the request."""
    return request.param if hasattr(request, 'param') else {}


@fixture(scope="function")
def headers(access_token):
    headers = {}
    if access_token:
        headers['Authorization'] = 'Bearer {}'.format(access_token)
    return headers if headers != {} else None


@fixture(scope='function')
def body(request):
    """Fixture that return the body for the request."""
    return request.param if hasattr(request, 'param') else {}


@fixture(scope='function')
def response_GET(client, url, headers):
    """Fixture that return the result of a GET request."""
    return client.get(url)


@fixture(scope='function')
def response_POST(client, url, headers, body):
    """Fixture that return the result of a POST request."""
    return client.post(url, headers=headers, json=body)


@fixture(scope='function')
def response_PUT(client, url, headers, body):
    """Fixture that return the result of a PUT request."""
    return client.put(url, headers=headers, json=body)


@fixture(scope='function')
def response_PATCH(client, url, headers, body):
    """Fixture that return the result of a PATCH request."""
    return client.patch(url, headers=headers, json=body)


@fixture(scope='function')
def response_DELETE(client, headers, url):
    """Fixture that return the result of a DELETE request."""
    return client.delete(url, headers=headers)
