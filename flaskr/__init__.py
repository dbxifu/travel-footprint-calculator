#! ../venv/bin/python
import os
from markdown import markdown

from dotenv import load_dotenv, find_dotenv, dotenv_values
# Load config from .env ; do this before importing local libs (and flask)
# 1. Write into OS environment -- if this fails you forgot to create .env file
load_dotenv(find_dotenv(raise_error_if_not_found=True), override=True)
# 2. Load it as well to inject it later into app.config
local_env = dotenv_values(find_dotenv())
# 3. Cast integers to integers
for key in local_env.keys():
    try:
        local_env[key] = int(local_env[key])
    except ValueError:
        pass


from flask import Flask, url_for
from flask.cli import ScriptInfo
from webassets.loaders import PythonLoader as PythonAssetsLoader


from flaskr import assets
from flaskr.models import db, Estimation, EstimationView
from flaskr.controllers.main_controller import main
from flaskr.extensions import (
    admin,
    assets_env,
    basic_auth,
    cache,
    debug_toolbar,
    login_manager,
    mail,
    session,
    captcha,
    icon2html,
)
from flaskr.content import content
from flaskr.core import increment_hit_counter, get_hit_counter


def create_app(object_name):
    """
    A flask application factory, as explained here:
    http://flask.pocoo.org/docs/patterns/appfactories/

    Arguments:
        object_name: the python path of the config object,
                     e.g. flaskr.settings.ProductionConfig
    """

    app = Flask(__name__)

    # We bypass object_name (for dev with flask run)
    if type(object_name) == ScriptInfo:
        object_name = 'flaskr.settings.DevelopmentConfig'

    # Load the configuration
    app.config.from_object(object_name)
    app.config.update(**local_env)

    app.config['BASIC_AUTH_USERNAME'] = os.getenv('ADMIN_USERNAME')
    app.config['BASIC_AUTH_PASSWORD'] = os.getenv('ADMIN_PASSWORD')

    app.config['CAPTCHA_ENABLE'] = True
    app.config['CAPTCHA_LENGTH'] = 5
    app.config['CAPTCHA_WIDTH'] = 256
    app.config['CAPTCHA_HEIGHT'] = 158
    app.config['SESSION_TYPE'] = 'sqlalchemy'

    # Initialize
    cache.init_app(app)
    session.init_app(app)
    captcha.init_app(app)
    mail.init_app(app)
    debug_toolbar.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    admin.add_view(EstimationView(Estimation, db.session))
    basic_auth.init_app(app)

    # For session storage
    app.session_interface.db.create_all()

    # Import and register the different asset bundles
    assets_env.init_app(app)
    assets_loader = PythonAssetsLoader(assets)
    for name, bundle in assets_loader.load_bundles().items():
        assets_env.register(name, bundle)

    # Register our blueprints
    app.register_blueprint(main)

    # VERSION (move to version.py ?)
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
        text = icon2html(text)
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
