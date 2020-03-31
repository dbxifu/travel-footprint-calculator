import tempfile


# Configuration should be done in .env file
# Create it first:
#     cp .env.dist .env
# And then edit it with your own sauce.
# The contents of .env will override values in here.


class Config(object):
    FLASK_RUN_EXTRA_FILES="content.yml"


class ProductionConfig(Config):
    ENV = 'production'

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database_prod.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'simple'


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'null'
    ASSETS_DEBUG = True


db_file = tempfile.NamedTemporaryFile()


class TestConfig(Config):
    ENV = 'test'
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False

    SQLALCHEMY_DATABASE_URI = 'sqlite:///../%s' % db_file.name
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CACHE_TYPE = 'null'
    WTF_CSRF_ENABLED = False
