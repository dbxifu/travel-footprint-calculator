from flask import Blueprint, render_template, flash, request, redirect, url_for

from flaskr.extensions import cache
from flaskr.forms import LoginForm, EstimateForm
from flaskr.models import db, User, Estimation

from flaskr.core import generate_unique_id

main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')


@main.route("/estimate", methods=["GET", "POST"])
def estimate():
    form = EstimateForm()

    if form.validate_on_submit():

        # FIXME: do things here with the form

        id = generate_unique_id()

        # estimation = form.data

        estimation = Estimation()
        estimation.email = form.email.data
        estimation.first_name = form.first_name.data
        estimation.last_name = form.last_name.data
        estimation.status = 'pending'

        db.session.add(estimation)
        db.session.commit()

        flash("Estimation request submitted successfully.", "success")
        return redirect(url_for(".home"))
        # return render_template("estimate-debrief.html", form=form)

    return render_template("estimate.html", form=form)

