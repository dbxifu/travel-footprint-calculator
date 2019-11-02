import geopy
import sqlalchemy

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, abort, send_from_directory, Response
from os.path import join

from flaskr.extensions import cache, basic_auth
from flaskr.forms import LoginForm, EstimateForm
from flaskr.models import db, User, Estimation, StatusEnum
from flaskr.geocoder import CachedGeocoder

from flaskr.core import generate_unique_id, get_emission_models
from flaskr.content import content

from yaml import safe_dump as yaml_dump

import csv
# from io import StringIO
from cStringIO import StringIO

main = Blueprint('main', __name__)


OUT_ENCODING = 'utf-8'


# -----------------------------------------------------------------------------
# refactor this outta here, like in core?


# -----------------------------------------------------------------------------


@main.route('/favicon.ico')
@cache.cached(timeout=10000)
def favicon():  # we want it served from the root, not from static/
    return send_from_directory(
        join(main.root_path, '..', 'static', 'img'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


@main.route('/')
@cache.cached(timeout=1000)
def home():
    models = get_emission_models()
    return render_template(
        'home.html',
        models=models,
        colors=[model.color for model in models],
    )


@main.route("/estimate", methods=["GET", "POST"])
def estimate():
    models = get_emission_models()
    form = EstimateForm()

    if form.validate_on_submit():

        id = generate_unique_id()

        estimation = Estimation()
        # estimation.email = form.email.data
        estimation.first_name = form.first_name.data
        estimation.last_name = form.last_name.data
        estimation.institution = form.institution.data
        estimation.status = StatusEnum.pending
        estimation.origin_addresses = form.origin_addresses.data
        estimation.destination_addresses = form.destination_addresses.data
        # estimation.compute_optimal_destination = form.compute_optimal_destination.data
        models_slugs = []
        for model in models:
            if getattr(form, 'use_model_%s' % model.slug).data:
                models_slugs.append(model.slug)
        estimation.models_slugs = "\n".join(models_slugs)

        db.session.add(estimation)
        db.session.commit()

        flash("Estimation request submitted successfully.", "success")
        return redirect(url_for(
            endpoint=".consult_estimation",
            public_id=estimation.public_id,
            extension='html'
        ))
        # return render_template("estimate-debrief.html", form=form)

    return render_template("estimate.html", form=form, models=models)


@main.route("/invalidate")
def invalidate():
    stuck_estimations = Estimation.query \
        .filter_by(status=StatusEnum.working) \
        .all()

    for estimation in stuck_estimations:
        estimation.status = StatusEnum.failure
        estimation.errors = "Invalidated. Try again."
        db.session.commit()

    return ""


@main.route("/compute")
def compute():  # process the queue of estimation requests

    def _respond(_msg):
        return "<pre>%s</pre>" % _msg

    def _handle_failure(_estimation, _failure_message):
        _estimation.status = StatusEnum.failure
        _estimation.errors = _failure_message
        db.session.commit()

    def _handle_warning(_estimation, _warning_message):
        _estimation.warnings = _warning_message
        db.session.commit()

    response = ""

    count_working = Estimation.query \
        .filter_by(status=StatusEnum.working) \
        .count()

    if 0 < count_working:
        return _respond("Already working on estimation.")

    try:
        estimation = Estimation.query \
            .filter_by(status=StatusEnum.pending) \
            .order_by(Estimation.id.asc()) \
            .first()
    except sqlalchemy.orm.exc.NoResultFound:
        return _respond("No estimation in the queue.")
    except Exception as e:
        return _respond("Database error: %s" % (e,))

    if not estimation:
        return _respond("No estimation in the queue.")

    estimation.status = StatusEnum.working
    db.session.commit()

    response += u"Processing estimation `%s`...\n" % (
        estimation.public_id
    )

    geocoder = CachedGeocoder()

    # GEOCODE ORIGINS #########################################################

    origins_addresses = estimation.origin_addresses.strip().split("\n")
    origins = []

    for i in range(len(origins_addresses)):

        origin_address = origins_addresses[i].strip()

        try:
            origin = geocoder.geocode(origin_address.encode('utf-8'))
        except geopy.exc.GeopyError as e:
            response += u"Failed to geocode origin `%s`.\n%s" % (
                origin_address, e,
            )
            _handle_warning(estimation, response)
            continue

        if origin is None:
            response += u"Failed to geocode origin `%s`." % (
                origin_address,
            )
            _handle_warning(estimation, response)
            continue

        origins.append(origin)

        response += u"Origin: %s == %s (%f, %f)\n" % (
            origin_address, origin.address,
            origin.latitude, origin.longitude,
        )

    # GEOCODE DESTINATIONS ####################################################

    destinations_addresses = estimation.destination_addresses.strip().split("\n")
    destinations = []

    for i in range(len(destinations_addresses)):

        destination_address = destinations_addresses[i].strip()

        try:
            destination = geocoder.geocode(destination_address.encode('utf-8'))
        except geopy.exc.GeopyError as e:
            response += u"Failed to geocode destination `%s`.\n%s" % (
                destination_address, e,
            )
            _handle_warning(estimation, response)
            continue

        if destination is None:
            response += u"Failed to geocode destination `%s`." % (
                destination_address,
            )
            _handle_warning(estimation, response)
            continue

        # print(repr(destination.raw))

        destinations.append(destination)

        response += u"Destination: %s == %s (%f, %f)\n" % (
            destination_address, destination.address,
            destination.latitude, destination.longitude,
        )

    # GTFO IF NO ORIGINS OR NO DESTINATIONS ###################################

    if 0 == len(origins):
        response += u"Failed to geocode all the origin(s)."
        _handle_failure(estimation, response)
        return _respond(response)
    if 0 == len(destinations):
        response += u"Failed to geocode all the destination(s)."
        _handle_failure(estimation, response)
        return _respond(response)

    # GRAB AND CONFIGURE THE EMISSION MODELS ##################################

    mdl_slugs = estimation.models_slugs.split("\n")
    emission_models = [m for m in get_emission_models() if m.slug in mdl_slugs]
    # print(emission_models)

    # PREPARE RESULT DICTIONARY THAT WILL BE STORED ###########################

    results = {}

    # UTILITY PRIVATE FUNCTION(S) #############################################

    def get_city_key(_location):

        return _location.address.split(',')[0]

        # _city_key = _location.address
        # # if 'address100' in _location.raw['address']:
        # #     _city_key = _location.raw['address']['address100']
        # if 'city' in _location.raw['address']:
        #     _city_key = _location.raw['address']['city']
        # elif 'state' in _location.raw['address']:
        #     _city_key = _location.raw['address']['state']
        # return _city_key

    def compute_one_to_many(
            _origin,
            _destinations,
            use_train_below=0.0
    ):
        _results = {}
        footprints = {}

        destinations_by_city_key = {}

        cities_sum_foot = {}
        cities_sum_dist = {}
        for model in emission_models:
            cities_dict = {}
            for _destination in _destinations:
                footprint = model.compute_travel_footprint(
                    origin_latitude=_origin.latitude,
                    origin_longitude=_origin.longitude,
                    destination_latitude=_destination.latitude,
                    destination_longitude=_destination.longitude,
                )

                city_key = get_city_key(_destination)

                destinations_by_city_key[city_key] = _destination

                if city_key not in cities_dict:
                    cities_dict[city_key] = {
                        'city': city_key,
                        'address': _destination.address,
                        'footprint': 0.0,
                        'distance': 0.0,
                    }
                cities_dict[city_key]['footprint'] += footprint['co2eq_kg']
                cities_dict[city_key]['distance'] += footprint['distance']
                if city_key not in cities_sum_foot:
                    cities_sum_foot[city_key] = 0.0
                cities_sum_foot[city_key] += footprint['co2eq_kg']
                if city_key not in cities_sum_dist:
                    cities_sum_dist[city_key] = 0.0
                cities_sum_dist[city_key] += footprint['distance']

            cities = [cities_dict[k] for k in cities_dict.keys()]
            cities = sorted(cities, key=lambda c: c['footprint'])

            footprints[model.slug] = {
                'cities': cities,
            }

        _results['footprints'] = footprints

        total_foot = 0.0
        total_dist = 0.0

        cities_mean_dict = {}
        for city in cities_sum_foot.keys():
            city_mean_foot = 1.0 * cities_sum_foot[city] / len(emission_models)
            city_mean_dist = 1.0 * cities_sum_dist[city] / len(emission_models)
            cities_mean_dict[city] = {
                'address': destinations_by_city_key[city].address,
                'city': city,
                'footprint': city_mean_foot,
                'distance': city_mean_dist,
            }
            total_foot += city_mean_foot
            total_dist += city_mean_dist

        cities_mean = [cities_mean_dict[k] for k in cities_mean_dict.keys()]
        cities_mean = sorted(cities_mean, key=lambda c: c['footprint'])

        _results['mean_footprint'] = {  # DEPRECATED?
            'cities': cities_mean
        }
        _results['cities'] = cities_mean

        _results['total'] = total_foot  # DEPRECATED
        _results['footprint'] = total_foot

        _results['distance'] = total_dist

        return _results

    # SCENARIO A : One Origin, At Least One Destination #######################
    #
    # In this scenario, we compute the sum of each of the travels' footprint,
    # for each of the Emission Models, and present a mean of all Models.
    #
    if 1 == len(origins):
        results = compute_one_to_many(
            _origin=origins[0],
            _destinations=destinations,
            use_train_below=0,
        )

    # SCENARIO B : At Least One Origin, One Destination #######################
    #
    # Same as A for now.
    #
    elif 1 == len(destinations):
        results = compute_one_to_many(
            _origin=destinations[0],
            _destinations=origins,
            use_train_below=0,
        )

    # SCENARIO C : At Least One Origin, At Least One Destination ##############
    #
    # Run Scenario A for each Destination, and expose optimum Destination.
    #
    else:
        unique_city_keys = []
        result_cities = []
        for destination in destinations:
            city_key = get_city_key(destination)

            if city_key in unique_city_keys:
                continue
            else:
                unique_city_keys.append(city_key)

            city_results = compute_one_to_many(
                _origin=destination,
                _destinations=origins,
                use_train_below=0,
            )
            city_results['city'] = city_key
            city_results['address'] = destination.address
            result_cities.append(city_results)

        result_cities = sorted(result_cities, key=lambda c: int(c['total']))
        results = {
            'cities': result_cities,
        }

    # WRITE RESULTS INTO THE DATABASE #########################################

    estimation.status = StatusEnum.success
    estimation.output_yaml = yaml_dump(results)
    db.session.commit()

    # FINALLY, RESPOND ########################################################

    response += yaml_dump(results) + "\n"

    return _respond(response)


@main.route("/estimation/<public_id>.<extension>")
def consult_estimation(public_id, extension):
    try:
        estimation = Estimation.query \
            .filter_by(public_id=public_id) \
            .one()
    except sqlalchemy.orm.exc.NoResultFound:
        return abort(404)
    except Exception as e:
        # TODO: log
        return abort(500)

    # allowed_formats = ['html']
    # if format not in allowed_formats:
    #     abort(404)

    unavailable_statuses = [StatusEnum.pending, StatusEnum.working]

    if extension in ['xhtml', 'html', 'htm']:

        if estimation.status in unavailable_statuses:
            return render_template(
                "estimation-queue-wait.html",
                estimation=estimation
            )
        else:
            return render_template(
                "estimation.html",
                estimation=estimation,
                estimation_output=estimation.get_output_dict(),
            )

    elif extension in ['yaml', 'yml']:

        if estimation.status in unavailable_statuses:
            abort(404)

        return estimation.output_yaml

    elif 'csv' == extension:

        if estimation.status in unavailable_statuses:
            abort(404)

        si = StringIO()
        cw = csv.writer(si, quoting=csv.QUOTE_ALL)
        cw.writerow([u"city", u"address", u"co2 (kg)", u"distance (km)"])

        results = estimation.get_output_dict()
        for city in results['cities']:
            cw.writerow([
                city['city'].encode(OUT_ENCODING),
                city['address'].encode(OUT_ENCODING),
                round(city['footprint'], 3),
                round(city['distance'], 3),
            ])

        # return si.getvalue().strip('\r\n')
        return Response(
            response=si.getvalue().strip('\r\n'),
            headers={
                'Content-type': 'text/csv',
                'Content-disposition': "attachment; filename=%s.csv"%public_id,
            },
        )

    else:
        abort(404)


@main.route("/scaling_laws.csv")
def get_scaling_laws_csv():
    distances = content.laws_plot.distances
    models = get_emission_models()

    si = StringIO()
    cw = csv.writer(si, quoting=csv.QUOTE_ALL)

    header = ['distance'] + [model.slug for model in models]
    cw.writerow(header)

    for distance in distances:
        row = [distance]
        for model in models:
            row.append(model.compute_airplane_distance_footprint(distance))
        cw.writerow(row)

    return Response(
        response=si.getvalue().strip('\r\n'),
        headers={
            'Content-type': 'text/csv',
            'Content-disposition': 'attachment; filename=scaling_laws.csv',
        },
    )


@main.route("/test")
@basic_auth.required
def dev_test():
    import os

    return os.getenv('ADMIN_USERNAME')
