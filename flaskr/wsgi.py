import os
import sys

PROJECT_ROOT_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

sys.path.append(PROJECT_ROOT_DIR)

# Only now can we import locals
# --> Not really true anymore since this file is in flaskr now.
from flaskr import create_app

app = create_app('flaskr.settings.ProductionConfig')

if __name__ == "__main__":
    # Pretty sure we're not using that during WSGI.
    app.run(host='0.0.0.0', port=80)
