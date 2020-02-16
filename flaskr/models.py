import enum
import shelve
from os.path import join, isfile
from flask_admin.contrib.sqla import ModelView

from flaskr.core import generate_unique_id, models
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, AnonymousUserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from yaml import safe_load as yaml_load

from content import get_path


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
    run_name = db.Column(db.Unicode(1024))   # JPGU 2020

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
    output_yaml = db.Column(db.UnicodeText())  # deprecated, use shelve file
    informations = db.Column(db.UnicodeText())
    warnings = db.Column(db.UnicodeText())
    errors = db.Column(db.UnicodeText())

    @property
    def link(self):
        return u"https://travel-footprint-calculator.irap.omp.eu/estimation/%s.html" \
               % self.public_id

    @property
    def author_name(self):
        s = u""
        if self.first_name:
            s += self.first_name
        if self.last_name:
            s += (u" " if s else u"") + self.last_name
        if self.institution:
            s += (u" " if s else u"") + self.institution
        return s

    @property
    def origins_count(self):
        return self.origin_addresses.strip().count("\n") + 1

    @property
    def destinations_count(self):
        return self.destination_addresses.strip().count("\n") + 1

    @property
    def errors_tail(self):
        return self.get_tail(self.errors)

    @property
    def warnings_tail(self):
        return self.get_tail(self.warnings)

    def get_tail(self, of_string, of_length=140):
        if not of_string:
            return ""
        return u"...%s" % of_string[-(min(of_length, len(of_string))):]

    def has_failed(self):
        return self.status == StatusEnum.failure

    def get_display_name(self):
        if self.run_name:
            return self.run_name
        return self.public_id

    def get_output_filename(self):
        runs_dir = get_path("var/runs")
        return join(runs_dir, self.public_id)

    def set_output_dict(self, output):
        # with shelve.open(filename=self.get_output_filename(), protocol=2) as shelf:
        #     shelf['output'] = output
        shelf = shelve.open(filename=self.get_output_filename(), protocol=2)
        shelf['output'] = output
        shelf.close()

    _output_dict = None

    def get_output_dict(self):
        if self._output_dict is None:
            if self.output_yaml is None:
                output_filename = self.get_output_filename()
                if isfile(output_filename):
                    # with shelve.open(filename=output_filename,
                    #                  protocol=2) as shelf:
                    #     self._output_dict = shelf['output']
                    shelf = shelve.open(filename=output_filename, protocol=2)
                    self._output_dict = shelf['output']
                    # self._output_dict = copy(shelf['output'])
                    shelf.close()
                else:
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


# BACKOFFICE CONFIGURATION ####################################################

class EstimationView(ModelView):
    # Show only name and email columns in list view
    column_list = (
        'public_id',
        'link',
        'run_name',
        'status',
        'author_name',
        'models_slugs',
        'scenario',
        'origins_count',
        'destinations_count',
        'warnings_tail',
        'errors_tail',
    )

    # Enable search functionality - it will search for terms in
    # name and email fields
    # column_searchable_list = ('name', 'email')

    column_filters = ('first_name', 'last_name', 'status')


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
