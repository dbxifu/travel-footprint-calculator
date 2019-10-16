#! ../venv/bin/python

from flask import Flask
from webassets.loaders import PythonLoader as PythonAssetsLoader

from flaskr import assets
from flaskr.models import db
from flaskr.controllers.main import main

from flaskr.extensions import (
    cache,
    assets_env,
    debug_toolbar,
    login_manager
)

from yaml import safe_load as yaml_safe_load

from markdown import markdown


def create_app(object_name):
    """
    An flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. flaskr.settings.ProductionConfig
    """

    app = Flask(__name__)

    # We bypass object_name (for now)
    object_name = 'flaskr.settings.DevelopmentConfig'

    # Load configuration
    app.config.from_object(object_name)

    # initialize the cache
    cache.init_app(app)

    # initialize the debug tool bar
    debug_toolbar.init_app(app)

    # initialize SQLAlchemy
    db.init_app(app)

    login_manager.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # register our blueprints
    app.register_blueprint(main)

    # Load content data from the YAML file
    content = {}
    with open('content.yml', 'r') as content_file:
        content = yaml_safe_load(content_file.read())

    # VERSION
    version = "0.0.0"
    with open('VERSION', 'r') as version_file:
        version = version_file.read().strip()

    # Inject it as global template var
    @app.context_processor
    def inject_template_global_variables():
        return dict(
            content=content,
            version=version,
        )

    # Markdown jinja2 filter
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown(text)

    return app
