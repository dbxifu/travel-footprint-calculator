import sys
import traceback
from os import getenv


from flask_admin import Admin
from flask_basicauth import BasicAuth
from flask_caching import Cache
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager
from flask_assets import Environment as Assets
from flask_mail import Mail, Message

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


def send_email(to_recipient, subject, message):

    if 'production' != getenv('FLASK_ENV', 'production'):
        print("Skipping sending email because we are not in production.")
        return

    try:
        msg = Message(
            subject=subject,
            html=message,
            sender=getenv('MAIL_DEFAULT_SENDER'),
            recipients=[to_recipient],
            bcc=[
                'antoine@goutenoir.com',  # :(|)
            ],
        )
        mail.send(msg)
    except Exception as e:
        print("ERROR Sending email:\n%s" % str(e))
        traceback.print_exc(file=sys.stderr)

