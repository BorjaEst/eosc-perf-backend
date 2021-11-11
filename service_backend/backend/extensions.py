"""This module implements the loading of multiple flask extensions to
extend the basic provided functionality to the API requirements.
For more information about flask and extensions see:

https://flask.palletsprojects.com/en/2.0.x/extensions

Each extension requires of a specific class initialization which is
lately initialized in the application factory using the settings and
configurations from the environment.
"""
from authlib.integrations.flask_client import OAuth
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_mailman import Mail
from flask_migrate import Migrate
from flask_smorest import Api
from flask_sqlalchemy import SQLAlchemy

#: Flask extension that provides support for handling oidc Access Tokens
oauth = OAuth()

#: Flask extension that provides bcrypt hashing utilities
bcrypt = Bcrypt()

#: Flask extension that adds caching support for various backends
cache = Cache()

#: Flask framework library for creating REST APIs (i.e. OpenAPI)
api = Api()

#: Flask extension hat adds support for SQLAlchemy
db = SQLAlchemy()

#: Flask extension that handles SQLAlchemy database migrations using Alembic
migrate = Migrate()

#: Flask extension providing simple email sending capabilities
mail = Mail()
