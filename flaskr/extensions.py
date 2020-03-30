from flask_admin import Admin
from flask_basicauth import BasicAuth
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_assets import Environment as Assets
from flask_mail import Mail

from flaskr.models import User

# Setup flask cache
cache = Cache()

# Init flask assets
assets_env = Assets()

# Mail handler
mail = Mail()

# Debug toolbar for easy dev (disabled in prod)
debug_toolbar = DebugToolbarExtension()

# Basic auth
login_manager = LoginManager()
login_manager.login_view = "main.login"
login_manager.login_message_category = "warning"

# Admin backoffice
admin = Admin()
basic_auth = BasicAuth()


@login_manager.user_loader
def load_user(userid):
    return User.query.get(userid)
