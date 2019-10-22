from flaskr.core import generate_unique_id
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

# These are not the emission "models" in the scientific meaning of the word.
# They are the SQL Database Models.
# These are also named Entities, in other conventions (we're following flasks")
# If you're looking for the Emission Models (aka scaling laws),
# look in `flaskr/laws/`.


db = SQLAlchemy()


class StatusEnum(enum.Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


class Estimation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    public_id = db.Column(
        db.Unicode(),
        default=lambda: generate_unique_id(),
        unique=True
    )
    email = db.Column(db.Unicode(1024))
    first_name = db.Column(db.Unicode(1024))  # Antoine
    last_name = db.Column(db.Unicode(1024))   # Goutenoir
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.pending)

    # City, Country
    # One address per line
    origin_addresses = db.Column(db.Unicode())
    destination_addresses = db.Column(db.Unicode())

    compute_optimal_destination = db.Column(db.Boolean())

    output_pickle = db.Column(db.UnicodeText())
    warnings = db.Column(db.UnicodeText())
    errors = db.Column(db.UnicodeText())


# USERS #######################################################################

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, value):
        return check_password_hash(self.password, value)

    @property
    def is_authenticated(self):
        if isinstance(self, AnonymousUserMixin):
            return False
        else:
            return True

    def is_active(self):
        return True

    def is_anonymous(self):
        if isinstance(self, AnonymousUserMixin):
            return True
        else:
            return False

    def get_id(self):
        return self.id

    def __repr__(self):
        return '<User %r>' % self.username
