from flask_wtf import Form
from wtforms import \
    StringField, \
    PasswordField, \
    TextAreaField, \
    BooleanField
from wtforms import validators

from .models import User
from .content import content_dict as content

form_content = content['estimate']['form']


# ESTIMATION FORM #############################################################

class EstimateForm(Form):
    # email = StringField(
    #     label=form_content['email']['label'],
    #     description=form_content['email']['description'],
    #     validators=[
    #         validators.DataRequired(),
    #         validators.Email(),
    #     ],
    # )
    first_name = StringField(
        label=form_content['first_name']['label'],
        description=form_content['first_name']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
        render_kw={
            "placeholder": form_content['first_name']['placeholder']
        },
    )
    last_name = StringField(
        label=form_content['last_name']['label'],
        description=form_content['last_name']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
        render_kw={
            "placeholder": form_content['last_name']['placeholder']
        },
    )
    institution = StringField(
        label=form_content['institution']['label'],
        description=form_content['institution']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=1024),
        ],
    )
    comment = TextAreaField(
        label=form_content['comment']['label'],
        description=form_content['comment']['description'],
        validators=[
            validators.Optional(),
            validators.Length(max=2048),
        ],
    )
    origin_addresses = TextAreaField(
        label=form_content['origin_addresses']['label'],
        description=form_content['origin_addresses']['description'],
        validators=[
            validators.DataRequired(),
        ],
        render_kw={
            "placeholder": form_content['origin_addresses']['placeholder']
        },
    )
    destination_addresses = TextAreaField(
        label=form_content['destination_addresses']['label'],
        description=form_content['destination_addresses']['description'],
        validators=[
            validators.DataRequired(),
        ],
        render_kw={
            "placeholder": form_content['destination_addresses']['placeholder']
        },
    )
    compute_optimal_destination = BooleanField(
        label=form_content['compute_optimal_destination']['label'],
        description=form_content['compute_optimal_destination']['description'],
        default=False,
        validators=[
            validators.Optional(),
        ],
    )
    use_atmosfair_rfi = BooleanField(
        label=form_content['use_atmosfair_rfi']['label'],
        description=form_content['use_atmosfair_rfi']['description'],
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
