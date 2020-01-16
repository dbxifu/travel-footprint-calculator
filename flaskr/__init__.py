#! ../venv/bin/python
import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


from flask import Flask, url_for
from flask.cli import ScriptInfo
from webassets.loaders import PythonLoader as PythonAssetsLoader


from flaskr import assets
from flaskr.models import db, Estimation, EstimationView
from flaskr.controllers.main_controller import main

from flaskr.extensions import (
    admin,
    cache,
    assets_env,
    debug_toolbar,
    login_manager,
    basic_auth
)

from flaskr.content import content
from flaskr.core import increment_hit_counter, get_hit_counter

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

    # We bypass object_name (for dev)
    if type(object_name) == ScriptInfo:
        object_name = 'flaskr.settings.DevelopmentConfig'

    # Load configuration
    app.config.from_object(object_name)

    # Initialize
    cache.init_app(app)
    debug_toolbar.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    admin.add_view(EstimationView(Estimation, db.session))
    basic_auth.init_app(app)

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # register our blueprints
    app.register_blueprint(main)

    app.config['BASIC_AUTH_USERNAME'] = os.getenv('ADMIN_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

    # VERSION (move to version.py is necessary)
    version = "0.0.0"
    with open('VERSION', 'r') as version_file:
        version = version_file.read().strip()

    # Inject it as global template var
    @app.context_processor
    def inject_template_global_variables():
        return dict(
            content=content,
            version=version,
            visits=get_hit_counter(),
        )

    # Markdown jinja2 filter
    @app.template_filter('markdown')
    def markdown_filter(text):
        return markdown(text, extensions=['extra'])

    # Authentication Gate for the Admin
    @app.before_first_request
    def restrict_admin_url():
        endpoint = 'admin.index'
        url = url_for(endpoint)
        admin_index = app.view_functions.pop(endpoint)

        @app.route(url, endpoint=endpoint)
        @basic_auth.required
        # @roles_required('admin')
        def secure_admin_index():
            return admin_index()

    return app
