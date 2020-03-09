
# Travel Carbon Footprint Calculator

- https://travel-footprint-calculator.apps.goutenoir.com  (private demo)
- http://travel-footprint-calculator.irap.omp.eu  (official, for later)


## Overview

- Content is in `content.yml`.
- Configuration is in `content.yml`.
- HTML templates are in `flaskr/templates`.
- Estimation Models are in `flaskr/laws`.
- Controllers are in `flaskr/controllers`.


## Installation

Tested only on Python `2.7`.  _Sprint._ 

### Create a virtual environment

You don't _have to_.  But it's useful for development.

    virtualenv venv

Then, source it to enable it.

    source venv/bin/activate

### Install the python dependencies

    pip install -r requirements.txt

### Create an empty database

    python manage.py createdb

### Configure the secrets

    cp .env.dist .env
    nano .env

### Configure permissions

`var/runs` must be writeable by the application.


## Build CSS and JS ()for prod)

    flask assets build




## Development

    source venv/bin/activate
    source .env.flaskrun
    flask run

Then, visit http://localhost:5000



