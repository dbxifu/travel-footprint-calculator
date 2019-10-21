from flask import Blueprint, render_template, flash, request, redirect, url_for

from flaskr.extensions import cache
from flaskr.forms import LoginForm, EstimateForm
from flaskr.models import db, User, Estimation, StatusEnum
from flaskr.geocoder import CachedGeocoder

from flaskr.core import generate_unique_id

import sqlalchemy
import geopy

main = Blueprint('main', __name__)


@main.route('/')
@cache.cached(timeout=1000)
def home():
    return render_template('index.html')


@main.route("/estimate", methods=["GET", "POST"])
def estimate():
    form = EstimateForm()

    if form.validate_on_submit():

        id = generate_unique_id()

        estimation = Estimation()
        estimation.email = form.email.data
        estimation.first_name = form.first_name.data
        estimation.last_name = form.last_name.data
        estimation.status = StatusEnum.pending
        estimation.origin_addresses = form.origin_addresses.data
        estimation.destination_addresses = form.destination_addresses.data
        estimation.compute_optimal_destination = form.compute_optimal_destination.data

        db.session.add(estimation)
        db.session.commit()

        flash("Estimation request submitted successfully.", "success")
        return redirect(url_for(".home"))
        # return render_template("estimate-debrief.html", form=form)

    return render_template("estimate.html", form=form)


@main.route("/compute")
def compute():

    def _respond(_msg):
        return "<pre>%s</pre>" % _msg

    def _handle_failure(_estimation, _failure_message):
        _estimation.status = StatusEnum.failed
        db.session.commit()

    response = ""

    try:
        estimation = Estimation.query \
            .filter_by(status=StatusEnum.pending) \
            .order_by(Estimation.id.desc()) \
            .one()
    except sqlalchemy.orm.exc.NoResultFound:
        return _respond("No estimation in the queue.")

    response += u"Processing estimation `%s` of `%s`...\n" % (estimation.id, estimation.email)

    geocoder = CachedGeocoder()

    destinations_addresses = estimation.destination_addresses.split("\n")
    destinations = []

    for i in range(len(destinations_addresses)):

        destination_address = str(destinations_addresses[i])

        try:
            destination = geocoder.geocode(destination_address)
        except geopy.exc.GeopyError as e:
            response += u"Failed to geolocalize destination `%s`.\n%s" % (
                destination_address, e,
            )
            _handle_failure(estimation, response)
            return _respond(response)

        if destination is None:
            response += u"Failed to geolocalize destination `%s`." % (
                destination_address,
            )
            _handle_failure(estimation, response)
            return _respond(response)

        destinations.append(destination)

        response += u"Destination: %s == %s (%f, %f)\n" % (
            destination_address, destination.address,
            destination.latitude, destination.longitude,
        )



    return _respond(response)
