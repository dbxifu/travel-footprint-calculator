from flask_wtf import Form
from wtforms import \
    StringField, \
    PasswordField, \
    TextAreaField, \
    BooleanField
from wtforms import validators

from .models import User


# ESTIMATION FORM #############################################################

class EstimateForm(Form):
    email = StringField(
        label=u"Email Address",
        description=u"Make sure you provide a valid address "
                    u"or you won't receive the results.",
        validators=[
            validators.DataRequired(),
            validators.Email(),
        ],
    )
    first_name = StringField(
        label=u"First Name",
        description=u"Also known as given name, eg. `Didier`.",
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
    )
    last_name = StringField(
        label=u"Last Name",
        description=u"Also known as family name, eg. `Barret`.",
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
    )
    institution = StringField(
        label=u"Institution / Enterprise",
        description=u"If any.",
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
    )
    comment = TextAreaField(
        label=u"Leave a comment",
        description=u"Any input is appreciated.  Everyone's a critic.",
        validators=[
            validators.Optional(),
            validators.Length(max=2048),
        ],
    )
    origin_addresses = TextAreaField(
        label=u"Origin Cities",
        description=u"One address per line, in the form `City, Country`. "
                    u"Make sure your addresses are correctly spelled.",
        validators=[
            validators.DataRequired(),
        ],
    )
    destination_addresses = TextAreaField(
        label=u"Destination Cities",
        description=u"One address per line, in the form `City, Country`. "
                    u"Make sure your addresses are correctly spelled.",
        validators=[
            validators.DataRequired(),
        ],
    )
    should_compute_optimal_destination = BooleanField(
        label=u"Compute the destination city "
              u"that will minimize emissions? <br>"
              u"(useful when setting up a meeting/conference)",
        description=u"",
        default=False,
        validators=[
            validators.Optional(),
        ],
    )

    def validate(self):
        check_validate = super(EstimateForm, self).validate()

        # Do our validators pass?
        if not check_validate:
            return False

        return True


# LOGIN FORM ##################################################################

class LoginForm(Form):
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
