from flask_admin.contrib.sqla import ModelView

from flaskr.core import generate_unique_id, models
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from yaml import safe_load as yaml_load
import enum

# These are not the emission "models" in the scientific meaning of the word.
# They are the SQL Database Models.
# These are also named Entities, in other conventions (we're following flasks")
# If you're looking for the Emission Models (aka scaling laws),
# look in `flaskr/laws/`.


db = SQLAlchemy()


class StatusEnum(enum.Enum):
    pending = 'pending'
    working = 'working'
    success = 'success'
    failure = 'failure'


class ScenarioEnum(enum.Enum):
    one_to_one = 'one_to_one'
    many_to_one = 'many_to_one'
    one_to_many = 'one_to_many'
    many_to_many = 'many_to_many'


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
    institution = db.Column(db.Unicode(1024))   # IRAP
    status = db.Column(db.Enum(StatusEnum), default=StatusEnum.pending)

    # City, Country
    # One address per line
    origin_addresses = db.Column(db.UnicodeText())
    destination_addresses = db.Column(db.UnicodeText())

    # For (single, not round) trips below this distance, use the train
    use_train_below_km = db.Column(db.Integer())

    # One slug per line (or blank char?)
    models_slugs = db.Column(db.UnicodeText())

    # Deprecated, we detect this scenario from the amount of locations.
    compute_optimal_destination = db.Column(db.Boolean())

    # Outputs
    scenario = db.Column(db.Enum(ScenarioEnum), default=ScenarioEnum.many_to_many)
    output_yaml = db.Column(db.UnicodeText())
    warnings = db.Column(db.UnicodeText())
    errors = db.Column(db.UnicodeText())

    def has_failed(self):
        return self.status == StatusEnum.failure

    _output_dict = None

    def get_output_dict(self):
        if self._output_dict is None:
            if self._output_yaml is None:
                self._output_dict = None
            else:
                self._output_dict = yaml_load(self.output_yaml)
            return self._output_dict

    def is_one_to_one(self):
        return self.scenario == ScenarioEnum.one_to_one

    def is_one_to_many(self):
        return self.scenario == ScenarioEnum.one_to_many

    def is_many_to_one(self):
        return self.scenario == ScenarioEnum.many_to_one

    def is_many_to_many(self):
        return self.scenario == ScenarioEnum.many_to_many

    _models = None

    def get_models(self):
        if self._models is None:
            mdl_slugs = self.models_slugs.split("\n")
            self._models = [m for m in models if m.slug in mdl_slugs]
        return self._models


class EstimationView(ModelView):
    # Show only name and email columns in list view
    column_list = (
        'public_id',
        'status',
        'first_name',
        'last_name',
        'models_slugs',
        'scenario',
        'origin_addresses',
        'destination_addresses',
        'warnings',
        'errors',
    )

    # Enable search functionality - it will search for terms in
    # name and email fields
    # column_searchable_list = ('name', 'email')

    column_filters = ('first_name', 'last_name')


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
