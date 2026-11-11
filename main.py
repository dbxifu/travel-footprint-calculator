import os
import sys

PROJECT_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, PROJECT_ROOT_DIR)

# Only now can we import from local modules
from flaskr import create_app

#
# This file is only used in dev I believe.
# See flaskr/wsgi.py
#

app = create_app('flaskr.settings.ProductionConfig')

if __name__ == "__main__":
    app.run(host='0.0.0.0')
