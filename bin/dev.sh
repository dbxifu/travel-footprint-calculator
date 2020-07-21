#!/usr/bin/env bash

# Run this and then visit http://localhost:5000

source venv/bin/activate
export FLASK_APP=flaskr
export FLASK_ENV=development
export FLASK_RUN_EXTRA_FILES="content.yml"

flask run
