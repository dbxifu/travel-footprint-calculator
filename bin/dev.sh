#!/usr/bin/env bash



source venv/bin/activate
export FLASK_APP=flaskr
export FLASK_ENV=development
export FLASK_RUN_EXTRA_FILES="content.yml"

flask run