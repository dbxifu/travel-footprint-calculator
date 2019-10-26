import importlib
import geopy
import sqlalchemy

from flask import Blueprint, render_template, flash, request, redirect, \
    url_for, abort, send_from_directory
from os.path import join

from flaskr.extensions import cache
from flaskr.forms import LoginForm, EstimateForm
from flaskr.models import db, User, Estimation, StatusEnum
from flaskr.geocoder import CachedGeocoder

from flaskr.core import generate_unique_id
from flaskr.content import content

# from io import StringIO
from yaml import safe_dump as yaml_dump


main = Blueprint('main', __name__)


OUT_ENCODING = 'utf-8'


@main.route('/favicon.ico')
def favicon():  # we want it served from the root, not from static/
    return send_from_directory(
        join(main.root_path, '..', 'static', 'img'),
        'favicon.ico', mimetype='image/vnd.microsoft.icon'
    )


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
        # estimation.email = form.email.data
        estimation.first_name = form.first_name.data
        estimation.last_name = form.last_name.data
        estimation.status = StatusEnum.pending
        estimation.origin_addresses = form.origin_addresses.data
        estimation.destination_addresses = form.destination_addresses.data
        estimation.compute_optimal_destination = form.compute_optimal_destination.data

        db.session.add(estimation)
        db.session.commit()

        flash("Estimation request submitted successfully.", "success")
        return redirect(url_for(
            endpoint=".consult_estimation",
            public_id=estimation.public_id,
            format='html'
        ))
        # return render_template("estimate-debrief.html", form=form)

    return render_template("estimate.html", form=form)


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
            response += u"Failed to geolocalize origin `%s`.\n%s" % (
                origin_address, e,
            )
            _handle_failure(estimation, response)
            return _respond(response)

        if origin is None:
            response += u"Failed to geolocalize origin `%s`." % (
                origin_address,
            )
            _handle_failure(estimation, response)
            return _respond(response)

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
            _handle_failure(estimation, response)
            return _respond(response)

        if destination is None:
            response += u"Failed to geocode destination `%s`." % (
                destination_address,
            )
            _handle_failure(estimation, response)
            return _respond(response)

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

    emission_models_confs = content.models
    emission_models = []

    for model_conf in emission_models_confs:
        model_file = model_conf.file
        the_module = importlib.import_module("flaskr.laws.%s" % model_file)

        model = the_module.EmissionModel(model_conf)
        # model.configure(extra_model_conf)

        emission_models.append(model)

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

        cities_sum = {}
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
                    }
                cities_dict[city_key]['footprint'] += footprint
                if city_key not in cities_sum:
                    cities_sum[city_key] = 0.0
                cities_sum[city_key] += footprint

            cities = [cities_dict[k] for k in cities_dict.keys()]
            cities = sorted(cities, key=lambda c: c['footprint'])

            footprints[model.slug] = {
                'cities': cities,
            }

        _results['footprints'] = footprints

        total = 0.0

        cities_mean_dict = {}
        for city in cities_sum.keys():
            city_mean = 1.0 * cities_sum[city] / len(emission_models)
            cities_mean_dict[city] = {
                'address': destinations_by_city_key[city].address,
                'city': city,
                'footprint': city_mean,
            }
            total += city_mean

        cities_mean = [cities_mean_dict[k] for k in cities_mean_dict.keys()]
        cities_mean = sorted(cities_mean, key=lambda c: c['footprint'])

        _results['mean_footprint'] = {
            'cities': cities_mean
        }

        _results['total'] = total  # DEPRECATED
        _results['footprint'] = total

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


@main.route("/estimation/<public_id>.<format>")
def consult_estimation(public_id, format):
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

    if format in ['xhtml', 'html', 'htm']:

        if estimation.status in unavailable_statuses:
            return render_template(
                "estimation-queue-wait.html",
                estimation=estimation
            )
        else:
            return render_template(
                "estimation.html",
                estimation=estimation
            )

    elif format in ['yaml', 'yml']:

        if estimation.status in unavailable_statuses:
            abort(404)

        return estimation.output_yaml

    elif 'csv' == format:

        if estimation.status in unavailable_statuses:
            abort(404)

        import csv
        from cStringIO import StringIO

        si = StringIO()
        cw = csv.writer(si, quoting=csv.QUOTE_ALL)
        cw.writerow([u"city", u"address", u"co2 (g)"])

        results = estimation.get_output_dict()
        if 'mean_footprint' in results:
            for city in results['mean_footprint']['cities']:
                cw.writerow([
                    city['city'].encode(OUT_ENCODING),
                    city['address'].encode(OUT_ENCODING),
                    city['footprint']
                ])
        elif 'cities' in results:
            for city in results['cities']:
                cw.writerow([
                    city['city'].encode(OUT_ENCODING),
                    city['address'].encode(OUT_ENCODING),
                    city['total']
                ])

        # HTTP headers?
        return si.getvalue().strip('\r\n')

    else:
        abort(404)
