# Travel Carbon Footprint Calculator

- https://travel-footprint-calculator.apps.goutenoir.com  (private demo)
- http://travel-footprint-calculator.irap.omp.eu  (official)


## Overview

- Content is in `content.yml`.
- Configuration is in `content.yml`.
- HTML templates are in `flaskr/templates`.
- Estimation Models are in `flaskr/laws`.
- Controllers are in `flaskr/controllers`.


## Installation

Works on Python `2.7` up to version `1.2`.
Works on Python `3.7` from version `1.3`.


### Create a virtual environment

You don't _have to_.  But it's useful for development.

    virtualenv .venv

Then, source it to enable it.

    source .venv/bin/activate

### Install the python dependencies

You will need Cython.

    sudo apt install cython
    pip install -r requirements.txt

### Configure the secrets

    cp .env.dist .env
    nano .env

### Create an empty database

    python manage.py createdb

### Configure permissions

`var/runs` must be writeable by the application.
It is the file-based part of the database.


## Build CSS and JS (for prod)

    flask assets build


## Development

    source .venv/bin/activate
    source .env.flaskrun
    flask run

Then, visit http://localhost:5000



