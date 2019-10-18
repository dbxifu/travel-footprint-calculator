from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import enum

db = SQLAlchemy()


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


class StatusEnum(enum.Enum):
    pending = 'pending'
    success = 'success'
    failed = 'failed'


class Estimation(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.Unicode(1024))
    first_name = db.Column(db.Unicode(1024))  # Antoine
    last_name = db.Column(db.Unicode(1024))   # Goutenoir
    status = db.Column(db.Enum(StatusEnum))

    # destination_address = db.Column(db.Unicode(1024))

    # City, Country
    # One address per line
    origin_addresses = db.Column(db.Unicode())
    destination_addresses = db.Column(db.Unicode())
