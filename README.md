
# Travel Carbon Footprint Calculator

## Overview

- Content is in `content.yml`.
- Configuration is in `content.yml`.
- HTML templates are in `flaskr/templates`.
- Estimation Models are in `flaskr/laws`.
- Controllers are in `flaskr/controllers`.


## Installation

Tested only on Python `2.7`.  _Sprint._ 

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py createdb


## Development

    source venv/bin/activate
    export FLASK_APP=flaskr
    export FLASK_ENV=development
    export FLASK_RUN_EXTRA_FILES="content.yml"
    flask run

Then, visit http://localhost:5000

> We're trying to remove the need for the `export` statements, but…


