from flask_wtf import FlaskForm
from werkzeug.datastructures import FileStorage
from wtforms import \
    StringField, \
    PasswordField, \
    TextAreaField, \
    SelectField, \
    BooleanField, \
    FileField
from wtforms import validators

from .content import content_dict as content
from .core import models
from .extensions import captcha
from .models import User

form_content = content['estimate']['form']
train_values = form_content['use_train_below_km']['values']
IS_HUMAN = 'carbon'


# ESTIMATION FORM #############################################################

class EstimateForm(FlaskForm):

    # email = StringField(
    #     label=form_content['email']['label'],
    #     description=form_content['email']['description'],
    #     validators=[
    #         validators.DataRequired(),
    #         validators.Email(),
    #     ],
    # )

    run_name = StringField(
        label=form_content['run_name']['label'],
        description=form_content['run_name']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=128),
        ],
        render_kw={
            "placeholder": form_content['run_name']['placeholder'],
        },
    )
    first_name = StringField(
        label=form_content['first_name']['label'],
        description=form_content['first_name']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=128),
        ],
        render_kw={
            "placeholder": form_content['first_name']['placeholder'],
            "autocomplete": "given-name",
        },
    )
    last_name = StringField(
        label=form_content['last_name']['label'],
        description=form_content['last_name']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=128),
        ],
        render_kw={
            "placeholder": form_content['last_name']['placeholder'],
            "autocomplete": "family-name",
        },
    )
    institution = StringField(
        label=form_content['institution']['label'],
        description=form_content['institution']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=128),
        ],
    )
    use_train_below_km = SelectField(
        label=form_content['use_train_below_km']['label'],
        description=form_content['use_train_below_km']['description'],
        default=500,
        choices=[(v['value'], v['label']) for v in train_values],
        coerce=int,
    )
    comment = TextAreaField(
        label=form_content['comment']['label'],
        description=form_content['comment']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=4096),
        ],
    )
    origin_addresses = TextAreaField(
        label=form_content['origin_addresses']['label'],
        description=form_content['origin_addresses']['description'],
        validators=[
            # validators.DataRequired(),
        ],
        render_kw={
            "placeholder": form_content['origin_addresses']['placeholder'],
        },
    )
    destination_addresses = TextAreaField(
        label=form_content['destination_addresses']['label'],
        description=form_content['destination_addresses']['description'],
        validators=[
            # validators.DataRequired(),
        ],
        render_kw={
            "placeholder": form_content['destination_addresses']['placeholder'],
        },
    )
    origin_addresses_file = FileField(
        label=form_content['origin_addresses_file']['label'],
        description=form_content['origin_addresses_file']['description'],
        validators=[
            # We disabled validators because they bug with multiple FileFields
            # validators.Optional(),
            # FileAllowed(
            #     ['csv', 'xls', 'xlsx'],
            #     form_content['origin_addresses_file']['error']
            # )
        ],
    )
    destination_addresses_file = FileField(
        label=form_content['destination_addresses_file']['label'],
        description=form_content['destination_addresses_file']['description'],
        validators=[
            # We disabled validators because they bug with multiple FileFields
            # validators.Optional(),
            # FileAllowed(
            #     ['csv', 'xls', 'xlsx'],
            #     form_content['destination_addresses_file']['error']
            # )
        ],
    )
    captcha = StringField(
        label=form_content['captcha']['label'],
        description=form_content['captcha']['description'],
        validators=[
            validators.InputRequired(),
            validators.Length(max=16),
        ],
    )

    upload_set = ['csv', 'xls', 'xlsx']

    # compute_optimal_destination = BooleanField(
    #     label=form_content['compute_optimal_destination']['label'],
    #     description=form_content['compute_optimal_destination']['description'],
    #     default=False,
    #     validators=[
    #         validators.Optional(),
    #     ],
    # )
    # use_atmosfair_rfi = BooleanField(
    #     label=form_content['use_atmosfair_rfi']['label'],
    #     description=form_content['use_atmosfair_rfi']['description'],
    #     default=False,
    #     validators=[
    #         validators.Optional(),
    #     ],
    # )

    def validate(self):
        check_validate = super(EstimateForm, self).validate()

        # Do our validators pass?
        if not check_validate:
            return False

        if self.captcha.data != IS_HUMAN:
            if not captcha.validate():
                self.captcha.errors.append(
                    "Captcha do not match.  Try again."
                )
                return False

        # Origins must be set either by field or file
        if (
            (not self.origin_addresses.data)
            and
            (not self.origin_addresses_file.data)
        ):
            self.origin_addresses.errors.append(
                "You need to provide either a list of cities or a file."
            )
            return False

        # Destinations must be set either by field or file
        if (
            (not self.destination_addresses.data)
            and
            (not self.destination_addresses_file.data)
        ):
            self.destination_addresses.errors.append(
                "You need to provide either a list of cities or a file."
            )
            return False

        # At least one model should be used
        uses_at_least_one_model = False
        for model in models:
            use_model = getattr(self, 'use_model_%s' % model.slug)
            # print("Model data", model.slug, use_model.data)
            if use_model.data:
                uses_at_least_one_model = True

        if not uses_at_least_one_model:
            last_model = getattr(self, 'use_model_%s' % models[-1].slug)
            last_model.errors.append(
                "Please select at least one plane model, "
                "<em>even for train-only estimations.</em>"
            )
            return False

        # Check uploaded files' extensions, if any
        # We have to do this "by hand" because of a bug in flask wtf
        if isinstance(self.origin_addresses_file.data, FileStorage):
            fn = self.origin_addresses_file.data.filename.lower()
            if fn and not any(fn.endswith('.' + x) for x in self.upload_set):
                self.origin_addresses_file.errors.append(
                    form_content['origin_addresses_file']['error']
                )
                return False
        if isinstance(self.destination_addresses_file.data, FileStorage):
            fn = self.destination_addresses_file.data.filename.lower()
            if fn and not any(fn.endswith('.' + x) for x in self.upload_set):
                self.destination_addresses_file.errors.append(
                    form_content['destination_addresses_file']['error']
                )
                return False

        return True


# Add the models' checkboxes to the above Form
for model in models:
    setattr(  # setattr() takes no keyword arguments -.-
        EstimateForm,
        'use_model_%s' % model.slug,
        BooleanField(
            label=model.name,
            # description=model.short_description,
            default=model.selected,
            validators=[
                validators.Optional(),
            ],
        )
    )


# LOGIN FORM ##################################################################

class LoginForm(FlaskForm):
    username = StringField(u'Username', validators=[validators.required()])
    password = PasswordField(u'Password', validators=[validators.optional()])

    def validate(self):
        check_validate = super(LoginForm, self).validate()

        # Do our validators pass?
        if not check_validate:
            return False

        # Does the user even exist?
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.username.errors.append('Invalid username or password')
            return False

        # Do the passwords match?
        if not user.check_password(self.password.data):
            self.username.errors.append('Invalid username or password')
            return False

        return True
